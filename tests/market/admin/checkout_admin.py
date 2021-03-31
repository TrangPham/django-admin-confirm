from django.core.exceptions import ValidationError
from admin_confirm.admin import AdminConfirmMixin

from django.contrib.admin import ModelAdmin
from django.forms import ModelForm

from ..models import Checkout


class CheckoutForm(ModelForm):
    class Meta:
        model = Checkout
        fields = [
            "currency",
            "shop",
            "total",
            "timestamp",
            "date",
        ]

    def clean_total(self):
        try:
            total = float(self.cleaned_data["total"])
        except:
            raise ValidationError("Invalid Total From clean_total")
        if total == 111:  # Use to cause error in test
            raise ValidationError("Invalid Total 111")

        return total

    def clean(self):
        try:
            total = float(self.data["total"])
        except:
            raise ValidationError("Invalid Total From clean")
        if total == 222:  # Use to cause error in test
            raise ValidationError("Invalid Total 222")

        self.cleaned_data["total"] = total


class CheckoutAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
    autocomplete_fields = ["shop"]
    form = CheckoutForm
