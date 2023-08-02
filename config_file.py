import os

#    processing settings
arrays_quantity = int(os.getenv("ARRAYSQUANTITY"))  # 5
central_array__id = int(os.getenv("CENTRALARRAYID"))  # 0
file_name = None  # (can be None)
skiprows = int(os.getenv("SKIPROWS"))  # 13
in_document_columns = None  # (can be None)
API_key = os.getenv("APIKEY")

#    MySQL settings
host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")

#    Bot settings
bot_token = os.getenv("BOTTOKEN")
admin_id = os.getenv("ADMINID")
