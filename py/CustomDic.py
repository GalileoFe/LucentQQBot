class CustomDict(dict):
    def __init__(self, initial_data=None, listener=None):
        super().__init__()
        self.listener = listener
        if initial_data:
            for key, value in initial_data.items():
                self[key] = value

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if self.listener:
            self.listener()
        return value

