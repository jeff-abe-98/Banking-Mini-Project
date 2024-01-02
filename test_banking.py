import banking.banking
from banking.banking import Bank, SavingsAccount, CheckingAccount, Customer, CreditCard
import pytest


def test_bank():
    bank = Bank('bank test')
    assert bank.name == 'bank test'
    with pytest.raises(ValueError) as execinfo:
        _ = Bank('bank test')
    assert str(execinfo.value) == 'A bank with name bank test already exists'
    

def test_customer():
    bank = Bank('First Bank and Trust')
    bank_name = bank.name
    Jeff = Customer(bank_name, 123456789, 'Jeff', 'Abe', '1234 Main st')
    assert Jeff.fname == "Customer's first name: Jeff"
    with pytest.raises(AttributeError) as execinfo:
        Jeff.fname = 'Jeffrey'
    assert str(execinfo.value) == "can't set attribute"
    Jeff.lname = 'Abraham'
    assert Jeff.lname == "Customer's last name: Abraham"
    assert Jeff.ssn[:-4] == 'xxx-xx-'
    with pytest.raises(ValueError) as execinfo:
        _ = Customer(bank_name, 123456789, 'Jeffrey', 'Abe', '1234 Main st')
    assert str(execinfo.value) == 'A customer already exists with the ssn supplied'
    

def test_savings():
    bank = Bank('Second Bank and Trust')
    bank_name = bank.name
    Jeff = Customer(bank_name, 123456789, 'Jeff', 'Abe', '1234 Main st')
    JeffsSavings = SavingsAccount(bank_name,Jeff.customer_id)
    assert JeffsSavings.balance ==  f'Customer {Jeff.customer_id} Balance is: $500.00'
    assert JeffsSavings.bank_name == bank_name
    assert JeffsSavings.interest_rate == 'Account interest rate is 0.50%'
    with pytest.raises(AttributeError) as execinfo:
        JeffsSavings.interest_rate = 0.1
    assert str(execinfo.value) == "can't set attribute"
    assert JeffsSavings.type == 'Savings Account'


def test_checking():
    bank = Bank('Third Bank and Trust')
    bank_name = bank.name
    Jeff = Customer(bank_name, 123456789, 'Jeff', 'Abe', '1234 Main st')
    JeffsChecking = CheckingAccount(bank_name,Jeff.customer_id)
    assert JeffsChecking.balance == f'Customer {Jeff.customer_id} Balance is: $0.00'
    assert JeffsChecking.bank_name == bank_name
    assert JeffsChecking.overdraft_fee == 'Account overdraft fee is $25.00'
    with pytest.raises(AttributeError) as execinfo:
        JeffsChecking.overdraft_fee = 0
    assert str(execinfo.value) == "can't set attribute"
    with pytest.raises(AttributeError) as execinfo:
        JeffsChecking.overdraft_limit = 0
    assert str(execinfo.value) == "can't set attribute"
    assert JeffsChecking.type == 'Checking Account'


def test_savings_withdraw():
    bank = Bank('Fourth Bank and Trust')
    bank_name = bank.name
    Jeff = Customer(bank_name, 123456789, 'Jeff', 'Abe', '1234 Main st')
    JeffsSavings = SavingsAccount(bank_name,Jeff.customer_id,700)
    JeffsSavings.withdraw(200)
    assert JeffsSavings.balance == f'Customer {Jeff.customer_id} Balance is: $500.00'
    with pytest.raises(ValueError) as execinfo:
        JeffsSavings.withdraw(301)
    assert str(execinfo.value) == f'The account {JeffsSavings._account_id} cannot withstand a withdrawl of $301.00'
    JeffsSavings.deposit(100)
    assert JeffsSavings.balance == f'Customer {Jeff.customer_id} Balance is: $600.00'

def test_checkings_withdraw():
    bank = Bank('Fifth Bank and Trust')
    bank_name = bank.name
    Jeff = Customer(bank_name, 123456789, 'Jeff', 'Abe', '1234 Main st')
    JeffsChecking = CheckingAccount(bank_name,Jeff.customer_id, 150)
    assert JeffsChecking.balance == f'Customer {Jeff.customer_id} Balance is: $150.00'
    with pytest.raises(ValueError) as execinfo:
        JeffsChecking.withdraw(250)
    assert str(execinfo.value) == 'The requested withdrawl brings the account balance below the overdraft limit'
    with pytest.raises(ValueError) as execinfo:
        JeffsChecking.withdraw(225)
    assert str(execinfo.value) == 'The requested withdrawl brings the account balance below the overdraft limit'
    JeffsChecking.withdraw(50)
    assert JeffsChecking.balance == f'Customer {Jeff.customer_id} Balance is: $100.00'
    banking.banking.input = lambda _: 'y'
    JeffsChecking.withdraw(101)
    assert JeffsChecking.balance == f'Customer {Jeff.customer_id} Balance is: -$26.00'
    banking.banking.input = lambda _: 'n'
    JeffsChecking.withdraw(1)
    assert JeffsChecking.balance == f'Customer {Jeff.customer_id} Balance is: -$26.00'
    banking.banking.input = lambda _: 'g'
    with pytest.raises(ValueError) as execinfo:
        JeffsChecking.withdraw(1)
    assert str(execinfo.value) == 'Input must be either a "y" or "n"'
    JeffsChecking.deposit(200)
    JeffsChecking.balance == f'Customer {Jeff.customer_id} Balance is: $174.00'

def test_credit_card():
    bank = Bank('Sixth Bank and Trust')
    bank_name = bank.name
    Jeff = Customer(bank_name, 123456789, 'Jeff', 'Abe', '1234 Main st')
    JeffsChecking = CheckingAccount(bank_name,Jeff.customer_id, 1000)
    JeffsCard = CreditCard(bank_name, Jeff._customer_id)
    JeffsCard.spend(100, JeffsCard.cvv,note='First Purchase')
    with pytest.raises(ValueError) as execinfo:
        JeffsCard.spend(100, JeffsCard.cvv+1)
    assert str(execinfo.value) == 'The CVV supplied does not match, transaction declined'
    assert JeffsCard.current_balance == JeffsCard.statement_balance
    assert JeffsCard.statement_balance == '$100.00'
    assert JeffsChecking.balance  == 'Customer 10001 Balance is: $1,000.00'
    print(CheckingAccount.__ACCOUNTS__)
    JeffsCard.pay(JeffsChecking.account_id,50)
    assert JeffsCard.statement_balance == '$50.00'
    bank.next_month()
    assert JeffsCard.statement_balance == '$0.00'
    assert JeffsCard.current_balance == '$50.00'
    assert JeffsChecking.balance == 'Customer 10001 Balance is: $950.00'
    JeffsCard.spend(150, JeffsCard.cvv)
    bank.next_month()
    assert JeffsCard.statement_balance == '$0.00'
    assert JeffsCard.current_balance == '$201.08'
    with pytest.raises(ValueError) as execinfo:
        JeffsCard.spend(1000, JeffsCard.cvv)
    assert str(execinfo.value) == 'The purchase was declined. It would put your card over its limit, you can spend $798.92 more before maxing out'
    JeffsCard.pay(JeffsChecking.account_id,500)
    assert JeffsCard.statement_balance == '$0.00'
    assert JeffsCard.current_balance == '$0.00'
    assert JeffsChecking.balance == 'Customer 10001 Balance is: $748.92'
    bank.next_month()
    assert JeffsCard.statement_balance == '$0.00'
    assert JeffsCard.current_balance == '$0.00'
