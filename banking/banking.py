import os
import json
import pathlib
from functools import wraps
import logging
from random import randint
import numpy as np


#Setting file path globally
file_path = pathlib.Path.home()/'Desktop'/'Springboard Bootcamp'/'Banking Mini Project'/'data'


#Setting up local file logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pathlib.Path.touch(file_path.parent/'logs'/'banking.log')

loghandler = logging.FileHandler(file_path.parent/'logs'/'banking.log')
loghandler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
loghandler.setFormatter(formatter)

logger.addHandler(loghandler)


def json_load(file):
    '''
    Loads json file at the file path, and returns in dict form

    Args:
        file (obj) : pathlib Path object of file location

    Returns:
        dict: loaded json data

    '''
    if file not in file_path.glob('*.json'):
        logging.error(ValueError(f'A bank with name {file.stem} does not exist'))
        raise ValueError(f'A bank with name {file.stem} does not exist')
    with file.open('r') as f:
        data = json.load(f) 
    return data

def json_write(file, data):
    '''
    Writes contents of {data} to the json file at {file}

    Args:
        file (obj) : pathlib Path object of file location
        data (dict): data to be loaded
    '''
    with file.open('w') as f:
        f.seek(0)
        f.truncate()
        json.dump(data, f)
        


class Bank:
    '''
    Bank, opens a file to store all the banks information

    Attributes:
        name (str)       : The name of the bank
        __BANKS__ (list) : A list containing all bank objects

    Methods:
        name : gets name
        file : gets file path
        next_month : applys interest to all savings accounts and credit cards within the bank
    '''
    __BANKS__ = []
    def __init__(self, name):
        '''
        Bank object initialization function

        Args:
            name (str) : the name of the bank
        
        Returns:
            Bank Class Object
        '''
        self._name = name
        self._file = file_path/f'{self._name}.json'
        if self._file not in file_path.glob('*.json'):
            data = {'Bank Name':self._name, 'Customers':[], 'Accounts':[], 'Credit Cards':[], 'Loans':[]}

            self._file.touch()
            with self._file.open('w') as f:
                json.dump(data, f)
        else:
            logging.error(ValueError(f'A bank with name {self._name} already exists'))
            raise ValueError(f'A bank with name {self._name} already exists')
        logger.info(f'Bank Created with the name {self._name} and database file at {self._file}')
        Bank.__BANKS__.append(self)
        
    @property
    def name(self):
        '''get name'''
        return self._name
    @property
    def file(self):
        '''get file path'''
        f'{self._name} data file is located at {self._file}'
    
    def next_month(self):
        '''
        Applys interest to all savings accounts and credit cards within the bank by calling their own next_month() method
        '''
        for acct in SavingsAccount.__ACCOUNTS__:
            if acct._bank_name == self._name:
                acct.next_month()
        for card in CreditCard.__CARDS__:
            if card._bank_name == self._name:
                card.next_month() 
            
                
    def __del__(self):
        '''
        Deletes all objects associated with this bank object
        '''
        for customer in Customer.__CUSTOMERS__:
            if customer._bank_name == self._name:
                del customer
        for account in CheckingAccount.__ACCOUNTS__:
            if account._bank_name == self._name:
                del account
        for account in SavingsAccount.__ACCOUNTS__:
            if account._bank_name == self._name:
                del account
        for card in CreditCard.__CARDS__:
            if card._bank_name == self._name:
                del card
        Bank.__BANKS__.remove(self)
        os.remove(self._file)


