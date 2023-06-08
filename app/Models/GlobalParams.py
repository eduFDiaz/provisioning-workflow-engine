from typing_extensions import override
from typing import Dict

class Global_params:
    _instance = None
    _singleton_data: Dict[str, Dict] = {}
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def getMap(self, correlationID: str):
        if correlationID not in self._singleton_data:
            self._singleton_data[correlationID] = { 'correlationID': correlationID }
        return self._singleton_data[correlationID]
    
    @override
    def __str__(self) -> str:
        return str(self._singleton_data)