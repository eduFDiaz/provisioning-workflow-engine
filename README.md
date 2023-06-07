## 1. Start the containers
Start the containers with --build param to reflect frequent changes in the python code

`clear; docker-compose down --volumes; docker-compose up --build`
![alt text](containers.png "Title")

## 2. Wait around 30 seconds
Wait for Cassandra gossip to settle, (around 30 seconds)
![alt text](cassandra.png)

## 3. Launch the UI
After the cassandra role is created launch the UI `http://localhost:4200`

3.1 Hit the start flow button to trigger flow

![Alt text](UI.png)


<!-- # python-microservices-sandbox
This will create a Mongodb, Temporal IO, GraphQL, FastAPI, Memgraph sandbox POC development

## Start the containers
Start the containers with --build param to reflect frequent changes in the python code
`clear; docker-compose down --volumes; docker-compose up --build`
![alt text](containers.png "Title")

## Swagger
Access the swagger endpoint
[http://localhost:8000/docs](http://localhost:8000/docs)

![alt text](swagger.png "Title")

## Graphql
Access the grapql endpoint 
[http://localhost:8000/graphql](http://localhost:8000/graphql), use query below
```
{
  books(author: "F. Scott Fitzgerald", title: "") {
    title
    author
  }
}
```
![alt text](graphql.png "Title")

## Temporal IO test
To test the temporal IO setup use the below endpoint
```
curl -X 'GET' \
  'http://localhost:8000/invokePrimeFlow/5' \
  -H 'accept: application/json'
```
![alt text](prime.png "Title")
Then navigate to the temporal ui to see the flows
http://localhost:8080/namespaces/default/workflows
![alt text](temporal.png "Title")

## Memgraph setup and API end endpoint
Memgraph is graph db that supports Cypher Query Language and is compatible with Neo4j. Memgraph is implented in C++ and runs in memory, making it 120x faster than Neo4j.
![alt text](memgraph.png "Title")
Below is an API endpoint which fetches Book nodes from the memgraph db
![alt text](memgraph-api.png "Title")

## Testing
To run the tests simply run
```
pytest -v app/tests/test_*.py
```
![alt text](tests.png "Title")

## TODO
- Refactor code following MVC pattern using FastAPI Routers
- <s>Create a new workflow that uses context and multiple activites<s>
- <s>Update tests for existing workflow<s>
- <s>Fix test_execute_prime_factorial_workflow<s>
- <s>Add Neo4j database and API endpoint<s> -->
