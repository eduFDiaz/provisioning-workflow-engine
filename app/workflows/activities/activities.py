from temporalio import activity, workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from config import logger as log
    from typing import Dict
    from Models.RestStep import RestStep
    from Models.CliStep import CliStep
    from Models.NetConfStep import NetConfStep
    from Models.GrpcStep import GrpcStep
    from Clients.KafkaProducer import send_in_progress_notification, send_complete_notification, send_error_notification, prepare_notification
    import requests
    import json
    from Models.NotificationModel import NotificationModel
    from config import is_running_in_docker
    from config import settings
    from Utils.Utils import read_step_yaml, get_list_of_steps
    
consumer_app_host = None
if is_running_in_docker:
    consumer_app_host = 'consumer_app'
else:
    consumer_app_host = 'localhost'

def sendNotifications(func):
    """Decorator to send notifications when a step is started, completed or failed.
    When the step is already completed from a previous flow instance this decorator
    returns without executing the step (i.e. without calling func)
    """
    async def wrapper(*args, **kwargs):
        notification = prepare_notification(args[0])
        
        # get this notification from the Consumer (Notification service)
        # TODO: outsource this code to a separate service?
        response = requests.post(f'http://{settings.consumer_app_host}:{settings.consumer_app_port}/notification/', json=json.loads(notification.toJSON()), verify=False)
        
        log.debug(f"sendNotifications response {response.status_code}")
        log.debug(f"sendNotifications response {response.json()}")
        log.debug(f"sendNotifications response unpacked {json.loads(json.dumps(response.json()))}")
        notification = NotificationModel(**json.loads(json.dumps(response.json())))

        log.debug(f"notification from response {notification}")
        if notification.status == "completed":
            log.debug(f"step already completed, not executing it")
            return 0

        log.debug(f"sendNotifications before in progress")
        notification = prepare_notification(args[0])

        notification = await send_in_progress_notification(notification)

        # execute the activity code
        try:
            result = await func(*args, **kwargs)
            log.debug(f"execute step result {result}")

            await send_complete_notification(notification)
            log.debug(f"sendNotifications after completed")
        except Exception as e:
            log.error(f"execute step exception {e}")
            notification = await send_error_notification(notification)
            raise e
        return result
    
    return wrapper

@activity.defn(name="read_template")
# @sendNotifications
async def read_template(wfFileName: str, requestId: str) -> list:
    log.debug(f"Step read_template {wfFileName} {requestId}")
    steps, error = get_list_of_steps(wfFileName, requestId)
    return steps


@activity.defn(name="exec_rest_step")
@sendNotifications
async def exec_rest_step(conf: Dict) -> int:
    log.debug(f"RestStep exec_rest_step {conf}")
    step = RestStep(conf)
    result = step.process_step()
    log.debug(f"RestStep process_step {step} - {result}")
    return result

@activity.defn(name="exec_netconf_step")
@sendNotifications
async def exec_netconf_step(conf: Dict) -> int:
    log.debug(f"NetConfStep exec_rest_step {conf}")
    step = NetConfStep(conf)
    result = step.process_step()
    log.debug(f"NetConfStep process_step {step} - {result}")
    return result

@activity.defn(name="exec_cli_step")
@sendNotifications
async def exec_cli_step(conf: Dict) -> int:
    log.debug(f"CliStep exec_rest_step {conf}")
    step = CliStep(conf)
    result = step.process_step()
    log.debug(f"CliStep process_step {step} - {result}")
    return result

@activity.defn(name="exec_grpc_step")
@sendNotifications
async def exec_grpc_step(conf: Dict) -> int:
    log.debug(f"GrpcStep exec_rest_step {conf}")
    step = GrpcStep(conf)
    result = step.process_step()
    log.debug(f"GrpcStep process_step {step} - {result}")
    return result