class Customer:
    '''
    Creates a customer of the bank with the bank name supplied, and an interface for that customer to interact with the bank

    Attributes:
        bank_name (str): The name of the bank where a customer 
        ssn (int): Social Security number of customer (e.g. 123456789)
        fname (str): First name of the customer
        lname (str): Last name of the customer
        address (str): Full address of the customer e.g. (1234 main street, New York NY 12345)

    Methods:

    '''
    __CUSTOMERS__ = []
    def __init__(self, bank_name, ssn, fname, lname, address):
        '''
        Customer object initialization function

        Args:
            bank_name (str): The name of the bank where a customer 
            ssn (int): Social Security number of customer (e.g. 123456789)
            fname (str): First name of the customer
            lname (str): Last name of the customer
            address (str): Full address of the customer e.g. (1234 main street, New York NY 12345)
        
        Returns:
            Customer Class Object
        '''
        if len(str(ssn)) != 9 or type(ssn) is not int:
            logging.error(ValueError(f'{ssn} is not a valid social security number input'))
            raise ValueError(f'{ssn} is not a valid social security number input')

        for field in [fname, lname, address]:
            if type(field) is not str:
                logging.error(ValueError(f'{field} must be a string'))
                raise ValueError(f'{field} must be a string') 
        
        self._bank_name = bank_name
        self._ssn = ssn
        self._fname = fname
        self._lname = lname
        self._address = address

        #Input validation
        self._file = file_path/f'{self._bank_name}.json'
        data = json_load(self._file)
        
        #Creating a new customer in the database if they are not already present
        existing_ssn = {cust['SSN'] for cust in data['Customers']}
        cust_ids = {cust['Customer Id'] for cust in data['Customers']}
        if ssn in existing_ssn:
            logging.error(ValueError(f'A customer already exists with the ssn supplied'))
            raise ValueError(f'A customer already exists with the ssn supplied')
        else:
            try: 
                new_id = max(cust_ids)+1
            except ValueError as e:
                logging.error(e)
                new_id = 10001
            self._customer_id = new_id
            data['Customers'].append({
                                    'Customer Id':new_id,
                                    'SSN':ssn, 
                                    'First Name':fname, 
                                    'Last Name':lname,
                                    'Address':address
                                    })
            
            json_write(self._file, data)
            logger.info(f'Customer created at {self._bank_name} for {self._fname} {self._lname} with an customer id of {self._customer_id}')
            print(f'Welcome {self._fname} {self._lname} to {self._bank_name}!! Your customer id is {self._customer_id}')
            Customer.__CUSTOMERS__.append(self)

    @property
    def bank_name(self):
        '''Gets bank name'''
        return self._bank_name
    @property
    def customer_id(self):
        '''Gets customer id'''
        return self._customer_id
    @property
    def ssn(self):
        '''Gets masked ssn'''
        return f'xxx-xx-{str(self._ssn)[-4:]}'
    @property 
    def fname(self):
        '''Gets first name'''
        return f"Customer's first name: {self._fname}"
    @property
    def lname(self):
        '''Gets last name'''
        return f"Customer's last name: {self._lname}"
    @lname.setter
    def lname(self, new_name):
        '''Sets last name and updates bank database'''
        self._lname = new_name
        data = json_load(self._file)
        (cust.update('Last Name', new_name) for cust in data['Customers'] if cust['Customer Id'] == self._customer_id)
        json_write(self._file, data)

        logger.info(f'Customer with id {self._customer_id} changed their lastname to {self._lname}')
    @property
    def address(self):
        '''Gets address'''
        return f"Customer's last name: {self._address}"
    @address.setter
    def address(self, new_address):
        '''Sets address and updates bank database'''
        self._address = new_address
        data = json_load(self._file)
        (cust.update('Address', new_address) for cust in data['Customers'] if cust['Customer Id'] == self._customer_id)
        json_write(self._file, data)
        
        logger.info(f'Customer with id {self._customer_id} changed their address to {self._address}')
    
    @property
    def file(self):
        '''Gets file location'''
        return f'{self._bank_name} data file is located at {self._file}'
    
    def __del__(self):
        '''Deletes customer object and its references from the bank database'''
        try:
            Customer.__CUSTOMERS__.remove(self)
            data = json_load(self._file)
            (data['Customers'].remove(cust) for cust in data['Customers'] if cust['Customer Id'] == self._customer_id)
            accounts = [account['Account Id'] for account in data['Accounts'] if account['Customer Id'] == self._customer_id]
            json_write(self._file, data)
            print(f'Customer {self._fname} {self._lname} removed from the bank database')
            print(f'{len(accounts)} Accounts remain open with Account Ids {accounts}') if len(accounts) > 0 else print(f'Customer had no Accounts remaining with {self._bank_name}')
        except ValueError:
            pass
        
            


