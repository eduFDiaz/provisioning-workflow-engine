from typing_extensions import override

api_credentials = {
    'REST': {
        'username': 'rest_user',
        'password': 'rest_pass',
        'paramsFile': './PARAMS/REST_PARAMS.yml'
    },
    'CLI': {
        'username': 'cli_user',
        'password': 'cli_pass',
        'paramsFile': './PARAMS/CLI_PARAMS.yml'
    },
    'NETCONF': {
        'username': 'netconf_user',
        'password': 'netconf_pass',
        'paramsFile': './PARAMS/NETCONF_PARAMS.yml'
    },
    'GRPC': {
        'username': 'grpc_user',
        'password': 'grpc_pass',
        'paramsFile': './PARAMS/GRPC_PARAMS.yml'
    }
}

class Global_params:
    _instance = None
    _singleton_data = {
    "city_id":["AUSTIN"],
    "site_id":["site1"],
    "sites": [ 
        {"name" : "site1"},
        {"name" : "site2"}
    ]
    }
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def getitem(self, key):
        return self._singleton_data[key]

    def setitem(self, key, value):
        self._singleton_data[key] = value
    
    def update(self, value):
        self._singleton_data.update(value)
    
    def getMap(self):
        return self._singleton_data
    
    @override
    def __str__(self) -> str:
        return str(self._singleton_data)
