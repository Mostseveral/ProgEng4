from datetime import datetime
from typing import List, Dict, Optional
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

class ProductUnit(Base):
    __tablename__ = 'product_units'

    unit_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)

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

    products = relationship('Product', secondary='discount_products')

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

# Many-to-Many Table

discount_products = Table(
    'discount_products', Base.metadata,
    Column('discount_id', Integer, ForeignKey('discounts.discount_id')),
    Column('product_id', Integer, ForeignKey('products.product_id'))
)

# Initialize Database

def init_db():
    engine = create_engine('postgresql+psycopg2://denis:12345@localhost/sales')
    Base.metadata.create_all(engine)
    return engine

def add_sample_data(session):
    # Adding sample products
    

    # Adding product prices
     # Adding product prices
    prices = [
        ProductPrice(product_id=1, price=49.99, start_date=datetime(2024, 1, 1), end_date=datetime(2024, 12, 31))
    ]
    session.add_all(prices)

    discount2 = Discount(name="Carta Magnit", description="3% and bonusi", discount_percentage=3.0, start_date=datetime(2019, 2, 1), end_date=datetime(2077, 2, 1))
    
  


    session.commit()

# Example Usage
if __name__ == "__main__":
    # Initialize system and database
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add sample data
    add_sample_data(session)

    # Query data
    products = session.query(Product).all()
    for product in products:
        print(f"Product ID: {product.product_id}, Name: {product.name}, Description: {product.description}")

    # Query receipts (example)
    receipts = session.query(Receipt).all()
    for receipt in receipts:
        print(f"Receipt ID: {receipt.receipt_id}, Sale ID: {receipt.sale_id}, Total Price: {receipt.total_price}, Issued Date: {receipt.issued_date}")
