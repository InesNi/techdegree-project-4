import datetime
import csv
import os
from collections import OrderedDict

from peewee import *


with open('inventory.csv', newline='') as csvfile:
    productreader = csv.DictReader(csvfile, delimiter=',')
    products = list(productreader)
    for product in products:
        product['product_price'] = int(
            float(product['product_price'].replace('$', '')) * 100
        )
        product['product_quantity'] = int(product['product_quantity'])
        product['date_updated'] = datetime.datetime.strptime(
            product['date_updated'], '%m/%d/%Y'
            )

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField(primary_key=True)
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

def clear():
    """Clears the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def add_products():
    for product in products:
        try:
            Product.create(
                product_name=product['product_name'],
                product_price=product['product_price'],
                product_quantity=product['product_quantity'],
                date_updated=product['date_updated']
                )
        except IntegrityError:
            product_status = Product.get(product_name=product['product_name'])
            product_status.product_price = product['product_price']
            product_status.product_quantity = product['product_quantity']
            product_status.date_updated = product['date_updated']
            product_status.save()

def initialize():
    """Create the database and the table if they don't exist."""
    db.connect()
    db.create_tables([Product], safe=True)

def menu_loop():
    """Show the menu"""
    choice = None
    
    while choice != 'q':
        clear()
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('Action: ').lower().strip()
        
        if choice in menu:
            menu[choice]()
        elif choice == 'q':
            break
        else:
            print('Your input is invalid. Please try again')

def view_product():
    """View the details of a single product in the database"""
    choice = None
    while choice != 'q':
        clear()
        try:
            id = int(input('Please enter the id number '
                           'of a product you wish to view: '))
            clear()
        except ValueError:
            choice = input(
                "Please use a number. Press enter to try again or 'q' to quit"
                ).lower().strip()
            clear()
            continue
        try:
            sel_product = Product.get_by_id(id)
        except DoesNotExist:
            choice = input(
                "The product with the given id number does not exist."
                "Press enter if you wish to try again or 'q' to quit "
                ).lower().strip()
            clear()
            continue
        timestamp = datetime.datetime.strftime(sel_product.date_updated,
                                               '%m/%d/%Y')
        print("Product ID: ", sel_product.product_id)
        print("Product name:", sel_product.product_name)
        print("Product quantity:", sel_product.product_quantity)
        print("Product price:", sel_product.product_price)
        print("Date updated:",timestamp)
        choice = input(
            "\nTo search for another product press enter, "
            "to quit and go back to main menu enter 'q': "
            ).lower().strip()

def add_product():
    """Add a new product"""
    clear()
    choice = None
    while choice != 'q':
        name = input("Name of product: ").strip()
        while True:
            clear()
            try:
                quantity = int(input("Quantity (in number format): "))
            except ValueError:
                input("Please use numbers. press enter to try again")
                continue
            break
        while True:
            clear()
            try:
                price = int(
                    input("Price of product in $ (number format): ")
                    ) * 100
            except ValueError:
                input("Please use numbers. press enter to try again")
                clear()
                continue
            break
        clear()
        try:
            Product.create(
                product_name=name,
                product_quantity=quantity,
                product_price=price
            )
        except IntegrityError:
            Product.update(
                product_quantity=quantity,
                product_price=price
                ).where(Product.product_name==name).execute()
        print("Product succesfully saved")
        choice = input("Press enter to add another product or 'q' to quit")

def create_backup():
    """Make a backup of the entire contents of the database"""
    clear()
    product_dicts = (Product.select().dicts())
    with open('backup.csv', 'w') as csvfile:
        fieldnames = [
            'product_id', 'product_name',
             'product_quantity', 'product_price',
              'date_updated'
        ]
        datawriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        datawriter.writeheader()
        for item in product_dicts:
            datawriter.writerow(item)
    input('Backup succesfully created. Press enter to return to main menu')

menu = OrderedDict([
    ('v', view_product),
    ('a', add_product),
    ('b', create_backup),
])

if __name__ == '__main__':
    initialize()
    add_products()
    menu_loop()