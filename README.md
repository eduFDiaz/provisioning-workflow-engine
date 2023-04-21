# python-microservices-sandbox
This will create a Mongodb, Temporal IO, GraphQL, FastAPI sandbox POC development

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

# TODOS
- Refactor code following MVC pattern
- Create a new workflow that uses context and multiple activites
- Update tests for existing workflow