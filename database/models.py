from flask_sqlalchemy import SQLAlchemy
from database import db
from datetime import date

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String)
    legal_name = db.Column(db.String)
    tax_id = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)

    # Relationships
    sales = db.relationship("Sale", back_populates="client")
    payments = db.relationship("Payment", back_populates="client")
    debts = db.relationship("Debt", back_populates="client")  # una por venta, entonces uselist=True

class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.Integer)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    total_amount = db.Column(db.Float)
    issue_date = db.Column(db.Date)
    due_date = db.Column(db.Date)

    # Relationships
    client = db.relationship("Client", back_populates="sales")
    items = db.relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan"
    )
    debt = db.relationship(
        "Debt",
        back_populates="sale",
        uselist=False,
        cascade="all, delete-orphan"
    )

class SaleItem(db.Model):
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    quantity = db.Column(db.Float)
    price_unit = db.Column(db.Float)

    # Relationships
    sale = db.relationship("Sale", back_populates="items")
    product = db.relationship("Product")

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    amount = db.Column(db.Float)
    date = db.Column(db.Date)
    
    # Relationship
    client = db.relationship("Client", back_populates="payments")

class Debt(db.Model):
    __tablename__ = 'debts'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String, default="pending")  # o "paid", "partial"

    # Relaciones
    sale = db.relationship("Sale", back_populates="debt", uselist=False)
    client = db.relationship("Client", back_populates="debts")

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)  # Precio actual de inventario o costo unitario
    cost = db.Column(db.Float)
    brand_name = db.Column(db.String)

    inventory_items = db.relationship("Inventory", back_populates="product")
    purchase_items = db.relationship("PurchaseItem", back_populates="product")  # <-- aquí va la relación inversa

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    quantity = db.Column(db.Float)

    # Relaciones
    product = db.relationship("Product", back_populates="inventory_items")

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Relationship
    purchases = db.relationship("Purchase", back_populates="supplier")

class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"))
    purchase_number = db.Column(db.Integer) 
    total_amount = db.Column(db.Float)
    date = db.Column(db.Date)

    supplier = db.relationship("Supplier", back_populates="purchases")
    items = db.relationship("PurchaseItem", back_populates="purchase")  # Correcto

class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))  # Apunta a products.id
    quantity = db.Column(db.Float)
    cost = db.Column(db.Float)

    purchase = db.relationship("Purchase", back_populates="items")
    product = db.relationship("Product", back_populates="purchase_items")  # Aquí la relación inversa en Product


if __name__ == "__main__":
    pass
