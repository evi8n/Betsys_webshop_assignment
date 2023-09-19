# Do not modify these lines
__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

# Add your code after this line
import peewee
import models
from rapidfuzz import fuzz


def search(term):
    term = term.lower()
    products = models.Product.select()

    matching_products = []

    for product in products:
        product_name = product.name.lower()
        product_description = product.description.lower()

        # Calculate a fuzzy match score for both name and description
        name_score = fuzz.ratio(term, product_name)
        description_score = fuzz.ratio(term, product_description)

        # You can adjust the threshold score as needed
        # Here, we're considering a product a match if either name or description has a score of at least 70
        if name_score >= 70 or description_score >= 70:
            matching_products.append(product)

    if matching_products:
        for product in matching_products:
            print(f"Product ID: {product.id}.")
            print(f"Product Name: {product.name}")
            print(f"Description: {product.description}")
            print(f"Price: {product.price}")
            print(f"Quantity in Stock: {product.quantity_in_stock}")
    else:
        print("No matching products found.")


def list_user_products(user_id):
    try:
        user = models.Buyer.get(models.Buyer.username == user_id)
        user_products = user.owned_products

        if user_products:
            print(f"-{user.username}- products owned:")
            for product in user_products:
                print(f"Product Name: {product.product_name}")
                print(f"Description: {product.description}")
                print(f"Price: {product.price}")
                print(f"Quantity in Stock: {product.quantity_in_stock}")
        else:
            print("User owns no products.")

    except models.Buyer.DoesNotExist:
        print("User was not found.")


def list_products_per_tag(tag_id):
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


def add_product_to_catalog(user_id, product):
    try:
        user = models.Buyer.get(models.Buyer.username == user_id)
        user.owned_products.add(product)

        print(
            f"Added product '{product.product_name}' to the catalogue of {user.username}."
        )
    except models.Buyer.DoesNotExist:
        print("User was not found.")


def update_stock(product_id, new_quantity):
    try:
        product = models.Product.get(models.Product.id == product_id)

        product.quantity_in_stock = new_quantity
        product.save()

        print(f"Stock quantity for '{product.product_name}' updated to {new_quantity}.")

    except models.Product.DoesNotExist:
        print("Product not found.")


def purchase_product(product_id, buyer_id, quantity):
    try:
        product = models.Product.get(models.Product.id == product_id)
        buyer = models.Buyer.get(models.Buyer.username == buyer_id)

        if product.quantity_in_stock >= quantity:
            total_price = product.price * quantity

            product.quantity_in_stock -= quantity
            product.save()

            transaction = models.Transaction.create(
                user=buyer,
                product=product,
                date=peewee.fn.Now(),
                products_purchased=quantity,
            )

            print(
                f"Purchase successful! {quantity} units of '{product.product_name}' purchased for ${total_price}."
            )
        else:
            print(
                f"Insufficient stock for '{product.product_name}'. Current stock: {product.quantity_in_stock}."
            )

    except (models.Product.DoesNotExist, models.Buyer.DoesNotExist):
        print("Product or buyer not found.")


def remove_product(user_id, product):
    try:
        user = models.Buyer.get(models.Buyer.username == user_id)
        user.owned_products.remove(product)

        print(
            f"Removed product '{product.product_name}' from the catalogue of {user.username}."
        )
    except models.Buyer.DoesNotExist:
        print("User was not found.")


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
        product_name="So",
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
        product_name="Beer 0",
        description="Beer in a bottle",
        price=8.99,
        quantity_in_stock=60,
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


user_id = "Peter12"
product3 = models.Product.create(
    product_name="Shampoo",
    description="Bottle of shampoo",
    price=8.49,
    quantity_in_stock=30,
)

# populate_test_database()
# add_product_to_catalog(user_id, product)

# search("Soap")

# list_products_per_tag("Tag1")
# add_product_to_catalog("Peter12", "Soap")

# list_user_products("Peter12")

# update_stock("Shampoo", 54)
