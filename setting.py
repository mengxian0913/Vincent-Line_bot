class User:
    def __init__(self, id, name, email, nid_account, nid_password, codeforces_handle, codeforces_password) -> None:
        self.user_id = id
        self.user_name = name
        self.email = email
        self.nid_account = nid_account
        self.nid_password = nid_password
        self.codeforces_handle = codeforces_handle
        self.codeforces_password = codeforces_password
        self.codeforces_register_state = 0
    

Users = {}

# examlpe_user = User('example_id', 1, 1, 1, 1, 1, 1)
# Users['example_id'] = examlpe_user

# print(Users['example_id'].codeforces_register_state)