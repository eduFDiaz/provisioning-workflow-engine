from cassandra.cluster import Cluster

class CassandraConnection:
    def __init__(self, nodes):
        self.cluster = Cluster(nodes, port=9042)
        self.session = self.cluster.connect()
        self.session.execute("CREATE KEYSPACE IF NOT EXISTS workflows WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")
        self.create_table()

    def get_session(self):
        return self.session

    def close(self):
        self.cluster.shutdown()

    def create_table(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS workflows.Notifications (
                workflow text,
                status text,
                step text,
                milestoneName text,
                milestoneStepName text,
                startTime text,
                endTime text,
                PRIMARY KEY (workflow, step, milestoneName)
            );
        """)