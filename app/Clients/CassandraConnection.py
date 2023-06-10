from cassandra.cluster import Cluster
from config import logger as log
from config import settings

CASSANDRA_URL = [settings.cassandra_server]

class CassandraConnection:
    def __init__(self):
        log.info("CASSANDRA_URL: " + str(CASSANDRA_URL))
        self.cluster = Cluster(CASSANDRA_URL, port=settings.cassandra_port)
        self.session = self.cluster.connect()
        self.session.execute("CREATE KEYSPACE IF NOT EXISTS workflows WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")
        # self.drop_table() # uncomment this line to drop the notifications table
        self.create_table()

    def get_session(self):
        return self.session

    def _del_(self):
        log.info("Shutting down Cassandra connection...")
        self.cluster.shutdown()
    
    def drop_table(self):
        self.session.execute("DROP TABLE IF EXISTS workflows.Notifications;")

    def create_table(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS workflows.Notifications (
                "requestID" uuid,
                "workflow" text,
                "status" text,
                "step" text,
                "milestoneName" text,
                "milestoneStepName" text,
                "startTime" text,
                "endTime" text,
                PRIMARY KEY ("requestID", "workflow", "step", "milestoneName")
            );
        """)