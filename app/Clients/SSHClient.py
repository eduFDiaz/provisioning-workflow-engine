import paramiko
import time

from config import logger as log

class SSHClient:
    """SSH Client for the CliStep class"""
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname, username=username, password=password)
        self.channel = self.ssh.invoke_shell()
    
    def __del__(self):
        log.info(f"closing the SSHClient")

    def execute_command(self, command, timeout=2):
        self.channel.send(command + '\n')
        output = ''
        while self.channel.recv_ready()==False:
            time.sleep(timeout)
        output += self.channel.recv(65535).decode()
        return output