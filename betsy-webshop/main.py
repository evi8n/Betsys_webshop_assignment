# Do not modify these lines
__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

# Add your code after this line
import peewee
import models
from rapidfuzz import fuzz
from datetime import datetime


def search(term):
    """
    Allows users to search for products by providing a search term,
    which can be the name or the description of the product.
    By performing a fuzzy search it returns the search result
    that comes closer to the provided term, so some spelling mistakes
    are allowed.
    Returns all details of the product.
    """
    term = term.lower()
    products = models.Product.select()

    matching_products = []

    for product in products:
        product_name = product.product_name.lower()
        product_description = product.description.lower()

        name_score = fuzz.ratio(term, product_name)
        description_score = fuzz.ratio(term, product_description)

        if name_score >= 70 or description_score >= 70:
            matching_products.append(product)

    if matching_products:
        for product in matching_products:
            print(f"Product ID: {product.id}.")
            print(f"Product Name: {product.product_name}")
            print(f"Description: {product.description}")
            print(f"Price: {product.price}")
            print(f"Quantity in Stock: {product.quantity_in_stock}")
    else:
        print("No matching products found.")


def list_user_products(username):
    """
    Returns a list of the products that the provided user owns.
    """
    try:
        user = models.Buyer.get(models.Buyer.username == username)
        user_products = user.owned_products

        if user_products:
            print(f"-{user.username}- products owned:")
            for product in user_products:
                print(f"Product Name: {product.product_name}")
                print(f"Description: {product.description}")
                print(f"Price: {product.price}")
        else:
            print("User owns no products.")

    except models.Buyer.DoesNotExist:
        print("User was not found.")


def list_products_per_tag(tag_id):
    """
    lists products associated with a specific tag identified
    by its tag_id. It returns the details of the products that have been
    tagged with the specified tag.
    """
    try:
        tag = models.Tag.get(models.Tag.name == tag_id)

        tagged_products = (
            models.Product.select()
            .join(models.ProductTag)
            .join(models.Tag)
            .where(models.Tag.id == tag.id)
        )

        if tagged_products:
            for product in tagged_products:
                print(f"Product Name: {product.product_name}")
                print(f"Description: {product.description}")
                print(f"Price: {product.price}")
                print(f"Quantity in Stock: {product.quantity_in_stock}")
        else:
            print("No products found with this tag.")

    except models.Tag.DoesNotExist:
        print("Tag was not found.")


def add_product_to_catalog(username, product_name):
    """
    Allows the user identified by their username to add a specific product
    to their catalog of owned products.
    It checks if the product with the given product_name
    exists in the database and,
    if it does, associates it with the user.
    """
    products = models.Product.select()

    for product in products:
        if product.product_name.lower() == product_name.lower():
            try:
                user = models.Buyer.get(models.Buyer.username == username)
                user.owned_products.add(product)

                print(
                    f"Added product '{product.product_name}' to the catalogue of {user.username}."
                )
            except models.Buyer.DoesNotExist:
                print("User was not found.")


def update_stock(product_name, new_quantity):
    """
    Enables the update of the stock quantity
    for a specific product identified by its product_name.
    It retrieves the product and sets its quantity in stock
    to the new quantity provided.
    """
    try:
        product = models.Product.get(models.Product.product_name == product_name)

        product.quantity_in_stock = new_quantity
        product.save()

        print(f"Stock quantity for '{product.product_name}' updated to {new_quantity}.")

    except models.Product.DoesNotExist:
        print("Product not found.")


def purchase_product(product_name, username, quantity):
    """
    Allows the user identified by their username
    to purchase a specific quantity of a product.
    It checks if the product is in stock and records the transaction,
    deducts the purchased quantity from the product's stock
    and calculates the total purchase price.
    """
    try:
        product = models.Product.get(models.Product.product_name == product_name)
        buyer = models.Buyer.get(models.Buyer.username == username)

        if product.quantity_in_stock >= quantity:
            total_price = product.price * quantity

            product.quantity_in_stock -= quantity
            product.save()

            transaction = models.Transaction.create(
                user=buyer,
                product=product,
                date=datetime.now(),
                products_purchased=quantity,
            )
            buyer.owned_products.add(product)

            print(
                f"Purchase successful! {quantity} pieces of '{product.product_name}' purchased for €{total_price}."
            )
        else:
            print(
                f"Insufficient stock for '{product.product_name}'. Current stock: {product.quantity_in_stock}."
            )

    except (models.Product.DoesNotExist, models.Buyer.DoesNotExist):
        print("Product or buyer not found.")


def remove_product(username, product_name):
    """
    Allows a user identified by their username
    to remove a specific product identified
    by its product_name from their catalog of owned products.
    """
    try:
        user = models.Buyer.get(models.Buyer.username == username)

        product = models.Product.get(
            peewee.fn.Lower(models.Product.product_name) == product_name.lower()
        )
        if product in user.owned_products:
            user.owned_products.remove(product)

            print(
                f"Removed product '{product_name}' from the catalogue of {user.username}."
            )
        else:
            print(f"Product '{product_name}' is not owned by {user.username}.")
    except models.Buyer.DoesNotExist:
        print("User was not found.")
    except models.Product.DoesNotExist:
        print(f"Product '{product_name}' was not found.")


def populate_test_database():
    example_user1 = models.Buyer.create(
        username="Anita89",
        name="Anita Aniton",
        address="1987 March St",
        billing_info="MasterCard",
    )
    example_user2 = models.Buyer.create(
        username="Peter12",
        name="Peter Peterson",
        address="12 April St",
        billing_info="Bank Account",
    )

    product1 = models.Product.create(
        product_name="Soap",
        description="Bar of soap",
        price=12.99,
        quantity_in_stock=50,
    )
    product3 = models.Product.create(
        product_name="Shampoo",
        description="Bottle of shampoo",
        price=8.49,
        quantity_in_stock=30,
    )
    product2 = models.Product.create(
        product_name="Beer",
        description="Beer in a bottle",
        price=8.99,
        quantity_in_stock=60,
    )
    product4 = models.Product.create(
        product_name="Hat",
        description="Hat for the head",
        price=6.49,
        quantity_in_stock=20,
    )

    product1.owners.add(example_user1)
    product2.owners.add(example_user2)

    tag1 = models.Tag.create(name="Tag1")
    tag2 = models.Tag.create(name="Tag2")

    product1.tags.add(tag1)
    product1.tags.add(tag2)
    product2.tags.add(tag2)
    product3.tags.add(tag1)

    transaction1 = models.Transaction.create(
        user=example_user1,
        product=product1,
        date="2023-09-10",
        products_purchased=5,
    )
    transaction2 = models.Transaction.create(
        user=example_user2,
        product=product2,
        date="2023-09-11",
        products_purchased=2,
    )

    print("Test data populated.")
