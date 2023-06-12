import paramiko
import time

from config import logger as log, settings
from socket import error as socket_error

class SSHClient:
    """SSH Client for the CliStep class"""
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname, username=username, password=password, 
                timeout=settings.ssh_timeout, banner_timeout=settings.ssh_banner_timeout, 
                auth_timeout=settings.ssh_auth_timeout, look_for_keys=False)
        except paramiko.BadHostKeyException as error:
            print ("BadHostKeyException")
            print (error)
        except paramiko.AuthenticationException as error:
            print ("AuthenticationException")
            print (error)
        except paramiko.UnableToAuthenticate as error:
            print ("UnableToAuthenticate")
            print (error)
        except socket_error as error:
            print ("socket_error")
            print (error)
        except paramiko.NoValidConnectionsError as error:
            print ("NoValidConnectionsError")
            print (error)
        except paramiko.SSHException as error:
            print ("SSHException")
            print (error)
        
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