import paramiko
import time

from config import logger as log, settings
from Models.Errors.CustomCliStepError import CustomCliStepError

class SSHClient:
    """SSH Client for the CliStep class"""
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        # masking the password and username for the exception handling
        self.exceptionArgs = {"hostname":self.hostname, "username": str(self.username[:3] + '*' * (len(self.username) - 3)), "password":str(self.password[:3] + '*' * (len(self.password) - 3))}
        log.debug(f"SSHClient self.exceptionArgs: {self.exceptionArgs}")
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname, username=username, password=password, 
                timeout=settings.ssh_timeout, banner_timeout=settings.ssh_banner_timeout, 
                auth_timeout=settings.ssh_auth_timeout, look_for_keys=False)
        except Exception as error:
            raise ValueError(CustomCliStepError(payload=error,args=self.exceptionArgs).toJSON())
        
        self.channel = self.ssh.invoke_shell()
    
    def __del__(self):
        log.info(f"closing the SSHClient")

    def execute_command(self, command, timeout=2):
        try:
            self.channel.send(command + '\n')
            output = ''
            while self.channel.recv_ready()==False:
                time.sleep(timeout)
            output += self.channel.recv(65535).decode()
            return output
        except Exception as error:
            self.exceptionArgs['command'] = command
            raise ValueError(CustomCliStepError(payload=error,args=self.exceptionArgs).toJSON())