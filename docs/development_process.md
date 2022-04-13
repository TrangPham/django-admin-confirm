### Local Development Setup

**Local:**
_You can skip this and just use docker if you want_

_NOTE: as of 2022-04-12 I don't know if 3.8.0 works anymore if you're on newer versions of macOS. See: https://github.com/pyenv/pyenv/issues/2143#issuecomment-1072032647 You can try using another version of python locally or use docker_

Install pyenv
pyenv install 3.8.0

Create **virtualenv** via pyenv

```
pyenv virtualenv 3.8.0 django-admin-confirm-3.8.0
```

Now your terminal should have `(django-admin-confirm-3.8.0)` prefix, because `.python-version` should have auto switch your virtual env

Install requirements

```
pip install -r requirements.txt
pip install -e .
```

Run **migrations** and create a superuser and run the server

```
./tests/manage.py migrate
./tests/manage.py createsuperuser
./tests/manage.py runserver
```

You should be able to see the test app at `localhost:8000/admin`

**Running tests:**

```sh
make test # Runs unit tests with coverage locally without integration tests
make test-all # Runs unit tests + integration tests, requires extra setup to run locally
```

Use `python -m pytest` if you want to pass in arguments

`make t` is a short cut to run without coverage, last-failed, and fail fast

Testing local changes on test project:

```
pip install -e .
make run
```

**Debugging**:

There's a environment variable `ADMIN_CONFIRM_DEBUG` which when set to true will print to stdout the messages that are sent to `log`.

The test project already has this set to true.

Example:

```py
from admin_confirm.utils import log

log('Message to send to stdout')
```

**Localstack**:
Localstack is used for integration testing and also in the test project.

To check if localstack is running correctly, go to `http://localhost:4566`
To check if the bucket has been set up correctly, go to `http://localhost:4566/mybucket`
To check if the static files have been set up correctly, go to `http://localhost:4566/mybucket/`

**Docker:**

Instead of local set-up, you can also use docker. You may have to delete `.python-version` to do this.

Install docker-compose (or Docker Desktop which installs this for you)

```
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

You should now be able to see the app running on `localhost:8000`

If you haven't already done migrations and created a superuser, you'll want to do it here

```
docker-compose -f docker-compose.dev.yml exec web tests/manage.py migrate
docker-compose -f docker-compose.dev.yml exec web tests/manage.py createsuperuser
```

Running tests in docker:

```
docker-compose -f docker-compose.dev.yml exec -T web make test-all
```

The integration tests are set up within docker. I recommend running the integration tests only in docker.

Docker is also set to mirror local folder so that you can edit code/tests and don't have to rebuild to run new code/tests.

Use `docker-compose -f docker-compose.dev.yml up -d --force-recreate` if you need to restart the docker containers. For example when updating the docker-compose.yml file, but if you change `Dockerfile` you have to rebuild.

### Release process

Honestly this part is just for my reference. But who knows :) maybe we'll have another maintainer in the future.

Run tests, check coverage, check readme

```
docker-compose -f docker-compose.dev.yml exec -T web make test-all
make check-readme
```

Update version in `setup.py`

```
make package
make upload-testpypi VERSION=<VERSION>
```

Install new version locally
First you have to uninstall if you used `pip install -e` earlier

```
pip uninstall django_admin_confirm
make install-testpypi VERSION=<VERSION>
```

Add test locally

```
make run
```

Go on github and make a release in UI
