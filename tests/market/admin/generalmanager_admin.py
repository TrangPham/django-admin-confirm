from django.contrib.admin import ModelAdmin


class GeneralManagerAdmin(ModelAdmin):
    save_as = True
    search_fields = ["name"]
