# Testing Documentation/Notes

[![Coverage Status](https://coveralls.io/repos/github/TrangPham/django-admin-confirm/badge.svg)](https://coveralls.io/github/TrangPham/django-admin-confirm)

Hello, friend! You have found the list of test cases that this package can benefit from.

You seem concerned about the stability and reliability of this package. You're probably wondering if you should include it in your production codebase. Well, although I have tried very hard to get 100% code coverage, there are so many permutations of ModelAdmins in the wild. And I'm only one person.

So if you want to include this package in your production codebase, be aware that AdminConfirmMixin works best with simple unmodified ModelAdmins.

## Save Options

- [x] Save
- [x] Conitnue
- [x] Save As New
- [x] Add another

### Field types

- [x] CharField
- [x] PositiveIntegerField
- [x] DecimalField
- [x] TextField
- [x] ImageField
- [x] FileField
- [x] ManyToManyField
- [x] OneToOneField
- [x] ForeignKey

- [x] Custom Readonly fields

### Options

- [x] .exclude
- [x] .fields
- [x] .readonly_fields
- [x] Actions

### Options to test

- [x] ModelAdmin.fieldsets
- [ ] ModelAdmin.form
- [ ] ModelAdmin.raw_id_fields
- [ ] ModelAdmin.radio_fields
- [ ] ModelAdmin.autocomplete_fields
- [ ] ModelAdmin.prepopulated_fields

## ModelAdmin form template overrides?

https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#custom-template-options
(Maybe??? IDK this is esoteric)

## Function overrides to test

- [ ] .save_model()
- [ ] .get_readonly_fields()
- [ ] .get_fields()
- [ ] .get_excludes()
- [ ] .get_form()
- [ ] .get_autocomplete_fields()
- [ ] .get_prepopulated_fields()
- [x] .get_fieldsets()
- [ ] ModelAdmin.formfield_for_manytomany()
- [ ] ModelAdmin.formfield_for_foreignkey()
- [ ] ModelAdmin.formfield_for_choice_field()
- [ ] ModelAdmin.get_changeform_initial_data()

## Inline instance support??

Confirmation on inline changes is not a current feature of this project.

Confirmation on add/change of ModelAdmin that includes inlines needs to be tested. Use AdminConfirmMixin with ModelAdmin containing inlines at your own risk.

- [ ] .inlines
- [ ] .get_inline_instances()
- [ ] .get_inlines() (New in Django 3.0)
- [ ] .get_formsets_with_inlines()

#### Options for inlines

- [ ] classes of inlines: Tabular, Stacked, etc
- [ ] extra
- [ ] action on the inline: add or change
- [ ] clicking add another on the inline

## IDK if we want to support these

- [ ] .get_changelist_form()
- [ ] ModelAdmin.list_editable
- [ ] ModelAdmin.changelist_view()

- [ ] ModelAdmin.add_view(request, form_url='', extra_context=None)
- [ ] ModelAdmin.change_view(request, object_id, form_url='', extra_context=None)

## More tests for these?

Note: Currently the code always calls super().\_changeform_view(), which would ensure permissions correct as well

- [x] ModelAdmin.has_add_permission
- [x] ModelAdmin.has_change_permission
