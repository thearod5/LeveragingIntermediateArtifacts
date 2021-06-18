format:
	etracer/venvnv/bin/black src/*.py

lint:
	tracer/venv/bin/pylint src/**/*.py

type:
	tracer/venv/bin/mypy src/*.py

test:
	tracer/venv/bin/nosetests src/tests

start:
	tracer/venv/bin/python3 src/start.py

checklist: format lint type test