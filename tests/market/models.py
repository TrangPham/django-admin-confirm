from django.db import models


class Item(models.Model):
    VALID_CURRENCIES = (
        ("CAD", "CAD"),
        ("USD", "USD"),
    )
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=3, choices=VALID_CURRENCIES)

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


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


class ShoppingMall(models.Model):
    name = models.CharField(max_length=120)
    shops = models.ManyToManyField(Shop)

    def __str__(self):
        return self.name
