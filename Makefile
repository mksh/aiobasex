test:
	docker-compose build test
	docker-compose run test

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
