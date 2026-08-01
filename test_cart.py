from testify import TestCase, assert_equal, setup, teardown

class ShoppingCart:
    def __init__(self):
        self.items = []
    def add_item(self, item: str):
        self.items.append(item)
    def clear(self):
        self.items = []
    
class ShoppingCartTest(TestCase):
    @setup
    def prepare_cart(self):
        self.cart=ShoppingCart()
        self.cart.add_item("Laptop")

    @teardown
    def cleanup_cart(self):
        self.cart.clear()
    def test_initial_item_count(self):
        assert_equal(len(self.cart.items), 1)
    
    def test_adding_second_item(self):
        self.cart.add_item("Mouse")
        assert_equal(len(self.cart.items), 2)

        