from pandas import read_excel
from pandas import DataFrame
from gspread import authorize
import config_file
import db_manipulation as db
from oauth2client.service_account import ServiceAccountCredentials


class TemperatureData:
    def __init__(self, *arrays_tuples):
        self.central_array_average = None
        self.central_array_delta = None
        self.arrays_tuples = arrays_tuples
        self.data_list = []
        self.file_name = None
        self.__arrays_quantity = int(config_file.arrays_quantity)
        self.__central_array__id = int(config_file.central_array__id)

        if config_file.in_document_columns is not None:
            self.__in_document_columns = config_file.in_document_columns
        else:
            in_document_columns = []
            counter = 0
            while counter < config_file.arrays_quantity:
                counter = counter + 1
                in_document_columns.append(str(100 + counter) + " (C)")
            config_file.in_document_columns = in_document_columns
            self.__in_document_columns = in_document_columns

    @staticmethod
    def convert_num_for_tab(num, symbols=6):
        num = "%.2f" % round(num, 2)
        num = str(num)
        if len(num) > symbols:
            num = "<9999.9"
        elif len(num) < symbols:
            num = (" " * (symbols - len(num))) + num
        else:
            pass
        return num

    @staticmethod
    def find_max_delta(average_int, minimum_int, maximum_int):
        if abs(average_int - minimum_int) > abs(average_int - maximum_int):
            answer = abs(average_int - minimum_int)
        else:
            answer = abs(average_int - maximum_int)
        return answer

    @staticmethod
    def average(nums_list):
        summ = 0
        for i in nums_list:
            summ = summ + i
        answer = summ / len(nums_list)
        return answer

    def calculate(self):
        central_id = self.__central_array__id
        arrays_tuples = self.arrays_tuples
        self.central_array_average = self.average(arrays_tuples[central_id])
        self.central_array_delta = self.find_max_delta(
            self.central_array_average,
            min(arrays_tuples[central_id]),
            max(arrays_tuples[central_id]),
        )

        counter = 0
        for i in arrays_tuples:
            name = self.__in_document_columns[counter]
            counter = +1
            maximum = max(i)
            minimum = min(i)
            median = (minimum + maximum) / 2
            average_value = self.average(i)
            delta = self.find_max_delta(self.central_array_average, minimum, maximum)
            array_data = {
                "data": i,
                "name": name,
                "max": maximum,
                "min": minimum,
                "median": median,
                "average": average_value,
                "delta": delta,
            }
            self.data_list.append(array_data)

    def set_data_from_xlsx(self, file_name, skiprows=config_file.skiprows):
        self.file_name = file_name
        data = read_excel(file_name, skiprows=skiprows)
        return_data = []
        for i in self.__in_document_columns:
            data_frame = DataFrame(data, columns=[i])
            data_array = data_frame.iloc[:, 0]
            data_tuple = tuple(data_array.array)
            return_data.append(data_tuple)
        self.arrays_tuples = return_data

    def set_data_from_google_doc_link(self, url):
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            config_file.API_key, scope
        )
        client = authorize(credentials)
        spreadsheet_key = url.split("/")[5]
        spreadsheet = client.open_by_key(spreadsheet_key)
        worksheet = spreadsheet.worksheets()[0]
        skiprows = config_file.skiprows

        data = worksheet.get_all_values()
        df = DataFrame(data[skiprows:], columns=data[skiprows])

        return_data = []
        for i in self.__in_document_columns:
            data_frame = DataFrame(df, columns=[i])
            data_array = data_frame.iloc[1:, 0]
            data_tuple = tuple(data_array.array)
            final_array = []
            for num in data_tuple:
                final_array.append(round(float(num), 3))
            return_data.append(final_array)
        self.arrays_tuples = return_data

    def get_info_tab(self):
        if len(self.data_list) == 0:
            self.calculate()
        return_tab = "name      max     min     med     avg      delt \n"
        for i in self.data_list:
            name = i.get("name")
            maximum = self.convert_num_for_tab(i.get("max"))
            minimum = self.convert_num_for_tab(i.get("min"))
            median = self.convert_num_for_tab(i.get("median"))
            average_value = self.convert_num_for_tab(i.get("average"))
            delta = self.convert_num_for_tab(i.get("delta"))
            current_string = (
                f"{name}  {maximum}  {minimum}  {median}  {average_value}  {delta} \n"
            )
            return_tab = return_tab + current_string
        return return_tab

    def __report_to_server_format(self):
        if len(self.data_list) == 0:
            self.calculate()
        maximums_list = ()
        minimums_list = ()
        averages_list = ()
        deltas_list = ()
        for i in self.data_list:
            maximums_list = maximums_list + (i.get("max"),)
            minimums_list = minimums_list + (i.get("min"),)
            averages_list = averages_list + (i.get("average"),)
            deltas_list = deltas_list + (i.get("delta"),)
        maximum = max(*maximums_list)
        minimum = min(*minimums_list)
        median = (minimum + maximum) / 2
        average_ = self.average(averages_list)
        delta = max(deltas_list)
        file_name = self.file_name

        report_to_server_data_dict = {
            "name": file_name,
            "max": maximum,
            "min": minimum,
            "median": median,
            "average": average_,
            "delta": delta,
        }
        return report_to_server_data_dict

    def send_to_db(self, chat_id=None, file_name=None):
        db.send_stat_data_to_server(
            self.__report_to_server_format(), chat_id, file_name
        )
