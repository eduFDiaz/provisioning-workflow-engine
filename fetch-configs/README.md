# Requirements
Install dependencies

`pip install netconf-console2`

To view the configs of the sandbox

`netconf-console2 --host=sandbox-iosxe-latest-1.cisco.com --port=830 --user=admin --password=C1sco12345 --get-config`

# Fetch interfaces
Run the script to fetch interfaces, description and status

`python get-configs.py`
```
$ python get-configs.py 
Interface GigabitEthernet1 has description: MANAGEMENT INTERFACE - DON'T TOUCH ME and is enabled: true
Interface GigabitEthernet2 has description: restconf_patch and is enabled: true
Interface GigabitEthernet3 has description: Network Interface and is enabled: false
Interface Loopback0 has description: CREATE_L1_RESTCONF and is enabled: true
Interface Loopback1 has description: test_netconf and is enabled: true
Interface Loopback10 has description: Configured by RESTCONF ga jadi and is enabled: true
Interface Loopback19 has description: TEST_SPSJM and is enabled: false
Interface Loopback42 has description: CCNP - YAS and is enabled: true```

# implementation
pip install requests paramiko ncclient grpcio grpcio-tools PyYAML