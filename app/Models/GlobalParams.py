from typing_extensions import override

class Global_params:
    _instance = None
    _singleton_data = {}
    # _singleton_data = {
    # "city_id":["AUSTIN"],
    # "site_id":["site1"],
    # "sites": [ 
    #     {"name" : "site1"},
    #     {"name" : "site2"}
    # ]
    # }
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def getitem(self, key):
        return self._singleton_data.get(key)

    def setitem(self, key, value):
        self._singleton_data[key] = value
    
    def update(self, value):
        self._singleton_data.update(value)
    
    def getMap(self):
        return self._singleton_data
    
    @override
    def __str__(self) -> str:
        return str(self._singleton_data)