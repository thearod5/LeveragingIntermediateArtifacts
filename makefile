format:
	env/bin/black src/*.py

lint:
	env/bin/pylint src/*.py

type:
	env/bin/mypy src/*.py

test:
	env/bin/nosetests src/tests

checklist: format lint type test