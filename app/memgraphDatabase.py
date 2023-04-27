from gqlalchemy import Memgraph
from gqlalchemy.models import Node
from config import logger as log
from config import settings as config

class MemGraphDB:
    _instance = None

    @staticmethod
    def get_instance(host=None, port=None):
        if MemGraphDB._instance is None:
            if host is None or port is None:
                raise ValueError("Host and port must be provided for the first instance creation.")
            MemGraphDB._instance = MemGraphDB(host, port)
        return MemGraphDB._instance

    def __init__(self, host, port):
        if MemGraphDB._instance is not None:
            raise Exception("This class is a singleton! Use 'get_instance()' to access it.")
        self.driver = Memgraph(host=host, port=port)
        self._clean_db()

    def exec(self, query):
        log.info("exec query\n " + query)
        results = self.driver.exec(query)
        return list(results)

    def execute_and_fetch(self, query):
        log.info("exec_and_fetch query\n " + query)
        results = self.driver.execute_and_fetch(query)
        return list(results)
    
    def serialize_results_to_json(self, results):
        json_results = []
        for result in results:
            json_result = {}
            node = result['result']
            if isinstance(node, Node):
                json_result['id'] = node._id
                json_result['labels'] = [node._labels]
                for key, value in node._properties.items():
                    json_result[key] = value
            json_results.append(json_result)
        return json_results

    def _clean_db(self):
        log.info("cleaning db and adding test data")
        self.driver.execute("MATCH (n) DETACH DELETE n")
        self.driver.execute("""CREATE (b1:Book {title: 'To Kill a Mockingbird', isbn: '978-0060935467'})
                               CREATE (b2:Book {title: '1984', isbn: '978-0451524935'})
                               CREATE (b3:Book {title: 'Animal Farm', isbn: '978-0451526342'})
                               CREATE (b4:Book {title: 'Pride and Prejudice', isbn: '978-1503290563'})
                               CREATE (b5:Book {title: 'Sense and Sensibility', isbn: '978-1503290525'})

                               CREATE (a1:Author {name: 'Harper Lee', birth_year: 1926})
                               CREATE (a2:Author {name: 'George Orwell', birth_year: 1903})
                               CREATE (a3:Author {name: 'Jane Austen', birth_year: 1775})

                               CREATE (g1:Genre {name: 'Dystopian'})
                               CREATE (g2:Genre {name: 'Classic Fiction'})

                               CREATE (a1)-[:WROTE]->(b1)
                               CREATE (a2)-[:WROTE]->(b2)
                               CREATE (a2)-[:WROTE]->(b3)
                               CREATE (a3)-[:WROTE]->(b4)
                               CREATE (a3)-[:WROTE]->(b5)

                               CREATE (b1)-[:BELONGS_TO]->(g2)
                               CREATE (b2)-[:BELONGS_TO]->(g1)
                               CREATE (b3)-[:BELONGS_TO]->(g1)
                               CREATE (b4)-[:BELONGS_TO]->(g2)
                               CREATE (b5)-[:BELONGS_TO]->(g2)""")

memgraphdb = MemGraphDB.get_instance(config.memgraph_host, config.memgraph_port)

# booksQuery = """MATCH (n:Book)
#            RETURN n as result"""
# results = memgraphdb.execute_and_fetch(booksQuery)

# results = memgraphdb.serialize_results_to_json(results)
# [print(result) for result in results]

# booksQueryAndAuthors = """MATCH (a:Author)-[:WROTE]->(b:Book {title: titleValue})
#                           RETURN a as result""".replace("titleValue", "'1984'")
# results = memgraphdb.execute_and_fetch(booksQueryAndAuthors)
# results = memgraphdb.serialize_results_to_json(results)

# [print(result) for result in results]