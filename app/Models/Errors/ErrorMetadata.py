from pydantic import BaseModel
import json
import uuid

class ErrorModel(BaseModel):
        correlationID: uuid.UUID
        timeStamp: str
        error: str

        def toJSON(self):
                json_dict = self.dict()
                json_dict['correlationID'] = str(json_dict['correlationID'])
                return json.dumps(json_dict, default=lambda o: o.__dict__, 
                        sort_keys=True, indent=4)

errorMetadata = {
        "GITHUB_ERROR_401" : { "description" : "connecting Github" , "message" : "access token not valid" },
        "GITHUB_ERROR_404" : { "description" : "resource not found" , "message" : "repo {repoName} not found" },
        "GITHUB_ERROR_405" : { "description" : "resource not found" , "message" : "branch {branch} not found" },
        "GITHUB_ERROR_999" : { "description" : "unhandled error" , "message" : "unhandled error" },
        
        "READ_STEPS_TEMPLATE_ERRORS_401" : { "description" : "step file read error" , "message" : "step file: {file_path} not found" },
        "READ_STEPS_TEMPLATE_ERRORS_402" : { "description" : "step file read error" , "message" : "provided path: {file_path} is a directory" },
        "READ_STEPS_TEMPLATE_ERRORS_403" : { "description" : "step file read error" , "message" : "permission denied for file: {file_path}" },
        "READ_STEPS_TEMPLATE_ERRORS_404" : { "description" : "step file read error" , "message" : "file: {file_path} content is not a string or a bytes-like object that can be parsed" },
        "READ_STEPS_TEMPLATE_ERRORS_405" : { "description" : "step file read error" , "message" : "file: {file_path} contains non-UTF-8 encoded data that cannot be decoded" },
        "READ_STEPS_TEMPLATE_ERRORS_406" : { "description" : "step file read error" , "message" : "file: {file_path} YML invalid syntax, error: {syntaxError}" },
        "READ_STEPS_TEMPLATE_ERRORS_407" : { "description" : "jinja template syntax error" , "message" : "file: {file_path} jinja2 invalid syntax, error: {syntaxError}" },
        "READ_STEPS_TEMPLATE_ERRORS_408" : { "description" : "jinja template syntax error" , "message" : "file: {file_path} jinja2 param value not provided please add it to *.values.yml, error: {syntaxError}" },
        "READ_STEPS_TEMPLATE_ERRORS_999" : { "description" : "unhandled error" , "message" : "unhandled error: {error}" },
        
        "REST_STEP_ERROR_302" : { "description" : "too many redirects" , "message" : "too many redirects when requesting resource: {url}" },
        "REST_STEP_ERROR_405" : { "description" : "unsupported HTTP method" , "message" : "method: {method} not allowed, try GET or POST" },
        "REST_STEP_ERROR_422" : { "description" : "unprocessable entity" , "message" : "response code: {actualStatusCode} != expected code: {expectedStatusCode}" },
        "REST_STEP_ERROR_423" : { "description" : "unprocessable entity" , "message" : "response param with path: {path} != expected value: {expectedValue}" },
        "REST_STEP_ERROR_424" : { "description" : "unprocessable entity" , "message" : "variable in path: {path} not found in response" },
        "REST_STEP_ERROR_425" : { "description" : "unprocessable entity" , "message" : "extracting variables from response, unhandled error" },
        "REST_STEP_ERROR_426" : { "description" : "unprocessable entity" , "message" : "url required, url passed: {url}" },
        "REST_STEP_ERROR_427" : { "description" : "unprocessable entity" , "message" : "missing schema, url provided: {url}" },
        "REST_STEP_ERROR_428" : { "description" : "unprocessable entity" , "message" : "invalid schema, url provided: {url}, protocol is most likely not recognized, or not supported by the underlying network transport" },
        "REST_STEP_ERROR_429" : { "description" : "unprocessable entity" , "message" : "invalid url provided: {url}, please check for invalid chars in the url" },
        "REST_STEP_ERROR_430" : { "description" : "unprocessable entity" , "message" : "invalid headers provided: {headers}, please all the header values are strings" },
        "REST_STEP_ERROR_431" : { "description" : "unprocessable entity" , "message" : "resource: {url} response body was not properly chunk-encoded" },
        "REST_STEP_ERROR_432" : { "description" : "unprocessable entity" , "message" : "resource: {url} response body decoding failed, please check headers" },
        "REST_STEP_ERROR_434" : { "description" : "unprocessable entity" , "message" : "retry attempts exceeded for the requested resource:{url}" },
        "REST_STEP_ERROR_436" : { "description" : "unprocessable entity" , "message" : "proxy url provided is invalid" },
        "REST_STEP_ERROR_437" : { "description" : "unprocessable entity" , "message" : "invalid proxy server, check proxy credentials as well" },
        "REST_STEP_ERROR_438" : { "description" : "unprocessable entity" , "message" : "invalid SSL certificate for the service:{host}" },
        "REST_STEP_ERROR_504" : { "description" : "gateway timeout" , "message" : "service not reachable host:{host} port:{port}" },
        "REST_STEP_ERROR_506" : { "description" : "gateway timeout" , "message" : "service timed out when requesting {url}" },
        "REST_STEP_ERROR_999" : { "description" : "unhandled error" , "message" : "unhandled error" },
        "CLI_STEP_ERROR_421" : { "description" : "connecting to host" , "message" : "server: {hostname} identity's cannot be verified" },
        "CLI_STEP_ERROR_422" : { "description" : "authentication error" , "message" : "authentication failed! Provider username: {username}, password: {password}" },
        "CLI_STEP_ERROR_423" : { "description" : "channel error" , "message" : "host: {hostname} unexpectedly closed the connection, issued command: {command}" },
        "CLI_STEP_ERROR_424" : { "description" : "authentication type error" , "message" : "authentication type not supported by the host: {hostname}"},
        "CLI_STEP_ERROR_425" : { "description" : "password required error" , "message" : "authentication requires password, password provided: {password}" },
        "CLI_STEP_ERROR_426" : { "description" : "proxy command error" , "message" : "ssh over proxy failed" },
        "CLI_STEP_ERROR_427" : { "description" : "ssh connection error", "message" : "ssh connection failed, hostname: {hostname}, username: {username}, password: {password}" },
        "CLI_STEP_ERROR_428" : { "description" : "address info error", "message" : "Name or service: {hostname} not known" },
        "CLI_STEP_ERROR_999" : { "description" : "unhandled error" , "message" : "unhandled error" },
        "NETCONF_STEP_ERROR_405" : { "description" : "unsupported request type" , "message" : "request type: {request_type} not allowed, try FETCH or EDIT" },
        "NETCONF_STEP_ERROR_406" : { "description" : "param to validate not initilized" , "message" : "param: {param} not initilized, please add it to *.values.yml" },
        "NETCONF_STEP_ERROR_407" : { "description" : "param to validate not found" , "message" : "param with path: {path} not found in the response, please correct the json path expression for this param in the step definifion .yml file validate section" },
        "NETCONF_STEP_ERROR_408" : { "description" : "response param validation error" , "message" : "response param: {path} not matching expected value: {result}. please correct it in *.values.yml" },
        "NETCONF_STEP_ERROR_409" : { "description" : "response param validation error" , "message" : "unhandled exception: {exception}" },
        "NETCONF_STEP_ERROR_410" : { "description" : "edit request error" , "message" : "netconf rpc response {response} was not of the expected type </ok>" },
        "NETCONF_STEP_ERROR_411" : { "description" : "edit request error" , "message" : "netconf rpc response {response} was empty, please correct the request payload in the step definition .yml file" },
        "NETCONF_STEP_ERROR_412" : { "description" : "extract param error" , "message" : "param with path: {path} not found in the response: {response}\n, please correct the json path expression for this param in variables section of the step definifion .yml file" },
        "NETCONF_STEP_ERROR_413" : { "description" : "extract param error" , "message" : "unhandled exception: {exception}" },
        "NETCONF_STEP_ERROR_414" : { "description" : "fetch request error" , "message" : "error validating and extracting params from netconf response, validate response: {validProcess}, extract params {extractVariables}." },
        "NETCONF_STEP_ERROR_415" : { "description" : "edit request error" , "message" : "edit netconf request validation sucess:{validProcess}" },
        "NETCONF_STEP_ERROR_480" : { "description" : "hostname resolution error" , "message" : "Could not resolve address for host: {host}" },
        "NETCONF_STEP_ERROR_481" : { "description" : "invalid credentials error" , "message" : "Invalid credentials provided, username: {username}, password: {password}" },
        "NETCONF_STEP_ERROR_482" : { "description" : "connection error" , "message" : "connection could not be stablished to host: {host}" },
        "NETCONF_STEP_ERROR_483" : { "description" : "timeout error" , "message" : "connection timed out" },
        "NETCONF_STEP_ERROR_484" : { "description" : "command execution failed" , "message" : "command execution with payload: {config} please check the request payload in the step definition .yml file" },
        "NETCONF_STEP_ERROR_485" : { "description" : "privilege error" , "message" : "please check the user: {username} has priviledges to execute the request with payload: {config}" },
        "NETCONF_STEP_ERROR_999" : { "description" : "unhandled error" , "message" : "unhandled error" },
}