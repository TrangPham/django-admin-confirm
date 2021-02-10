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
	ifndef VERSION
		$(error VERSION is not set)
	endif
	python3 -m twine upload --repository testpypi dist/django_admin_confirm-$(VERSION)*

i-have-tested-with-testpypi-and-am-ready-to-release:
	ifndef VERSION
		$(error VERSION is not set)
	endif
	python3 -m twine upload --repository pypi dist/django_admin_confirm-$(VERSION)*

install-testpypi:
	python -m pip install --index-url https://test.pypi.org/simple/ django_admin_confirm
