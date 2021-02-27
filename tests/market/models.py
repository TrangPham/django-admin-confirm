from django.db import models


class Item(models.Model):
    VALID_CURRENCIES = (
        ("CAD", "CAD"),
        ("USD", "USD"),
    )
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
    shops = models.ManyToManyField(Shop)
    general_manager = models.OneToOneField(
        GeneralManager, on_delete=models.CASCADE, null=True, blank=True
    )
    town = models.ForeignKey(Town, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