class Account:
    '''
    Base class that is used for children Savings Account and Checking Account

    Attributes:
        bank_name (str): The name of the bank where a customer 
        customer_id (int): Customer Id
        starting_balance (float, optional): The starting balance of the account, defaults to 0

    Methods:
        deposit : Deposits into the account
    '''
    def __new__(cls, *args, **kwargs):
        '''Raises an error if this calss is called directly'''
        if cls is Account:
            logger.error(TypeError(f"only children of '{cls.__name__}' may be instantiated"))
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)
    
    def __init__(self, bank_name, customer_id, starting_balance = 0):
        '''
        Account object initialization function
        '''
        self._bank_name = bank_name
        self._customer_id = customer_id
        self._balance = starting_balance

        self._file = file_path/f'{self._bank_name}.json'
        data = json_load(self._file)

        acct_ids = {acct['Account Id'] for acct in data['Accounts']}
        try: 
            new_id = max(acct_ids)+1
        except ValueError:
            new_id = 90001
        self._account_id = new_id

        data['Accounts'].append({
                                'Account Id':new_id,
                                'Customer Id': self._customer_id,
                                'Balance':starting_balance, 
                                })
        
        json_write(self._file, data)
    
    @property
    def bank_name(self):
        '''Gets bank name'''
        return self._bank_name
    @property
    def customer_id(self):
        '''Gets customer id'''
        return self._customer_id
    @property
    def account_id(self):
        '''Gets account id'''
        return self._account_id
    @property
    def balance(self):
        '''Gets account balance'''
        return 'Customer {} Balance is: {}${:0,.2f}'.format(self._customer_id,'-' if self._balance < 0 else '', abs(self._balance))
    @balance.setter
    def balance(self, new_balance):
        '''sets account balance and updates the bank database'''
        self._balance = new_balance

        data = json_load(self._file)
        (acct.update('Balance', new_balance) for acct in data['Accounts'] if acct['Account Id'] == self._account_id)
        json_write(self._file, data)
        
        logger.info(f'Account with id {self._account_id} has a new balance of {self._balance}')
    @property
    def file(self):
        '''Gets file location'''
        return f'{self._bank_name} data file is located at {self._file}'
    
    def __str__(self):
        '''Returns a string representation of the account'''
        return 'Customer {} Account {} with a balance of {}{:0,.2f}'.format(self._customer_id, self._account_id,'-' if self._balance < 0 else '',abs(self._balance))
    
    def deposit(self, amount):
        '''
        Deposits the amount specified

        Args:
            amount (float): The amount to be deposited from the account

        Returns:
            None
        '''
        logger.info('Customer with id {} has deposited ${:0,.2f}'.format(self._customer_id, amount))
        self._balance += amount
        print(self)

        




