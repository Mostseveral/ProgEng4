from datetime import datetime
from typing import List, Dict
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

# Database Models

class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    unit = Column(String, nullable=False)


class ProductPrice(Base):
    __tablename__ = 'product_prices'

    price_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    price = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)


class Discount(Base):
    __tablename__ = 'discounts'

    discount_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)


class Sale(Base):
    __tablename__ = 'sales'

    sale_id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now, nullable=False)
    total_price = Column(Float, nullable=False)
    discount = Column(Float, nullable=True)
    payment_method = Column(String, nullable=True)
    payment_status = Column(String, nullable=True)


class SaleItem(Base):
    __tablename__ = 'sale_items'

    item_id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.sale_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)


class Receipt(Base):
    __tablename__ = 'receipts'

    receipt_id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.sale_id'), nullable=False)
    total_price = Column(Float, nullable=False)
    issued_date = Column(DateTime, default=datetime.now, nullable=False)

    sale = relationship('Sale')


def init_db():
    engine = create_engine('postgresql+psycopg2://denis:12345@localhost/sales')
    Base.metadata.create_all(engine)
    return engine


class SaleSystem:
    def __init__(self, session):
        self.session = session

    def list_products(self):
        products = self.session.query(Product).all()
        if not products:
            print("No products found.")
            return
        for product in products:
            print(f"Product ID: {product.product_id}, Name: {product.name}, Description: {product.description}")

    def list_discounts(self):
        discounts = self.session.query(Discount).filter(
            Discount.start_date <= datetime.now(),
            Discount.end_date >= datetime.now()
        ).all()
        return discounts


class SaleSystemCLI:
    def __init__(self, system):
        self.system = system
        self.current_sale = None
        self.current_sale_items = []
        self.current_discount = None

    def start(self):
        print("Welcome to the Sale System!")
        while True:
            print("\nMain Menu:")
            print("1. List Products")
            print("2. Start Sale")
            print("3. Add Item to Sale")
            print("4. Remove Item from Sale")
            print("5. Apply Discount")
            print("6. Cancel Sale")
            print("7. Complete Sale")
            print("8. List Receipts")
            print("9. Exit")

            choice = input("Select an option: ").strip()
            if choice == "1":
                self.system.list_products()
            elif choice == "2":
                self.start_sale()
            elif choice == "3":
                self.add_item_to_sale()
            elif choice == "4":
                self.remove_item_from_sale()
            elif choice == "5":
                self.apply_discount()
            elif choice == "6":
                self.cancel_sale()
            elif choice == "7":
                self.complete_sale()
            elif choice == "8":
                self.list_receipts()
            elif choice == "9":
                print("Exiting system. Goodbye!")
                break
            else:
                print("Invalid option, try again.")

    def start_sale(self):
        if self.current_sale is not None:
            print("A sale is already in progress.")
            return

        self.current_sale = Sale(total_price=0, payment_status="In Progress")
        self.current_sale_items = []
        self.current_discount = None
        print("New sale started.")

    def add_item_to_sale(self):
        if self.current_sale is None:
            print("No sale in progress. Start a sale first.")
            return

        try:
            product_id = int(input("Enter Product ID: "))
            quantity = int(input("Enter Quantity: "))
            product = self.system.session.query(Product).filter_by(product_id=product_id).first()

            if not product:
                print("Product not found.")
                return

            price_entry = self.system.session.query(ProductPrice).filter(
                ProductPrice.product_id == product_id,
                ProductPrice.start_date <= datetime.now(),
                ProductPrice.end_date >= datetime.now()
            ).first()

            if not price_entry:
                print("No active price for this product.")
                return

            price = price_entry.price
            self.current_sale.total_price += price * quantity
            self.current_sale_items.append(SaleItem(product_id=product_id, quantity=quantity, price=price))
            print(f"Added {quantity} {product.unit} of {product.name} to the sale.")
        except ValueError:
            print("Invalid input. Please enter numeric values.")

    def remove_item_from_sale(self):
        if self.current_sale is None:
            print("No sale in progress. Start a sale first.")
            return

        if not self.current_sale_items:
            print("No items in the sale to remove.")
            return

        print("Current Sale Items:")
        for idx, item in enumerate(self.current_sale_items, 1):
            product = self.system.session.query(Product).filter_by(product_id=item.product_id).first()
            print(f"{idx}. {product.name} - Quantity: {item.quantity}, Price per unit: {item.price}")

        try:
            choice = int(input("Select an item to remove: "))
            if 1 <= choice <= len(self.current_sale_items):
                item_to_remove = self.current_sale_items[choice - 1]
                self.current_sale.total_price -= item_to_remove.price * item_to_remove.quantity
                self.current_sale_items.pop(choice - 1)
                print("Item removed from sale.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    

    def apply_discount(self):
        if self.current_sale is None:
            print("No sale in progress. Start a sale first.")
            return

        discounts = self.system.list_discounts()
        if not discounts:
            print("No active discounts available.")
            return

        print("Available Discounts:")
        for idx, discount in enumerate(discounts, 1):
            print(f"{idx}. {discount.name} - {discount.description} ({discount.discount_percentage}% off)")

        try:
            choice = int(input("Select a discount: "))
            if 1 <= choice <= len(discounts):
                self.current_discount = discounts[choice - 1]
                print(f"Applied discount: {self.current_discount.name}")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    def cancel_sale(self):
        if self.current_sale is None:
            print("No sale in progress.")
            return

        self.current_sale = None
        self.current_sale_items = []
        self.current_discount = None
        print("Sale canceled.")

    def complete_sale(self):
        if self.current_sale is None:
            print("No sale in progress.")
            return

        discount_amount = 0
        if self.current_discount:
            discount_amount = self.current_sale.total_price * (self.current_discount.discount_percentage / 100)
            self.current_sale.total_price -= discount_amount

        print(f"Total price after discount: {self.current_sale.total_price}")
        payment_method = input("Enter Payment Method (e.g., Cash, Credit Card): ").strip()
        self.current_sale.payment_method = payment_method
        self.current_sale.discount = discount_amount
        self.current_sale.payment_status = "Completed"

        self.system.session.add(self.current_sale)
        self.system.session.commit()

        for item in self.current_sale_items:
            item.sale_id = self.current_sale.sale_id
            self.system.session.add(item)

        receipt = Receipt(
            sale_id=self.current_sale.sale_id,
            total_price=self.current_sale.total_price
        )
        self.system.session.add(receipt)
        self.system.session.commit()

        print(f"Sale completed. Receipt ID: {receipt.receipt_id}")
        self.current_sale = None
        self.current_sale_items = []
        self.current_discount = None

    def list_receipts(self):
        receipts = self.system.session.query(Receipt).all()
        if not receipts:
            print("No receipts found.")
            return
        for receipt in receipts:
            print(f"Receipt ID: {receipt.receipt_id}, Sale ID: {receipt.sale_id}, Total Price: {receipt.total_price}, Issued Date: {receipt.issued_date}")


if __name__ == "__main__":
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    system = SaleSystem(session)
    cli = SaleSystemCLI(system)
    cli.start()