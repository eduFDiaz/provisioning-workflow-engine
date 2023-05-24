from asyncio import sleep
from CassandraConnection import CassandraConnection
from NotificationDao import NotificationDao
from NotificationModel import NotificationModel
import uuid
from datetime import datetime

notificationId = uuid.UUID("510c6551-aea5-4763-9ff0-1730d9fd6713")

async def main():
    connection = CassandraConnection()
    session = connection.get_session()
    notification_dao = NotificationDao(session)

    # Use the DAO
    # Adding a notification
    new_notification = NotificationModel(
        correlationId=notificationId,
        workflow="workflow1", 
        status="in-progress", 
        step="step1", 
        milestoneName="milestoneName1", 
        milestoneStepName="milestoneStepName1", 
        startTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        endTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    notification_dao.add_or_update_notification(new_notification)    
    
    await sleep(2)

    # Getting a notification
    notification = notification_dao.get_notification(new_notification)
    print(notification.toJSON())

    # Getting all notifications
    notifications = notification_dao.get_all_notifications()
    for notification in notifications:
        print(notification.toJSON())

    # Updating a notification
    updated_notification = NotificationModel(
        correlationId=notificationId,
        workflow="workflow1", 
        status="completed", 
        step="step1", 
        milestoneName="milestoneName1", 
        milestoneStepName="updated_milestoneStepName", 
        startTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        endTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    notification_dao.update_notification(updated_notification)

    # Getting all notifications
    notifications = notification_dao.get_all_notifications()
    for notification in notifications:
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