class SavingsAccount(Account):
    '''
    Creates a customers savings account and holds methods related to savings accounts

    Attributes:
        bank_name (str): The name of the bank where a customer 
        customer_id (int): Customer Id
        starting_balance (float, optional): The starting balance of the account, defaults to 500
        minimum_balance (float, optional): The minimum balance for the account, defaults to 500
        interest_rate (float, optional): The interest rate for the account, defaults to 0.005 or 0.5%

    Methods:

    '''
    __ACCOUNTS__ = []

    def __init__(self, bank_name, customer_id, starting_balance=500, minimum_balance=500, interest_rate=0.005):
        '''
        SavingsAccount object initialization function

        Args:
            bank_name (str): The name of the bank where a customer 
            customer_id (int): Customer Id
            starting_balance (float, optional): The starting balance of the account, defaults to 500
            minimum_balance (float, optional): The minimum balance for the account, defaults to 500
            interest_rate (float, optional): The interest rate for the account, defaults to 0.005 or 0.5%
        '''
        Account.__init__(self, bank_name, customer_id, starting_balance)

        self._minimum_balance = minimum_balance
        self._interest_rate = interest_rate
        self._type = 'S'

        data = json_load(self._file)
        for acct in data['Accounts']:
            if acct['Account Id'] == self._account_id:
                acct['Type']=self._type
                acct['Minimum Balance'] = self._minimum_balance
                acct['Interest Rate'] = self._interest_rate
        
        json_write(self._file, data)
        print(f'Savings Account created at {self._bank_name} with id {self._account_id} for customer with id {self._customer_id}')
        logger.info(f'Savings Account created at {self._bank_name} with id {self._account_id} for customer with id {self._customer_id}')
        SavingsAccount.__ACCOUNTS__.append(self)
    
    @property
    def minimum_balance(self):
        '''Gets minimum balance'''
        return 'Account minimum balance is ${:0,.2f}'.format(self._minimum_balance)
    
    @property 
    def interest_rate(self):
        '''Gets interest rate'''
        return 'Account interest rate is {:0,.2f}%'.format(100*self._interest_rate)
    
    @property
    def type(self):
        '''Gets account type'''
        return 'Savings Account'
    

    def withdraw(self, amount):
        '''
        Withdraws the amount specified

        Args:
            amount (float): The amount to be withdrawn from the account

        '''
        if self._minimum_balance <= self._balance - amount:
            logger.info('Customer with id {} has withdrawn ${:0,.2f}'.format(self._customer_id, amount))
            self._balance -= amount
        else:
            raise ValueError('The account {} cannot withstand a withdrawl of ${:0,.2f}'.format(self._account_id, amount))
        print(self)

    def next_month(self):
        '''Applys interest to the savings account'''
        self._balance += self._balance*(self._interest_rate/12)
    
    def __del__(self):
        '''Removes account from the list of savings accounts objects'''
        SavingsAccount.__ACCOUNTS__.remove(self)


class CheckingAccount(Account):
    '''
    Creates a customers savings account and holds methods related to savings accounts

    Attributes:
        bank_name (str): The name of the bank holding the account
        customer_id (int): Customer Id
        overdraft_limit (float): Any withdraw that takes the account more than this value below zero will result in a fee
        overdraft_fee (float): Fee amount for an overdraft

    Methods:

    '''
    __ACCOUNTS__ = []
    def __init__(self, bank_name, customer_id, starting_balance=0):
        '''
        CheckingAccount object initialization function

        Args:
            bank_name (str): The name of the bank holding the account
            customer_id (int): Customer Id

        Returns:
            CheckingAccount Class object
        '''
        Account.__init__(self, bank_name, customer_id, starting_balance)

        self._overdraft_limit = 100.0
        self._overdraft_fee = 25
        self._type = 'C'

        data = json_load(self._file)
        for acct in data['Accounts']:
            if acct['Account Id'] == self._account_id:
                acct['Type'] = self._type
                acct['Overdraft Limit'] = self._overdraft_limit
                acct['Overdraft Fee'] = self._overdraft_fee
        
        json_write(self._file, data)
        print(f'Checking Account created at {self._bank_name} with id {self._account_id} for customer with id {self._customer_id}')
        CheckingAccount.__ACCOUNTS__.append(self)
    
    @property
    def overdraft_limit(self):
        '''Gets overdraft limit'''
        return 'Account overdraft limit is ${:0,.2f}'.format(self._overdraft_limit)
    
    @property 
    def overdraft_fee(self):
        '''Gets overdraft fee'''
        return 'Account overdraft fee is ${:0,.2f}'.format(self._overdraft_fee)
    
    @property
    def type(self):
        '''Gets account type'''
        return 'Checking Account'
    
    def withdraw(self, amount):
        '''
        Withdraws the amount specified, and if the user will incurr an overdraft fee, then asks for the users confirmation

        Args:
            amount (float): The amount to be withdrawn from the account

        Returns:
            str: The remaining balance of the account
        '''

        if self._balance >= amount:
            logger.info('Customer with id {} has withdrawn ${:0,.2f}'.format(self._customer_id, amount))
            self._balance -= amount
        elif amount + self._overdraft_fee - self._balance >= self._overdraft_limit:
            logger.error(ValueError('The requested withdrawl brings the account balance below the overdraft limit'))
            raise ValueError('The requested withdrawl brings the account balance below the overdraft limit')
        else:
            confirm = input(f'The requested withdrawl will incurr an overdraft fee of {self._overdraft_fee}. Would you like to continue (y/n)')
            if confirm.lower() == 'y':
                logger.info('Customer with id {} has withdrawn ${:0,.2f} and incurred a overdraft fee of {}'.format(self._customer_id, amount, self._overdraft_fee))
                self._balance -= (amount + self._overdraft_fee)
            elif confirm.lower() == 'n':
                print('Withdrawl Canceled')
            else:
                raise ValueError('Input must be either a "y" or "n"')
        print(self)
    
    def __del__(self):
        '''Removes account from the list of checkings accounts objects'''
        CheckingAccount.__ACCOUNTS__.remove(self)
    
                
