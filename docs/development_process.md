### Development Setup

**Docker (Recommended)**

Install docker-compose (or Docker Desktop which installs this for you)

```
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
```

You should now be able to see the app running on `localhost:8000`

> Note:
> If you get NoSuchBucket error in the web container, execute `awslocal s3 mb s3://mybucket` in the localstack container and restart web container.

```
docker compose -f docker-compose.dev.yml exec -T localstack awslocal s3 mb s3://mybucket
```

If you haven't already done migrations and created a superuser, you'll want to do it here

```
docker compose -f docker-compose.dev.yml exec web tests/manage.py migrate
docker compose -f docker-compose.dev.yml exec web tests/manage.py createsuperuser
```

**Running tests:**

```
docker compose -f docker-compose.dev.yml exec -T web make test-all
```

The integration tests are set up within docker. I recommend running the integration tests only in docker.

Docker is also set to mirror local folder so that you can edit code/tests and don't have to rebuild to run new code/tests.

Use `docker compose -f docker-compose.dev.yml up -d --force-recreate` if you need to restart the docker containers. For example when updating the docker-compose.yml file, but if you change `Dockerfile` you have to rebuild.

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
To check if the static files have been set up correctly, go to `http://localhost:4566/mybucket/static/admin/css/base.css`

### Release process

Honestly this part is just for my reference. But who knows :) maybe we'll have another maintainer in the future.

1. Update version in `setup.py`
2. Push this branch and dispatch the workflow for `Test Release`

3. Install new version locally
   First you have to uninstall if you used `pip install -e` earlier

   ```
   make install-testpypi VERSION=<VERSION>
   ```

   Add test locally

   ```
   make run
   ```

   If the css is not applied, run:

   ```
   python tests/manage.py collectstatic
   ```

4. Manually smoke check changes

5. Merge the version change into main
6. Then dispatch the workflow for `Publish Release`

To update supported version badges, use <https://shields.io> (Most of these are dynamic though)
