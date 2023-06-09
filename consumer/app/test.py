from asyncio import sleep
from CassandraConnection import CassandraConnection
from NotificationDao import NotificationDao
from Models.NotificationModel import NotificationModel
import uuid
from datetime import datetime
import json
import requests
from config import logger as log

notificationId = uuid.UUID("0c32b683-683a-4de4-a7f3-44318a14acbc")

async def main():
    connection = CassandraConnection()
    session = connection.get_session()
    notification_dao = NotificationDao(session)

    # jsonRes = {
    # "correlationID": "00000000-0000-0000-0000-000000000000",
    # "workflow": "phy_interface_vrf",
    # "status": "not-started",
    # "step": "Fetch_order_configs",
    # "milestoneName": "phy_interface_vrf",
    # "milestoneStepName": "",
    # "startTime": "",
    # "endTime": ""
    # }

    # # Use the DAO
    # # Adding a notification
    # new_notification = NotificationModel(**json.loads(json.dumps(jsonRes)))
    # # notification_dao.add_or_update_notification(new_notification)    
    # print(f"test get_notification {new_notification.toJSON()}")
    # # await sleep(2)

    # assert(jsonRes == json.loads(new_notification.toJSON()))

    # # get this notification from the Consumer (Notification service)
    # response = requests.post('http://localhost:4040/notification/', json=json.loads(new_notification.toJSON()), verify=False)
        
    # log.debug(f"sendNotifications response {response.status_code}")
    # log.debug(f"sendNotifications response {response.content}")
    # log.debug(f"sendNotifications response unpacked {json.loads(json.dumps(response.json()))}")
    # notification = NotificationModel(**json.loads(json.dumps(response.json())))

    # # Getting a notification
    # notification = notification_dao.get_notification(new_notification)
    # print(f"test get_notification {notification.toJSON()}")

    # # Getting all notifications
    # notifications = notification_dao.get_all_notifications()
    # for notification in notifications:
    #     print(notification.toJSON())

    # # Updating a notification
    # updated_notification = NotificationModel(
    #     correlationID=notificationId,
    #     workflow="workflow1", 
    #     status="completed", 
    #     step="step1", 
    #     milestoneName="milestoneName1", 
    #     milestoneStepName="updated_milestoneStepName", 
    #     startTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
    #     endTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # )
    # notification_dao.update_notification(updated_notification)

    # # Getting all notifications
    # notifications = notification_dao.get_all_notifications()
    # for notification in notifications:
    #     print(notification.toJSON())

    notificationsbyCorrelationId = notification_dao.get_notifications_by_correlationID(notificationId)
    for notification in notificationsbyCorrelationId:
        print(notification.toJSON())

    # Deleting a notification
    # notification_dao.delete_notification(updated_notification)

    # Closing connection
    connection.close()

if __name__ == "__main__":
    import asyncio

    async def run_main():
        await main()

    asyncio.run(run_main())
