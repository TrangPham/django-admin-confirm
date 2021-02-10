run:
	./tests/manage.py runserver

test:
	coverage run --source admin_confirm --branch -m pytest
	coverage html
	coverage-badge -f -o coverage.svg

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
	python3 -m twine upload --repository testpypi dist/django_admin_confirm-$(VERSION)*

i-have-tested-with-testpypi-and-am-ready-to-release:
	python3 -m twine upload --repository pypi dist/django_admin_confirm-$(VERSION)*
