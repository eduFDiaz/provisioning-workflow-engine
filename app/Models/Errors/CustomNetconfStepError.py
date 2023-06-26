from Models.Errors.ErrorMetadata import errorMetadata
from dataclasses import dataclass
from Models.Errors.CustomError import CustomErrorBase
from config import logging as log

from enum import Enum
from scrapli.exceptions import ScrapliAuthenticationFailed, ScrapliConnectionError, ScrapliTimeout, ScrapliCommandFailure, ScrapliPrivilegeError

class NETCONF_ERRORS(Enum):
    UNSUPPORTED_REQUEST_TYPE = "UNSUPPORTED_REQUEST_TYPE"
    VALIDATE_FETCH_RESPONSE_PARAM_NOT_INITIALIZED = "VALIDATE_FETCH_RESPONSE_PARAM_NOT_INITIALIZED"
    VALIDATE_FETCH_RESPONSE_PARAM_PATH_NOT_FOUND = "VALIDATE_FETCH_RESPONSE_PARAM_PATH_NOT_FOUND"
    VALIDATE_FETCH_RESPONSE_PARAM_NOT_EQUAL = "VALIDATE_FETCH_RESPONSE_PARAM_NOT_EQUAL"
    VALIDATE_FETCH_RESPONSE_EXCEPTION = "VALIDATE_FETCH_RESPONSE_EXCEPTION"
    VALIDATE_EDIT_RESPONSE_ERROR = "VALIDATE_EDIT_RESPONSE_ERROR"
    VALIDATE_FETCH_RESPONSE_EMPTY = "VALIDATE_FETCH_RESPONSE_EMPTY"
    EXTRACT_VARIABLES_NO_MATCHING_VALUE = "EXTRACT_VARIABLES_NO_MATCHING_VALUE"
    EXTRACT_VARIABLES_EXCEPTION = "EXTRACT_VARIABLES_EXCEPTION"
    PROCESS_STEP_FETCH_ERROR = "PROCESS_STEP_FETCH_ERROR"
    PROCESS_STEP_EDIT_ERROR = "PROCESS_STEP_EDIT_ERROR"
    SCRAPLI_AUTHENTICATION_FAILED_HOSTNAME_RESOLUTION_ERROR = "SCRAPLI_AUTHENTICATION_FAILED_HOSTNAME_RESOLUTION_ERROR"
    SCRAPLI_AUTHENTICATION_FAILED_CREDENTIALS_ERROR = "SCRAPLI_AUTHENTICATION_FAILED_CREDENTIALS_ERROR"
    SCRAPLI_CONNECTION_ERROR = "SCRAPLI_CONNECTION_ERROR"
    SCRAPLI_TIMEOUT = "SCRAPLI_TIMEOUT"
    SCRAPLI_COMMAND_FAILURE = "SCRAPLI_COMMAND_FAILURE"
    SCRAPLI_PRIVILEGE_ERROR = "SCRAPLI_PRIVILEGE_ERROR"

@dataclass
class CustomNetconfError(CustomErrorBase):
    def __post_init__(self):
        super().__post_init__()
        self.__processError__()
    def __processError__(self):
        log.info(f"__processError__ Error: {self.payload}")

        match self.payload:
            case NETCONF_ERRORS.UNSUPPORTED_REQUEST_TYPE:
                self.code = 405
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_PARAM_NOT_INITIALIZED:
                self.code = 406
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_PARAM_PATH_NOT_FOUND:
                self.code = 407
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_PARAM_NOT_EQUAL:
                self.code = 408
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)   
                return
            case NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_EXCEPTION:
                self.code = 409
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.VALIDATE_EDIT_RESPONSE_ERROR:
                self.code = 410
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.VALIDATE_FETCH_RESPONSE_EMPTY:
                self.code = 411
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.EXTRACT_VARIABLES_NO_MATCHING_VALUE:
                self.code = 412
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.EXTRACT_VARIABLES_EXCEPTION:
                self.code = 413
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.PROCESS_STEP_FETCH_ERROR:
                self.code = 414
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.PROCESS_STEP_EDIT_ERROR:
                self.code = 415
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)   
                return
            case NETCONF_ERRORS.SCRAPLI_AUTHENTICATION_FAILED_HOSTNAME_RESOLUTION_ERROR:
                self.code = 480
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.SCRAPLI_AUTHENTICATION_FAILED_CREDENTIALS_ERROR:
                self.code = 481
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.SCRAPLI_CONNECTION_ERROR:
                self.code = 482
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.SCRAPLI_TIMEOUT:
                self.code = 483
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.SCRAPLI_COMMAND_FAILURE:
                self.code = 484
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return
            case NETCONF_ERRORS.SCRAPLI_PRIVILEGE_ERROR:
                self.code = 485
                self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
                return

        if isinstance(self.payload, ScrapliAuthenticationFailed):
            log.debug("ScrapliAuthenticationFailed")
            if (str(self.payload).find("Could not resolve address for host") != -1):
                error = CustomNetconfError(NETCONF_ERRORS.SCRAPLI_AUTHENTICATION_FAILED_HOSTNAME_RESOLUTION_ERROR, args=self.args)
                self.code, self.description, self.message = error.code, error.description, error.message
                return
            if (str(self.payload).find("permission denied") != -1):
                error = CustomNetconfError(NETCONF_ERRORS.SCRAPLI_AUTHENTICATION_FAILED_CREDENTIALS_ERROR, args=self.args)
                self.code, self.description, self.message = error.code, error.description, error.message
                return
        if isinstance(self.payload, ScrapliConnectionError):
            log.debug("ScrapliConnectionError")
            error = CustomNetconfError(NETCONF_ERRORS.SCRAPLI_CONNECTION_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, ScrapliTimeout):
            log.debug("ScrapliTimeout")
            error = CustomNetconfError(NETCONF_ERRORS.SCRAPLI_TIMEOUT, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, ScrapliCommandFailure):
            log.debug("ScrapliCommandFailure")
            error = CustomNetconfError(NETCONF_ERRORS.SCRAPLI_COMMAND_FAILURE, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, ScrapliPrivilegeError):
            log.debug("ScrapliPrivilegeError")
            error = CustomNetconfError(NETCONF_ERRORS.SCRAPLI_PRIVILEGE_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,Exception):
            # most generic exception in case the error is not catched by the implementation
            log.debug(f"returning unhandled error not catched by implementation")
            self.code = 999
            self.description = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["description"]
            self.message = errorMetadata[f"NETCONF_STEP_ERROR_{str(self.code)}"]["message"].format_map(self.args)
            return