class CreditCard():
    '''
    Opens a credit card

    Attributes:
        bank_name (str): The name of the bank holding the account
        customer_id (int): Customer Id
        limit (int): credit limit on the account
        apr (float): interest rate
        statement_balance (float): The balance on the current months statement
        current_balance (float): The current total balance on the card

    Methods:
        Spend : Makes a purchase on the card
        Pay : Pays off the account
    '''
    __CARDS__ = []
    def __init__(self, bank_name, customer_id, limit=1000):
        '''
        CreditCard object initialization function

        Args:
            bank_name (str): The name of the bank holding the account
            customer_id (int): Customer Id
            limit (int): credit limit on the account

        Returns:    
            CreditCard Class Object
        '''
        self._bank_name = bank_name
        self._customer_id = customer_id
        self._limit = limit
        self._apr = 0.26
        self._statement_balance = 0
        self._current_balance = 0


        self._file = file_path/f'{self._bank_name}.json'
        data = json_load(self._file)

        cards = {card['Card Number'] for card in data['Credit Cards']}
        
        try: 
            new_card = max(cards)+1
        except ValueError:
            new_card = 1234123412340001

        self._card_number = new_card
        self._cvv = randint(100,999)

        data['Credit Cards'].append({
            'Customer Id': self._customer_id,
            'Card Number': self._card_number,
            'CVV': self._cvv,
            'Credit Limit': self._limit,
            'APR': self._apr,
            'Statement Balance': self._statement_balance,
            'Current Balance': self._current_balance
        })

        json_write(self._file, data)
        logger.info(f'Credit Card opened with credit card number {self._card_number}')
        print(f'Credit Card created at {self._bank_name} with card number {self._card_number} for customer with id {self._customer_id}')
        CreditCard.__CARDS__.append(self)

    @property
    def bank_name(self):
        '''Gets bank name'''
        return self._bank_name
    @property
    def customer_id(self):
        '''Gets customer name'''
        return self._customer_id
    @property
    def card_number(self):
        '''Gets card number'''
        return f'{self._card_number[:4]}-{self._card_number[4:8]}-{self._card_number[8:-4]}-{self._card_number[-4:]}'
    @property
    def cvv(self):
        '''Gets cvv'''
        return self._cvv
    @property
    def limit(self):
        '''Gets card limit'''
        return self._limit
    @property
    def apr(self):
        '''Gets formatted interest rate'''
        return '{:0,.2f}% APR'.format(self._apr)
    @property
    def statement_balance(self):
        '''Gets formatted statment balance'''
        return '${:0,.2f}'.format(self._statement_balance)
    @property
    def current_balance(self):
        '''Gets formatted current balance'''
        return '${:0,.2f}'.format(self._current_balance)
    
    def spend(self, amount, cvv, note=None):
        '''
        Makes a purchase with the card of {amount}
        
        Args:
            amount (float) : Dollar amount to be spent
            cvv (int) : Three digit security code
            note (str, optional) : A note for the purchase, defaults to None
        
        '''
        if cvv != self._cvv:
            logger.error(ValueError('Transaction declined for ${:0,.2f} on card {}'.format(amount, self._card_number)))
            raise ValueError('The CVV supplied does not match, transaction declined')
        else:
            pass
        if self._limit < self._current_balance + amount:
            logger.error(ValueError('Transaction declined for ${:0,.2f} on card {}'.format(amount, self._card_number)))
            raise ValueError('The purchase was declined. It would put your card over its limit, you can spend ${:0,.2f} more before maxing out'.format((self._limit-self._current_balance)))
        self._current_balance += amount
        self._statement_balance += amount
        
        data = json_load(self._file)
        (card.update({'Current Balance': self._current_balance, 'Statement Balance':self._statement_balance}) for card in data['Credit Cards'] if card['Card Number']==self._card_number)
        json_write(self._file, data)
        logger.info('Purchase made with note:{} on card {} for ${:0,.2f}'.format(note, self._card_number, amount)) if note is not None else logger.info('Purchase made on card {} for ${:0,.2f}'.format( self._card_number, amount))


    def pay(self, account_id, amount):
        '''
        Pays off credit card using funds from account at {account_id}

        Args:
            account_id (int) : Account id of a checking account
            amount (fload) : Dollar amount to pay off
        '''
        account = next(acct for acct in CheckingAccount.__ACCOUNTS__ if acct._account_id == account_id)
        last_month = self._current_balance - self._statement_balance
        if account._balance < amount:
            logger.error(ValueError('The account id specified only has ${:0,.2f} available, and cannot pay ${:0,.2f}'.format(account._balance, amount)))
            raise ValueError('The account id specified only has ${:0,.2f} available, and cannot pay ${:0,.2f}'.format(account._balance, amount))
        elif amount > self._current_balance:
            account.withdraw(self._current_balance)
            logger.info('Credit card {} fully paid off, and ${:0,.2f} were withdrawn from account id {}'.format(self._card_number, self._current_balance, account_id))
            self._current_balance = 0
            self._statement_balance = 0
        elif amount < last_month:
            self._current_balance -= amount
            logger.info('${:0,.2f} was paid towards credit card {} with funds from account id {}. The remaining statement balance is ${:0,.2f} and total balance is ${:0,.2f}'.format(amount, self._card_number, account_id, self._statement_balance, self._statement_balance))
            print('${:0,.2f} was paid towards credit card {} with funds from account id {}. The remaining statement balance is ${:0,.2f} and total balance is ${:0,.2f}'.format(amount, self._card_number, account_id, self._statement_balance, self._statement_balance))
        else:
            self._statement_balance = (0 if self._statement_balance <= amount else self._statement_balance + (last_month-amount))
            self._current_balance -= amount
            account.withdraw(amount)
            print('${:0,.2f} was paid towards credit card {} with funds from account id {}. The remaining statement balance is ${:0,.2f} and total balance is ${:0,.2f}'.format(amount, self._card_number, account_id, self._statement_balance, self._statement_balance))

        data = json_load(self._file)
        
        (card.update({
            'Current Balance': self._current_balance,
            'Statement Balance': self._statement_balance
        }) for card in data['Credit Cards'] if card['Card Number'] == self._card_number)

        json_write(self._file, data)

    def next_month(self):
        '''
        Iterates to the next month, applying interest and moving to the next statement
        '''
        if self.current_balance == self.statement_balance:
                self._current_balance = self._statement_balance
                self._statement_balance = 0
        else:
            self._current_balance = self._statement_balance + ((self._current_balance-self._statement_balance)*(1+self._apr/12))
            self._statement_balance = 0
            

        data = json_load(self._file)
        (card.update({
            'Current Balance': self._current_balance,
            'Statement Balance': self._statement_balance
        }) for card in data['Credit Cards'] if card['Card Number'] == self._card_number)

        json_write(self._file, data)
    
    def __del__(self):
        '''Removes the credit card from the list of credit card objects'''
        CreditCard.__CARDS__.remove(self)
        
