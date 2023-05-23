# from cassandra.cluster import Cluster

# cluster = Cluster(['0.0.0.0'], port=9042)
# session = cluster.connect()
# # session.execute("CREATE KEYSPACE IF NOT EXISTS test WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")  
# # session.execute("""CREATE TABLE IF NOT EXISTS test.test (id int PRIMARY KEY, name text);""")

# # prepared_statement = session.prepare("INSERT INTO test.test (id, name) VALUES (?,?);")
# # for i in range(11,20):
# #     session.execute(prepared_statement, (i, 'test' + str(i)))

# rows = session.execute("SELECT * FROM test.test;")
# # for row in rows:
# print(len(rows.current_rows))


from CassandraConnection import CassandraConnection
from NotificationDao import NotificationDao
from NotificationModel import NotificationModel

def main():
    cassandra_nodes = ['0.0.0.0']
    connection = CassandraConnection(cassandra_nodes)
    session = connection.get_session()

    notification_dao = NotificationDao(session)

    # Use the DAO
    # Adding a notification
    new_notification = NotificationModel(
        workflow="workflow1", 
        status="status1", 
        step="step1", 
        milestoneName="milestoneName1", 
        milestoneStepName="milestoneStepName1", 
        startTime="startTime1", 
        endTime="endTime1"
    )
    notification_dao.add_notification(new_notification)

    # Getting a notification
    notification = notification_dao.get_notification("workflow1", "step1", "milestoneName1")
    print(notification.toJSON())

    # Getting all notifications
    notifications = notification_dao.get_all_notifications()
    for notification in notifications:
        print(notification.toJSON())

    # Updating a notification
    updated_notification = NotificationModel(
        workflow="workflow1", 
        status="updated_status", 
        step="step1", 
        milestoneName="milestoneName1", 
        milestoneStepName="updated_milestoneStepName", 
        startTime="updated_startTime", 
        endTime="updated_endTime"
    )
    notification_dao.update_notification(updated_notification)

    # Deleting a notification
    notification_dao.delete_notification("workflow1", "step1", "milestoneName1")

    # Closing connection
    connection.close()

if __name__ == "__main__":
    main()