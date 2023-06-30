from Models.Errors.ErrorMetadata import errorMetadata
from dataclasses import dataclass
from Models.Errors.CustomError import CustomErrorBase
from config import logging as log

from enum import Enum

from github import GithubException
from urllib3.exceptions import ReadTimeoutError

class GITHUB_ERRORS(Enum):
    GITHUB_CREDENTIALS_ERROR = "GITHUB_CREDENTIALS_ERROR"
    GITHUB_REPO_NOT_FOUND_ERROR = "GITHUB_REPO_NOT_FOUND_ERROR"
    GITHUB_BRANCH_NOT_FOUND_ERROR = "GITHUB_BRANCH_NOT_FOUND_ERROR"
    GITHUB_TIMEOUT_ERROR = "GITHUB_TIMEOUT_ERROR"
    GITHUB_ERROR_UNHANDLED_ERROR = "GITHUB_ERROR_UNHANDLED_ERROR"

@dataclass
class githubError:
    status: int
    message: str
    documentation_url: str

@dataclass
class CustomGithubError(CustomErrorBase):
    def __post_init__(self):
        super().__post_init__()
        self.__processError__()
    def __processError__(self):
        log.info(f"__processError__ Error: {self.payload}")
        log.info(f"__processError__ Error class: {self.payload.__class__.__name__}")

        match self.payload:
            case GITHUB_ERRORS.GITHUB_CREDENTIALS_ERROR:
                self.code = "GITHUB_ERROR_401"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case GITHUB_ERRORS.GITHUB_REPO_NOT_FOUND_ERROR:
                self.code = "GITHUB_ERROR_404"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case GITHUB_ERRORS.GITHUB_BRANCH_NOT_FOUND_ERROR:
                self.code = "GITHUB_ERROR_405"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case GITHUB_ERRORS.GITHUB_TIMEOUT_ERROR:
                self.code = "GITHUB_ERROR_406"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
            case GITHUB_ERRORS.GITHUB_ERROR_UNHANDLED_ERROR:
                self.code = "GITHUB_ERROR_999"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
        
        if isinstance(self.payload, ReadTimeoutError):
            error = CustomGithubError(GITHUB_ERRORS.GITHUB_TIMEOUT_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return

        if isinstance(self.payload, GithubException):
            data = githubError(status=self.payload.status, 
                            message=self.payload.data['message'], 
                            documentation_url=self.payload.data['documentation_url'])
            
            log.debug(f"Github error - {data}")
            
            match data.message:
                case "Bad credentials":
                    error = CustomGithubError(GITHUB_ERRORS.GITHUB_CREDENTIALS_ERROR, args=self.args)
                    self.code, self.description, self.message = error.code, error.description, error.message
                    return

            match data.documentation_url:
                case "https://docs.github.com/rest/reference/repos#get-a-repository":
                    error = CustomGithubError(GITHUB_ERRORS.GITHUB_REPO_NOT_FOUND_ERROR, args=self.args)
                    self.code, self.description, self.message = error.code, error.description, error.message
                    return
            
            if data.message.__contains__(f"No commit found for the ref {self.args['branch']}"):
                error = CustomGithubError(GITHUB_ERRORS.GITHUB_BRANCH_NOT_FOUND_ERROR, args=self.args)
                self.code, self.description, self.message = error.code, error.description, error.message
                return

            log.debug(f"returning unhandled error not catched by implementation")
            self.args['exceptionClassName'] = self.payload.__class__.__name__
            self.args['error'] = self.payload
            error = CustomGithubError(GITHUB_ERRORS.GITHUB_ERROR_UNHANDLED_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return
        
        if isinstance(self.payload, Exception):
            self.args['exceptionClassName'] = self.payload.__class__.__name__
            self.args['error'] = self.payload
            error = CustomGithubError(GITHUB_ERRORS.GITHUB_ERROR_UNHANDLED_ERROR, args=self.args)
            self.code, self.description, self.message = error.code, error.description, error.message
            return