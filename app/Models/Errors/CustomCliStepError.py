from Models.Errors.ErrorMetadata import errorMetadata
from dataclasses import dataclass
from Models.Errors.CustomError import CustomErrorBase
from config import logging as log

from enum import Enum
from paramiko import BadHostKeyException, AuthenticationException, ChannelException, BadAuthenticationType, PasswordRequiredException, ProxyCommandFailure, SSHException
from socket import gaierror

class CLI_ERRORS(Enum):
    BAD_HOST_KEY_ERROR = "BAD_HOST_KEY_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    CHANNEL_ERROR = "CHANNEL_ERROR"
    BAD_AUTHENTICATION_TYPE_ERROR = "BAD_AUTHENTICATION_TYPE_ERROR"
    PASSWORD_REQUIRED_ERROR = "PASSWORD_REQUIRED_ERROR"
    PROXY_COMMAND_FAILURE_ERROR = "PROXY_COMMAND_FAILURE_ERROR"
    SSH_ERROR = "SSH_ERROR"
    ADDRESS_ERROR = "ADDRESS_ERROR"

@dataclass
class CustomCliStepError(CustomErrorBase):
    def __post_init__(self):
        super().__post_init__()
        self.__processError__()
    def __processError__(self):
        log.info(f"__processError__ Error: {self.payload}")

        match self.payload:
            case CLI_ERRORS.BAD_HOST_KEY_ERROR:
                self.code = "CLI_STEP_ERROR_421"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case CLI_ERRORS.AUTHENTICATION_ERROR:
                self.code = "CLI_STEP_ERROR_422"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case CLI_ERRORS.CHANNEL_ERROR:
                self.code = "CLI_STEP_ERROR_423"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case CLI_ERRORS.BAD_AUTHENTICATION_TYPE_ERROR:
                self.code = "CLI_STEP_ERROR_424"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case CLI_ERRORS.PASSWORD_REQUIRED_ERROR:
                self.code = "CLI_STEP_ERROR_425"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case CLI_ERRORS.PROXY_COMMAND_FAILURE_ERROR:
                self.code = "CLI_STEP_ERROR_426"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case CLI_ERRORS.SSH_ERROR:
                self.code = "CLI_STEP_ERROR_427"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case CLI_ERRORS.ADDRESS_ERROR:
                self.code = "CLI_STEP_ERROR_428"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return

        if isinstance(self.payload,BadHostKeyException):
            log.debug("BadHostKeyException")
            error = CustomCliStepError(CLI_ERRORS.BAD_HOST_KEY_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,AuthenticationException):
            log.debug("AuthenticationException")
            error = CustomCliStepError(CLI_ERRORS.AUTHENTICATION_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,ChannelException):
            log.debug("ChannelException")
            error = CustomCliStepError(CLI_ERRORS.CHANNEL_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,BadAuthenticationType):
            log.debug("BadAuthenticationType")
            error = CustomCliStepError(CLI_ERRORS.BAD_AUTHENTICATION_TYPE_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,PasswordRequiredException):
            log.debug("PasswordRequiredException")
            error = CustomCliStepError(CLI_ERRORS.PASSWORD_REQUIRED_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,ProxyCommandFailure):
            log.debug("ProxyCommandFailure")
            error = CustomCliStepError(CLI_ERRORS.PROXY_COMMAND_FAILURE_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,SSHException):
            log.debug("SSHException")
            error = CustomCliStepError(CLI_ERRORS.SSH_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,gaierror):
            log.debug("gaierror")
            error = CustomCliStepError(CLI_ERRORS.ADDRESS_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,Exception):
            # most generic exception in case the error is not catched by the implementation
            log.debug(f"returning unhandled error not catched by implementation")
            self.code = "CLI_STEP_ERROR_999"
            self.description = errorMetadata[self.code]["description"]
            self.message = errorMetadata[self.code]["message"].format_map(self.args)
            return