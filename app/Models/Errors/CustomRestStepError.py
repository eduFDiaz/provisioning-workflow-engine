from Models.Errors.ErrorMetadata import errorMetadata
from dataclasses import dataclass
from Models.Errors.CustomError import CustomErrorBase
from config import logging as log

from enum import Enum
import requests.exceptions as reqExceptions

class REST_ERRORS(Enum):
    STATUS_CODE_MISMATCH = "STATUS_CODE_MISMATCH"
    PARAM_VALUE_MISMATCH = "PARAM_VALUE_MISMATCH"
    EXTRACT_VALUE_ERROR = "EXTRACT_VALUE_ERROR"
    EXTRACT_VALUE_UNHANDLED_ERROR = "EXTRACT_VALUE_UNHANDLED_ERROR"
    UNSUPPORTED_METHOD = "UNSUPPORTED_METHOD"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    REQUEST_TIMEOUT_ERROR = "REQUEST_TIMEOUT_ERROR"
    TOO_MANY_REDIRECTS_ERROR = "TOO_MANY_REDIRECTS_ERROR"
    URL_REQUIRED_ERROR = "URL_REQUIRED_ERROR"
    MISSING_SCHEMA_ERROR = "MISSING_SCHEMA_ERROR"
    INVALID_SCHEMA_ERROR = "INVALID_SCHEMA_ERROR"
    INVALID_URL_ERROR = "INVALID_URL_ERROR"
    INVALID_HEADER_ERROR = "INVALID_HEADER_ERROR"
    CHUNKED_ENCODING_ERROR = "CHUNKED_ENCODING_ERROR"
    CONTENT_DECODING_ERROR = "CONTENT_DECODING_ERROR"
    RETRY_ERROR = "RETRY_ERROR"
    INVALID_PROXY_URL_ERROR = "INVALID_PROXY_URL_ERROR"
    PROXY_ERROR = "PROXY_ERROR"
    SSL_ERROR = "SSL_ERROR"

@dataclass
class CustomRestStepError(CustomErrorBase):
    def __post_init__(self):
        super().__post_init__()
        self.__processError__()
    def __processError__(self):
        log.info(f"__processError__ Error: {self.payload}")

        match self.payload:
            case REST_ERRORS.UNSUPPORTED_METHOD:
                self.code = "REST_STEP_ERROR_405"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.STATUS_CODE_MISMATCH:
                self.code = "REST_STEP_ERROR_422"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.PARAM_VALUE_MISMATCH:
                self.code = "REST_STEP_ERROR_423"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.EXTRACT_VALUE_ERROR:
                self.code = "REST_STEP_ERROR_424"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.CONNECTION_ERROR:
                self.code = "REST_STEP_ERROR_504"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
            case REST_ERRORS.REQUEST_TIMEOUT_ERROR:
                self.code = "REST_STEP_ERROR_506"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.TOO_MANY_REDIRECTS_ERROR:
                self.code = "REST_STEP_ERROR_302"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.URL_REQUIRED_ERROR:
                self.code = "REST_STEP_ERROR_426"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.MISSING_SCHEMA_ERROR:
                self.code = "REST_STEP_ERROR_427"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.INVALID_SCHEMA_ERROR:
                self.code = "REST_STEP_ERROR_428"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.INVALID_URL_ERROR:
                self.code = "REST_STEP_ERROR_429"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.INVALID_HEADER_ERROR:
                self.code = "REST_STEP_ERROR_430"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.CHUNKED_ENCODING_ERROR:
                self.code = "REST_STEP_ERROR_431"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.CONTENT_DECODING_ERROR:
                self.code = "REST_STEP_ERROR_432"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.RETRY_ERROR:
                self.code = "REST_STEP_ERROR_434"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.INVALID_PROXY_URL_ERROR:
                self.code = "REST_STEP_ERROR_436"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.PROXY_ERROR:
                self.code = "REST_STEP_ERROR_437"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.SSL_ERROR:
                self.code = "REST_STEP_ERROR_438"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case REST_ERRORS.EXTRACT_VALUE_UNHANDLED_ERROR:
                self.code = "REST_STEP_ERROR_999"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return

        if isinstance(self.payload,reqExceptions.ConnectionError):
            log.debug("ConnectionError")
            error = CustomRestStepError(REST_ERRORS.CONNECTION_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.Timeout):
            log.debug("Timeout")
            error = CustomRestStepError(REST_ERRORS.REQUEST_TIMEOUT_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.TooManyRedirects):
            log.debug("TooManyRedirects")
            error = CustomRestStepError(REST_ERRORS.TOO_MANY_REDIRECTS_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.URLRequired):
            log.debug("URLRequired")
            error = CustomRestStepError(REST_ERRORS.URL_REQUIRED_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.MissingSchema):
            log.debug("MissingSchema")
            error = CustomRestStepError(REST_ERRORS.MISSING_SCHEMA_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.InvalidSchema):
            log.debug("InvalidSchema")
            error = CustomRestStepError(REST_ERRORS.INVALID_SCHEMA_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.InvalidURL):
            log.debug("InvalidURL")
            error = CustomRestStepError(REST_ERRORS.INVALID_URL_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.InvalidHeader):
            log.debug("InvalidHeader")
            error = CustomRestStepError(REST_ERRORS.INVALID_HEADER_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.ChunkedEncodingError):
            log.debug("ChunkedEncodingError")
            error = CustomRestStepError(REST_ERRORS.CHUNKED_ENCODING_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.ContentDecodingError):
            log.debug("ContentDecodingError")
            error = CustomRestStepError(REST_ERRORS.CONTENT_DECODING_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.RetryError):
            log.debug("RetryError")
            error = CustomRestStepError(REST_ERRORS.RETRY_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.InvalidProxyURL):
            log.debug("InvalidProxyURL")
            error = CustomRestStepError(REST_ERRORS.INVALID_PROXY_URL_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.ProxyError):
            log.debug("ProxyError")
            error = CustomRestStepError(REST_ERRORS.PROXY_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,reqExceptions.SSLError):
            log.debug("SSLError")
            error = CustomRestStepError(REST_ERRORS.SSL_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload,Exception):
            # most generic exception in case the error is not catched by the implementation
            log.debug(f"returning unhandled error not catched by implementation")
            self.code = "REST_STEP_ERROR_999"
            self.description = errorMetadata[self.code]["description"]
            self.message = errorMetadata[self.code]["message"].format_map(self.args)
            return

        