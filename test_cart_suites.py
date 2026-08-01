from testify import TestCase, setup, teardown, assert_equal, suite

class ShoppingCartTest(TestCase):

    @setup
    def setup_cart(self):
        self.cart = []

    @suite('fast')
    @suite('unit')
    @suite('cart')
    def test_add_item(self):
        self.cart.append("laptop")
        assert_equal(len(self.cart), 1)

    @suite('slow')
    @suite('integration')
    def test_checkout_payment_gateway(self):
        # Simulates external payment network call
        pass