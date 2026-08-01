from testify import TestCase, assert_equal, assert_raises, setup

class BankAccount:
    def __init__(self, balance: float):
        self.balance = balance
    
    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        return self.balance
    
class BankAccountTest(TestCase):
    @setup
    def create_account(self):
        self.account = BankAccount(balance=100.0)
    
    def test_sucess_withdraw(self):
        remain_bal = self.account.withdraw(40.0)
        assert_equal(remain_bal, 60.0)
    
    def test_overdraw(self):
        with assert_raises(ValueError):
            self.account.withdraw(150)
    