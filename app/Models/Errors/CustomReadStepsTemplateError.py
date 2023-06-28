from Models.Errors.ErrorMetadata import errorMetadata
from dataclasses import dataclass
from Models.Errors.CustomError import CustomErrorBase
from config import logging as log

from enum import Enum
from yaml import YAMLError
from yaml.scanner import ScannerError
from yaml.parser import ParserError
# FileNotFoundError
# IsADirectoryError
# PermissionError
# TypeError
# UnicodeDecodeError
from jinja2 import TemplateSyntaxError, UndefinedError


class READ_STEPS_TEMPLATE_ERRORS(Enum):
    STEP_FILE_NOT_FOUND_ERROR = "STEP_FILE_NOT_FOUND_ERROR"
    STEP_FILE_IS_A_DIRECTORY_ERROR = "STEP_FILE_IS_A_DIRECTORY_ERROR"
    STEP_FILE_PERMISSION_ERROR = "STEP_FILE_PERMISSION_ERROR"
    STEP_FILE_TYPE_ERROR = "STEP_FILE_TYPE_ERROR"
    STEP_FILE_UNICODE_DECODE_ERROR = "STEP_FILE_UNICODE_DECODE_ERROR"
    STEP_FILE_YAML_ERROR = "STEP_FILE_YAML_ERROR"
    STEP_FILE_JINJA2_SYNTAX_ERROR = "STEP_FILE_JINJA2_SYNTAX_ERROR"
    STEP_FILE_JINJA2_UNDEFINED_PARAM_ERROR = "STEP_FILE_JINJA2_UNDEFINED_PARAM_ERROR"
    READ_STEPS_TEMPLATE_UNHANDLED_ERROR = "READ_STEPS_TEMPLATE_UNHANDLED_ERROR"

@dataclass
class CustomReadStepsTemplateError(CustomErrorBase):
    def __post_init__(self):
        super().__post_init__()
        self.__processError__()
    def __processError__(self):
        log.info(f"__processError__ Error: {self.payload}")

        match self.payload:
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_NOT_FOUND_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_401"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_IS_A_DIRECTORY_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_402"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_PERMISSION_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_403"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_TYPE_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_404"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_UNICODE_DECODE_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_405"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_YAML_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_406"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_JINJA2_SYNTAX_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_407"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_JINJA2_UNDEFINED_PARAM_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_408"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case READ_STEPS_TEMPLATE_ERRORS.READ_STEPS_TEMPLATE_UNHANDLED_ERROR:
                self.code = "READ_STEPS_TEMPLATE_ERRORS_999"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return

        if isinstance(self.payload, FileNotFoundError):
            log.debug("FileNotFoundError")
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_NOT_FOUND_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, IsADirectoryError):
            log.debug("IsADirectoryError")
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_IS_A_DIRECTORY_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, PermissionError):
            log.debug("PermissionError")
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_PERMISSION_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, TypeError):
            log.debug("TypeError")
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_TYPE_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, UnicodeDecodeError):
            log.debug("UnicodeDecodeError")
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_UNICODE_DECODE_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, (YAMLError, ScannerError, ParserError)):
            log.debug("YAMLError")
            self.args["syntaxError"] = self.payload
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_YAML_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, TemplateSyntaxError):
            log.debug("TemplateSyntaxError")
            self.args["syntaxError"] = self.payload
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_JINJA2_SYNTAX_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, UndefinedError):
            log.debug("UndefinedError")
            self.args["syntaxError"] = self.payload
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.STEP_FILE_JINJA2_UNDEFINED_PARAM_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        if isinstance(self.payload, Exception):
            log.debug(f"returning unhandled error not catched by implementation")
            self.args["error"] = self.payload
            error = CustomReadStepsTemplateError(READ_STEPS_TEMPLATE_ERRORS.READ_STEPS_TEMPLATE_UNHANDLED_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return

