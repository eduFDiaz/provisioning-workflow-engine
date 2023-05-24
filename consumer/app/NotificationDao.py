from cassandra.query import SimpleStatement
from NotificationModel import NotificationModel

class NotificationDao:
    def __init__(self, session):
        self.session = session

    def get_notification(self, notification):
        """ This method returns a notification for a given workflow, step, milestoneName and correlationId. """
        stmt = SimpleStatement("""
            SELECT * 
            FROM workflows.Notifications 
            WHERE "workflow"=%s AND "step"=%s AND "milestoneName"=%s AND "correlationId"=%s
        """, fetch_size=10)
        notification = self.session.execute(stmt, 
        [
        notification.workflow, 
        notification.step, 
        notification.milestoneName,
        notification.correlationId
        ])
        notification = notification[0]._asdict()
        print(notification)
        return NotificationModel(**notification)
    
    def get_notifications_by_correlationId(self, correlationId):
        """ This method returns all notifications for a given correlationId."""
        stmt = SimpleStatement("""
            SELECT * 
            FROM workflows.Notifications 
            WHERE "correlationId"=%s
        """, fetch_size=10)
        notifications = self.session.execute(stmt, [correlationId])
        return [NotificationModel(**notification._asdict()) for notification in notifications]

    def get_all_notifications(self):
        stmt = SimpleStatement("SELECT * FROM workflows.Notifications", fetch_size=10)
        notifications = self.session.execute(stmt)
        return [NotificationModel(**notification._asdict()) for notification in notifications]

    def update_notification(self, notification):
        """ This will not be used, check explanation in the add_or_update_notification method."""
        stmt = SimpleStatement("""
            UPDATE workflows.Notifications 
            SET "status"=%s, "milestoneStepName"=%s, "startTime"=%s, "endTime"=%s 
            WHERE "workflow"=%s AND "step"=%s AND "milestoneName"=%s AND "correlationId"=%s
        """)
        self.session.execute(stmt, [
            notification.status, 
            notification.milestoneStepName, 
            notification.startTime, 
            notification.endTime, 
            notification.workflow, 
            notification.step, 
            notification.milestoneName,
            notification.correlationId
        ])

    def delete_notification(self, notification):
        """ This method deletes a notification based on the composite key. """
        stmt = SimpleStatement("""
            DELETE FROM workflows.Notifications 
            WHERE "correlationId"=%s AND "workflow"=%s AND "step"=%s AND "milestoneName"=%s
        """)
        self.session.execute(stmt, [
            notification.correlationId,
            notification.workflow, 
            notification.step, 
            notification.milestoneName
            ])
    
    def delete_notifications_by_correlationId(self, correlationId):
        """ This method deletes all notifications for a given correlationId. """
        stmt = SimpleStatement("""
            DELETE FROM workflows.Notifications 
            WHERE "correlationId"=%s
        """)
        self.session.execute(stmt, [correlationId])

    def add_or_update_notification(self, notification):
        """ By design, Cassandra performs Upserts. so this stamement will also update
            the record if a record whith such composite key already exists."""
        stmt = SimpleStatement("""
            INSERT INTO workflows.Notifications (
                "correlationId", "workflow", "status", "step", "milestoneName", "milestoneStepName", "startTime", "endTime"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """)
        self.session.execute(stmt, [
            notification.correlationId,
            notification.workflow, 
            notification.status, 
            notification.step, 
            notification.milestoneName, 
            notification.milestoneStepName, 
            notification.startTime, 
            notification.endTime
        ])