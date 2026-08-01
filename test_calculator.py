from testify import TestCase, assert_equal

class CalculatorTest(TestCase):

    def test_addition(self):
        result = 2 + 3
        assert_equal(result, 5)