from Models.Errors.ErrorMetadata import errorMetadata
from dataclasses import dataclass
from Models.Errors.CustomError import CustomErrorBase
from config import logging as log

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

        data = githubError(status=self.payload.status, 
                           message=self.payload.data['message'], 
                           documentation_url=self.payload.data['documentation_url'])
        
        match data.message:
            case "Bad credentials":
                self.code = data.status
                self.description = errorMetadata[f"GITHUB_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"GITHUB_ERROR_{str(self.code)}"]["message"]
                return

        match data.documentation_url:
            case "https://docs.github.com/rest/reference/repos#get-a-repository":
                self.code = data.status
                self.description = errorMetadata[f"GITHUB_ERROR_{str(self.code)}"]["description"]
                self.message = errorMetadata[f"GITHUB_ERROR_{str(self.code)}"]["message"].format(param=self.args['repoName'])
                return
        
        if data.message.__contains__(f"No commit found for the ref {self.args['branch']}"):
            self.code = 405
            self.description = errorMetadata[f"GITHUB_ERROR_{str(self.code)}"]["description"]
            self.message = errorMetadata[f"GITHUB_ERROR_{str(self.code)}"]["message"].format(param=self.args['branch'])
            return

        log.debug(f"returning unhandled error not catched by implementation")
        self.code = 999
        self.description = errorMetadata[f"GITHUB_ERROR_UNHANDLED"]["description"]
        self.message = errorMetadata[f"GITHUB_ERROR_UNHANDLED"]["message"]
        return