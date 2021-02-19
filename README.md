# Django Admin Confirm

[![PyPI](https://img.shields.io/pypi/v/django-admin-confirm?color=blue)](https://pypi.org/project/django-admin-confirm/) ![Tests Status](https://github.com/TrangPham/django-admin-confirm/actions/workflows/.github/workflows/test.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/TrangPham/django-admin-confirm/badge.svg)](https://coveralls.io/github/TrangPham/django-admin-confirm)

AdminConfirmMixin is a mixin for ModelAdmin to add confirmations to change, add and actions.

![Screenshot of Change Confirmation Page](https://raw.githubusercontent.com/TrangPham/django-admin-confirm/main/screenshot.png)

![Screenshot of Add Confirmation Page](https://raw.githubusercontent.com/TrangPham/django-admin-confirm/main/screenshot_confirm_add.png)

![Screenshot of Action Confirmation Page](https://raw.githubusercontent.com/TrangPham/django-admin-confirm/main/screenshot_confirm_action.png)

It can be configured to add a confirmation page on ModelAdmin upon:

- saving changes
- adding new instances
- performing actions

Typical Usage:

```py
    from admin_confirm import AdminConfirmMixin

    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        confirm_change = True
        confirmation_fields = ['field1', 'field2']
```

## Installation

Install django-admin-confirm by running:

    pip install django-admin-confirm

Add to INSTALLED_APPS in your project settings before `django.contrib.admin`:

    INSTALLED_APPS = [
        ...
        'admin_confirm',

        'django.contrib.admin',
        ...
    ]

Note that this project follows the template override rules of Django.
To override a template, your app should be listed before `admin_confirm` in INSTALLED_APPS.

## Configuration Options

**Attributes:**

- `confirm_change` _Optional[bool]_ - decides if changes should trigger confirmation
- `confirm_add` _Optional[bool]_ - decides if additions should trigger confirmation
- `confirmation_fields` _Optional[Array[string]]_ - sets which fields should trigger confirmation for add/change. For adding new instances, the field would only trigger a confirmation if it's set to a value that's not its default.
- `change_confirmation_template` _Optional[string]_ - path to custom html template to use for change/add
- `action_confirmation_template` _Optional[string]_ - path to custom html template to use for actions

Note that setting `confirmation_fields` without setting `confirm_change` or `confirm_add` would not trigger confirmation for change/add. Confirmations for actions does not use the `confirmation_fields` option.

**Method Overrides:**
If you want even more control over the confirmation, these methods can be overridden:

- `get_confirmation_fields(self, request: HttpRequest, obj: Optional[Object]) -> List[str]`
- `render_change_confirmation(self, request: HttpRequest, context: dict) -> TemplateResponse`
- `render_action_confirmation(self, request: HttpRequest, context: dict) -> TemplateResponse`

## Usage

**Confirm Change:**

```py
    from admin_confirm import AdminConfirmMixin

    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        confirm_change = True
        confirmation_fields = ['field1', 'field2']
```

This would confirm changes on changes that include modifications on`field1` and/or `field2`.

**Confirm Add:**

```py
    from admin_confirm import AdminConfirmMixin

    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        confirm_add = True
        confirmation_fields = ['field1', 'field2']
```

This would confirm add on adds that set `field1` and/or `field2` to a non default value.

Note: `confirmation_fields` apply to both add/change confirmations.

**Confirm Action:**

```py
    from admin_confirm import AdminConfirmMixin

    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        actions = ["action1", "action2"]

        def action1(modeladmin, request, queryset):
            # Do something with the queryset

        @confirm_action
        def action2(modeladmin, request, queryset):
            # Do something with the queryset

        action2.allowed_permissions = ('change',)
```

This would confirm `action2` but not `action1`.

Action confirmation will respect `allowed_permissions` and the `has_xxx_permission` methods.

> Note: AdminConfirmMixin does not confirm any changes on inlines

## Contribution & Appreciation

Contributions are most welcome :) Feel free to:

- address an issue
- raise an issue
- add more test cases
- add feature requests

Your appreciation is also very welcome :) Feel free to:

- star the project
- open an issue just to share your thanks

### Local Development Setup

Install pyenv
Install python 3.8

Create virtualenv via pyenv

```
pyenv vituralenv 3.8 django-admin-confirm-3.8
```

Now your terminal should have `(django-admin-confirm-3.8)` prefix, because `.python-version` should have auto switch your virtual env

Run migrations and create a superuser and run the server

```
./tests/manage.py migrate
./tests/manage.py createsuperuser
./tests/manage.py runserver
```

You should be able to see the test app at `localhost:8000/admin`

Running tests:

```
make test
```

Testing new changes on test project:

```
pip install -e .
make run
```

### Release process

Honestly this part is just for my reference. But who knows :) maybe we'll have another maintainer in the future.

Run tests, check coverage, check readme

```
make test
make check-readme
```

Update version in `setup.py`

```
make package
make upload-testpypi
```

Install new version locally
First you have to uninstall if you used `pip install -e` earlier

```
pip uninstall django_admin_confirm
make install-testpypi
```

Update version in `requirements.txt`
Add test locally

```
make run
```

Go on github and make a release in UI

## Feature List

This is a list of features which could potentially be added in the future. Some of which might make more sense in their own package.

- [x] confirmations on changelist actions
- [ ] confirmations on inlines
- [ ] global actions on changelist page
- [ ] instance actions on change/view page
- [ ] action logs (adding actions to history of instances)
- [ ] add help tooltip/popover to any field for more info
- [ ] add help tooltop/popover/help button to admin actions on changelist
- [ ] run scripts from admin
- [ ] completed action summary page
- [ ] add top and bottom areas to instance pages which can be configured for any content

## Support

If you are having issues, please let us know through raising an issue.

## License

The project is licensed under the Apache 2.0 license.
