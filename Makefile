# run temporal instance and worker plus backend
docker:
	clear; docker-compose down --volumes; docker-compose up --build
test:
	pytest -v app/tests/test_*.py
	pytest -v app/sandbox.py