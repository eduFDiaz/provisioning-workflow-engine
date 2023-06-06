from typing_extensions import override

class Global_params:
    _instance = None
    _singleton_data = {
        "interfaceName":["GigabitEthernet1"],
        "loopbackInterface": ["Loopback109"],
        'api_key': 'api_key_value', 'uuid': '7c277d3a-a11c-433a-a4a8-c9e6bc39a7a6', 'userId': 'palsa', 'interface_name': 'GigabitEthernet1', 'dns_name': '8.8.8.8', 'PL_AS_65003_IN': ['ip address 10.0.1.19', 'ip address 10.0.1.20', 'ip address 10.0.1.21'], 'ip_prefix_list': [[{'name': 'Capgemini-DC1-Management', 'index': 10, 'action': 'permit', 'prefix': '192.168.187.0/28'}]], 'route_map': [[{'name': 'Capgemini-VRF-IMPORT', 'match-list': [{'index': 10, 'operation': 'permit', 'prefix': 'Capgemini-DC1-Management'}, {'index': 20, 'operation': 'permit', 'prefix': 'Capgemini-DC2-Management'}]}]], 'vrf': [[{'name': 'VRF_Capgemini', 'rd': '100:110', 'rt-import': ['100:1000'], 'rt-export': ['100:1000'], 'ipv4-import': ['Capgemini-VRF-IMPORT'], 'ipv4-export': ['Capgemini-VRF-EXPORT']}]]
    }
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