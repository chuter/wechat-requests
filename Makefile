.PHONY: test
init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
test:
	# This runs all of the tests, on both Python 2 and Python 3.
	detox

test-readme:
	@pipenv run python setup.py check --restructuredtext --strict && ([ $$? -eq 0 ] && echo "README.rst ok") || echo "Invalid markup in README.rst!"

flake8:
	pipenv run flake8 .

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml tests

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist
	twine upload dist/*
	rm -fr build dist .egg
