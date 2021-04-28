run:
	./tests/manage.py runserver

test:
	coverage run --source admin_confirm --branch -m pytest --ignore=admin_confirm/tests/integration
	coverage report -m

test-all:
	coverage run --source admin_confirm --branch -m pytest
	coverage report -m

t:
	python -m pytest --last-failed -x

test-integration:
	coverage run --source admin_confirm --branch -m pytest --ignore=admin_confirm/tests/unit

docker-exec:
	docker-compose exec -T web ${COMMAND}

check-readme:
	python -m readme_renderer README.md -o /tmp/README.html

migrate:
	./tests/manage.py makemigrations
	./tests/manage.py migrate

shell:
	./tests/manage.py shell

dbshell:
	./tests/manage.py dbshell

package:
	python3 setup.py sdist bdist_wheel

upload-testpypi:
	python3 -m twine upload --repository testpypi dist/django_admin_confirm-$(VERSION)-*

i-have-tested-with-testpypi-and-am-ready-to-release:
	python3 -m twine upload --repository pypi dist/django_admin_confirm-$(VERSION)-*

install-testpypi:
	pip uninstall django_admin_confirm
	python -m pip install --index-url https://test.pypi.org/simple/ django_admin_confirm==${VERSION}

testpypi:
	python3 -m twine upload --repository testpypi dist/django_admin_confirm-$(VERSION)*
	pip uninstall django_admin_confirm
	python -m pip install --index-url https://test.pypi.org/simple/ django_admin_confirm==${VERSION}
