from django.test import TestCase
from inventory.serializers import ItemSerializer
from inventory.models import Item

class ItemSerializerTest(TestCase):

    def setUp(self):
        self.item_data = {
            'name': 'Phone',
            'description': 'Smartphone with 5G'
        }
        self.serializer = ItemSerializer(data=self.item_data)

    def test_serializer_valid(self):
        self.assertTrue(self.serializer.is_valid())

    def test_serializer_data(self):
        item = Item.objects.create(**self.item_data)
        serializer = ItemSerializer(item)
        self.assertEqual(serializer.data['name'], 'Phone')
        self.assertEqual(serializer.data['description'], 'Smartphone with 5G')
