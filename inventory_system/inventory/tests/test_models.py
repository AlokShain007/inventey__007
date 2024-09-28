from django.test import TestCase
from inventory.models import Item

class ItemModelTest(TestCase):

    def setUp(self):
        self.item = Item.objects.create(
            name="Laptop",
            description="A high-end gaming laptop"
        )

    def test_item_creation(self):
        self.assertEqual(self.item.name, "Laptop")
        self.assertEqual(self.item.description, "A high-end gaming laptop")

    def test_str_representation(self):
        self.assertEqual(str(self.item), "Laptop")
