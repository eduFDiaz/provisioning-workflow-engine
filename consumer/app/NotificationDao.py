from cassandra.query import SimpleStatement
from NotificationModel import NotificationModel

class NotificationDao:
    def __init__(self, session):
        self.session = session

    def get_notification(self, workflow, step, milestoneName):
        stmt = SimpleStatement("""
            SELECT * 
            FROM workflows.Notifications 
            WHERE workflow=%s AND step=%s AND milestoneName=%s
        """, fetch_size=10)
        notification = self.session.execute(stmt, [workflow, step, milestoneName])
        return NotificationModel(**notification[0])

    def get_all_notifications(self):
        stmt = SimpleStatement("SELECT * FROM workflows.Notifications", fetch_size=10)
        notifications = self.session.execute(stmt)
        return [NotificationModel(**notification) for notification in notifications]

    def update_notification(self, notification):
        stmt = SimpleStatement("""
            UPDATE workflows.Notifications 
            SET status=%s, milestoneStepName=%s, startTime=%s, endTime=%s 
            WHERE workflow=%s AND step=%s AND milestoneName=%s
        """)
        self.session.execute(stmt, [
            notification.status, 
            notification.milestoneStepName, 
            notification.startTime, 
            notification.endTime, 
            notification.workflow, 
            notification.step, 
            notification.milestoneName
        ])

    def delete_notification(self, workflow, step, milestoneName):
        stmt = SimpleStatement("""
            DELETE FROM workflows.Notifications 
            WHERE workflow=%s AND step=%s AND milestoneName=%s
        """)
        self.session.execute(stmt, [workflow, step, milestoneName])

    def add_notification(self, notification):
        stmt = SimpleStatement("""
            INSERT INTO workflows.Notifications (
                workflow, status, step, milestoneName, milestoneStepName, startTime, endTime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """)
        self.session.execute(stmt, [
            notification.workflow, 
            notification.status, 
            notification.step, 
            notification.milestoneName, 
            notification.milestoneStepName, 
            notification.startTime, 
            notification.endTime
        ])