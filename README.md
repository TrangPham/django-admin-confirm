Django Admin Confirm
========

AdminConfirmMixin is a mixin for ModelAdmin to add confirmations to changes and additions.

It can be configured to add a confirmation page upon saving changes and/or additions on ModelAdmin.

Typical Usage:
    
    from admin_confirm import AdminConfirmMixin
    
    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        confirm_change = True
        confirmation_fields = ['field1', 'field2']
       

Installation
------------

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

        
Configuration Options
--------
- `confirm_change` Optional[bool] - decides if changes should trigger confirmation
- `confirm_add` Optional[bool] - decides if additions should trigger confirmation
- `confirmation_fields` Optional[Array[string]] - sets which fields changes/additions should trigger confirmation
- `change_confirmation_template` Optional[string] - path to custom html template to use

Note that setting `confirmation_fields` without setting `confirm_change` or `confirm_add` would not trigger confirmation.

Contribution & Appreciation
----------

Contributions are most welcome :) Feel free to:
- address an issue
- raise an issue
- add more test cases
- add feature requests

Your appreciation is also very welcome :) Feel free to:
- star the project
- open an issue just to share your thanks

Feature List
-------

This is a list of features which could potentially be added in the future.

- global actions on changelist page
- instance actions on change/view page
- confirmations on changelist actions
- run scripts from admin
- completed action summary page
- action logs (adding actions to history of instances)

Support
-------

If you are having issues, please let us know through raising an issue.

License
-------

The project is licensed under the Apache 2.0 license.