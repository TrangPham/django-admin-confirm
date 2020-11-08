import factory

from random import choice, randint

from tests.market.models import Item, Shop, Inventory


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    name = factory.Faker("name")
    price = factory.LazyAttribute(lambda _: randint(5, 500))
    currency = factory.LazyAttribute(lambda _: choice(Item.VALID_CURRENCIES))


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
