from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from config import logger as log
# from config import is_running_in_docker
from config import settings
import asyncio

class CassandraConnection:
    def __init__(self):
        log.info("CASSANDRA_URL: " + settings.cassandra_host)
        auth_provider = PlainTextAuthProvider(settings.cassandra_user, settings.cassandra_password)
        while True:
            try:
                self.cluster = Cluster([settings.cassandra_host], port=settings.cassandra_port, auth_provider=auth_provider)
                self.session = self.cluster.connect()
                self.session.execute("CREATE KEYSPACE IF NOT EXISTS workflows WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")
                # self.drop_tables() # uncomment this line to drop the notifications table
                self.create_tables()
                break
            except Exception as e:
                log.debug(f"Failed to connect to Cassandra server due to {str(e)}, retrying in 5 seconds...")
                asyncio.sleep(5)        

    def get_session(self):
        return self.session

    def _del_(self):
        log.info("Shutting down Cassandra connection...")
        self.cluster.shutdown()
    
    def drop_tables(self):
        self.session.execute("DROP TABLE IF EXISTS workflows.Notifications;")
        self.session.execute("DROP TABLE IF EXISTS workflows.Errors;")

    def create_tables(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS workflows.Notifications (
                "correlationID" uuid,
                "workflow" text,
                "status" text,
                "step" text,
                "milestoneName" text,
                "milestoneStepName" text,
                "startTime" text,
                "endTime" text,
                PRIMARY KEY ("correlationID", "workflow", "step", "milestoneName")
            );
        """)
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS workflows.Errors (
                "correlationID" uuid,
                "timeStamp" text,
                "error" text,
                PRIMARY KEY ("correlationID", "timeStamp", "error")
            );
        """)