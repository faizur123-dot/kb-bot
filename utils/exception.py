class MyError(Exception):
    def __init__(self, error_code, error_message, error_data=None):
        super().__init__({
            'error_code': error_code,
            'error_message': error_message,
            'error_data': error_data
        })
        self.error_code = error_code
        self.error_message = error_message
        self.error_data = error_data

    def __getitem__(self, key):
        if key == 'error_code':
            return self.error_code
        elif key == 'error_message':
            return self.error_message
        elif key == 'error_data':
            return self.error_data
        else:
            raise KeyError(f"{key} not found in MyError")
