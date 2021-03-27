import factory

from random import choice, randint
from django.utils import timezone

from .market.models import Item, Shop, Inventory, Transaction
from .market.constants import VALID_CURRENCIES


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    name = factory.Faker("name")
    price = factory.LazyAttribute(lambda _: randint(5, 500))
    currency = "CAD"


class ShopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shop

    name = factory.Faker("name")


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inventory

    shop = factory.SubFactory(ShopFactory)
    item = factory.SubFactory(ItemFactory)
    quantity = factory.Sequence(lambda n: n)


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    currency = "CAD"
    total = 0
    date = factory.LazyAttribute(lambda _: timezone.now().date())
    timestamp = factory.LazyAttribute(lambda _: timezone.now())
    shop = factory.SubFactory(ShopFactory)
