class MyResponse:
    def __init__(self, status_code, body: dict):
        self.status_code = status_code
        self.body = body

    def to_dict(self):
        return {
            'status_code': self.status_code,
            'body': self.body
        }
