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
                self.code = f"GITHUB_ERROR_{str(data.status)}"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return

        match data.documentation_url:
            case "https://docs.github.com/rest/reference/repos#get-a-repository":
                self.code = f"GITHUB_ERROR_{str(data.status)}"
                self.description = errorMetadata[self.code]["description"]
                self.message = errorMetadata[self.code]["message"].format_map(self.args)
                return
        
        if data.message.__contains__(f"No commit found for the ref {self.args['branch']}"):
            self.code = "GITHUB_ERROR_405"
            self.description = errorMetadata[self.code]["description"]
            self.message = errorMetadata[self.code]["message"].format_map(self.args)
            return

        log.debug(f"returning unhandled error not catched by implementation")
        self.code = "GITHUB_ERROR_999"
        self.description = errorMetadata[self.code]["description"]
        self.message = errorMetadata[self.code]["message"].format_map(self.args)
        return