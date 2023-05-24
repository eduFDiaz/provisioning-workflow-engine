from cassandra.cluster import Cluster
from config import logger as log
from config import is_running_in_docker

if is_running_in_docker():
    CASSANDRA_URL = ['cassandra']
else:
    CASSANDRA_URL = ['0.0.0.0']

class CassandraConnection:
    def __init__(self):
        self.cluster = Cluster(CASSANDRA_URL, port=9042)
        self.session = self.cluster.connect()
        self.session.execute("CREATE KEYSPACE IF NOT EXISTS workflows WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")
        # self.drop_table() # uncomment this line to drop the notifications table
        self.create_table()

    def get_session(self):
        return self.session

    def close(self):
        self.cluster.shutdown()
    
    def drop_table(self):
        self.session.execute("DROP TABLE IF EXISTS workflows.Notifications;")

    def create_table(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS workflows.Notifications (
                "correlationId" uuid,
                "workflow" text,
                "status" text,
                "step" text,
                "milestoneName" text,
                "milestoneStepName" text,
                "startTime" text,
                "endTime" text,
                PRIMARY KEY ("correlationId", "workflow", "step", "milestoneName")
            );
        """)