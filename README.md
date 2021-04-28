# Django Admin Confirm

[![PyPI](https://img.shields.io/pypi/v/django-admin-confirm?color=blue)](https://pypi.org/project/django-admin-confirm/) ![Tests Status](https://github.com/TrangPham/django-admin-confirm/actions/workflows/.github/workflows/test.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/TrangPham/django-admin-confirm/badge.svg)](https://coveralls.io/github/TrangPham/django-admin-confirm)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-admin-confirm) ![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-admin-confirm)
![PyPI - License](https://img.shields.io/pypi/l/django_admin_confirm) ![Status](https://img.shields.io/badge/status-alpha-yellow)

AdminConfirmMixin is a mixin for ModelAdmin to add confirmations to change, add and actions.

![Screenshot of Change Confirmation Page](https://raw.githubusercontent.com/TrangPham/django-admin-confirm/302e02b1e483fd41e9a6f0b6803b45cd34c866cf/screenshot.png)

![Screenshot of Add Confirmation Page](https://raw.githubusercontent.com/TrangPham/django-admin-confirm/302e02b1e483fd41e9a6f0b6803b45cd34c866cf/screenshot_confirm_add.png)

![Screenshot of Action Confirmation Page](https://raw.githubusercontent.com/TrangPham/django-admin-confirm/302e02b1e483fd41e9a6f0b6803b45cd34c866cf/screenshot_confirm_action.png)

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

## Disclaimer

Be aware that not all possible combinations of ModelAdmin have been tested, even if test coverage is high.

See [testing readme](docs/testing_notes.md) for more details

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

**Environment Variables**:

Caching is used to cache files for confirmation. When change/add is submitted on the ModelAdmin, if confirmation is required, files will be cached until all validations pass and confirmation is received.

- `ADMIN_CONFIRM_CACHE_TIMEOUT` _default: 1000_
- `ADMIN_CONFIRM_CACHE_KEY_PREFIX` _default: admin_confirm\_\_file_cache_

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

Check out our [development process](docs/development_process.md) if you're interested.

## Support

If you are having issues, please let us know through raising an issue.

## License

The project is licensed under the Apache 2.0 license.
