# Models go here
import peewee

db = peewee.SqliteDatabase("betsy_database.db")


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Buyer(BaseModel):
    username = peewee.CharField(unique=True, max_length=20)
    name = peewee.CharField(max_length=20)
    address = peewee.CharField(max_length=30)
    billing_info = peewee.CharField(max_length=20)


class Tag(BaseModel):
    name = peewee.CharField(unique=True, max_length=50)


class Product(BaseModel):
    product_name = peewee.CharField(max_length=100, default="", index=True)
    description = peewee.CharField(max_length=100, index=True)
    price = peewee.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = peewee.IntegerField(
        constraints=[peewee.Check("quantity_in_stock >= 0")]
    )
    owners = peewee.ManyToManyField(Buyer, backref="owned_products")
    tags = peewee.ManyToManyField(Tag, backref="product_tag")


class Transaction(BaseModel):
    user = peewee.ForeignKeyField(Buyer, backref="transaction_id")
    product = peewee.ForeignKeyField(Product, backref="product_name", index=True)
    date = peewee.DateField()
    products_purchased = peewee.IntegerField(
        constraints=[peewee.Check("products_purchased >= 0")]
    )


ProductBuyer = Product.owners.get_through_model()
ProductTag = Product.tags.get_through_model()

db.connect()

db.create_tables([Buyer, Product, Transaction, Tag, ProductBuyer, ProductTag])
