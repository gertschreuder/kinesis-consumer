class Wrapper(object):
    def load(self, key, initial_data):
        if key not in self.__dict__:
            setattr(self, key, [])
        data = {
            "PutRequest": {
                "Item": initial_data
            }
        }

        self.__dict__[key].append(data)
