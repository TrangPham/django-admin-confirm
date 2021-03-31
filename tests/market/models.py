from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db.models.aggregates import Sum
from django.db import models
from .constants import VALID_CURRENCIES
from .validators import validate_currency


class Item(models.Model):
    # Because I'm lazy and don't want to update all test references
    VALID_CURRENCIES = VALID_CURRENCIES

    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=3, choices=VALID_CURRENCIES)
    image = models.ImageField(upload_to="tmp/items", null=True, blank=True)
    file = models.FileField(upload_to="tmp/files", null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return str(self.name)


class Inventory(models.Model):
    class Meta:
        unique_together = ["shop", "item"]
        ordering = ["shop", "item__name"]
        verbose_name_plural = "Inventory"

    shop = models.ForeignKey(
        to=Shop, on_delete=models.CASCADE, related_name="inventory"
    )
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    notes = models.TextField(default="This is the default", null=True, blank=True)


class GeneralManager(models.Model):
    name = models.CharField(max_length=120)
    headshot = models.ImageField(upload_to="tmp/gm/headshots", null=True, blank=True)


class Town(models.Model):
    name = models.CharField(max_length=120)


class ShoppingMall(models.Model):
    name = models.CharField(max_length=120)
    shops = models.ManyToManyField(Shop, blank=True, null=True)
    general_manager = models.OneToOneField(
        GeneralManager, on_delete=models.CASCADE, null=True, blank=True
    )
    town = models.ForeignKey(Town, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=VALID_CURRENCIES)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_created=True)
    date = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ItemSale(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="item_sales"
    )
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=5, validators=[validate_currency])

    def clean(self):
        errors = {}
        # check that shop has the stock
        shop = self.transaction.shop
        inventory = Inventory.objects.filter(shop=shop, item=self.item)
        if not inventory:
            errors["item"] = "Shop does not have the item stocked"
        else:
            in_stock = inventory.aggregate(Sum("quantity")).get("quantity__sum", 0)
            if in_stock < self.quantity:
                errors["item"] = "Shop does not have enough of the item stocked"
        if errors:
            raise ValidationError(errors)


class Checkout(Transaction):
    """
    Proxy Model to use in Django Admin to create a Transaction
    As if a customer was checking out at a physical checkout
    """

    class Meta:
        proxy = True
