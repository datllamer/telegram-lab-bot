class access_level:
    def __init__(self, needed_user_rights):
        self.needed_user_rights = needed_user_rights

    def is_access_granted(self, user_rights):
        if user_rights in self.needed_user_rights:
            return True
        else:
            return False


not_user = access_level(("not_user", "user0", "user1", "user2", "user3", "admin"))
user0 = access_level(("user0", "user1", "user2", "user3"))
user1 = access_level(("user1", "user2", "user3"))
user2 = access_level(("user2", "user3"))
user3 = access_level("user3")
admin = access_level("admin")
