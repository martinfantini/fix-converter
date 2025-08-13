# Copyright (C) 2025 Roberto Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from collections import UserDict

class UniqueKeysDict(UserDict):
    def __setitem__(self, key, value):
        if key in self.data:
            raise Exception(f'duplicate key "{key}"')
        self.data[key] = value