run:
	./tests/manage.py runserver

test:
	coverage run --branch -m pytest
	coverage html
	coverage-badge -f -o coverage.svg
	python -m readme_renderer README.md -o /tmp/README.html

check-readme:
	python -m readme_renderer README.md -o /tmp/README.html

migrate:
	./tests/manage.py makemigrations
	./tests/manage.py migrate

shell:
	./tests/manage.py shell

package:
	python3 setup.py sdist bdist_wheel

upload-testpypi:
	python3 -m twine upload --repository testpypi dist/*
