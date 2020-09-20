class Error400(Exception):
    status_code = 400

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __call__(self, *args, **kwargs):
        return {'message': self.message}
