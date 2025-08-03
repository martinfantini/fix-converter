from collections import UserDict

class UniqueKeysDict(UserDict):
    def __setitem__(self, key, value):
        if key in self.data:
            raise Exception(f'duplicate key "{key}"')
        self.data[key] = value