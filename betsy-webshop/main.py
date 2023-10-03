# Do not modify these lines
__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

# Add your code after this line
import peewee
import models
from models import initialize_database
from rapidfuzz import fuzz
from datetime import datetime
import os
import json


def main():
    """
    Function to test program
    """
    if os.path.exists("betsy_database.db") == False:
        initialize_database()
        populate_test_database()

    # search("Bottle of shampoo")
    # add_product_to_user_list("Johnny", "gUITAR")
    # list_products_per_tag("misc")
    # list_user_products("Johnny")
    # update_stock("Shampoo", 17)
    # user_purchase_product("Hat", "Anita89", 2)
    # remove_product_from_user_list("Peter12", "Hat")
    # add_new_user()
    add_new_product()
    # remove_product_from_database(11)


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


def list_user_products(user_id):
    """
    Returns a list of the products that the provided user owns.
    """
    try:
        user = models.Buyer.get(models.Buyer.username == user_id)
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
        tag = models.Tag.get(models.Tag.name == tag_id.lower())

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


def add_product_to_user_list(user_id, product_id):
    """
    Allows the user identified by their username to add a specific product
    to their catalog of owned products.
    It checks if the product with the given product_name
    exists in the database and,
    if it does, associates it with the user.
    """
    products = models.Product.select()

    for product in products:
        if product.product_name.lower() == product_id.lower():
            try:
                user = models.Buyer.get(models.Buyer.username == user_id)
                user.owned_products.add(product)

                print(
                    f"Added product '{product.product_name}' to the catalogue of {user.username}."
                )
            except models.Buyer.DoesNotExist:
                print("User was not found.")


def update_stock(product_id, new_quantity):
    """
    Enables the update of the stock quantity
    for a specific product identified by its product_name.
    It retrieves the product and sets its quantity in stock
    to the new quantity provided.
    """
    try:
        product = models.Product.get(models.Product.product_name == product_id)

        product.quantity_in_stock = new_quantity
        product.save()

        print(f"Stock quantity for '{product.product_name}' updated to {new_quantity}.")

    except models.Product.DoesNotExist:
        print("Product not found.")


def user_purchase_product(product_id, user_id, quantity):
    """
    Allows the user identified by their username
    to purchase a specific quantity of a product.
    It checks if the product is in stock and records the transaction,
    deducts the purchased quantity from the product's stock
    and calculates the total purchase price.
    """
    try:
        product = models.Product.get(models.Product.product_name == product_id)
        buyer = models.Buyer.get(models.Buyer.username == user_id)

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
                f"Purchase successful! {quantity} pieces of product '{product.product_id}' purchased for €{total_price}."
            )
        else:
            print(
                f"Insufficient stock for '{product.product_name}'. Current stock: {product.quantity_in_stock}."
            )

    except (models.Product.DoesNotExist, models.Buyer.DoesNotExist):
        print("Product or buyer not found.")


def remove_product_from_user_list(user_id, product_id):
    """
    Allows a user identified by their username
    to remove a specific product identified
    by its product_name from their catalog of owned products.
    """
    try:
        user = models.Buyer.get(models.Buyer.username == user_id)

        product = models.Product.get(
            peewee.fn.Lower(models.Product.product_name) == product_id.lower()
        )
        if product in user.owned_products:
            user.owned_products.remove(product)

            print(
                f"Removed product '{product_id}' from the catalogue of {user.username}."
            )
        else:
            print(f"Product '{product_id}' is not owned by {user.username}.")
    except models.Buyer.DoesNotExist:
        print("User was not found.")
    except models.Product.DoesNotExist:
        print(f"Product '{product_id}' was not found.")


def add_new_user():
    # Allows the user to add a list of new users from a JSON file
    # or to add a user manually by inputting their info
    print("Choose how to add a new user:")
    print("1. Enter user data interactively")
    print("2. Import user data from a file")

    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        username = input("Enter username: ")
        name = input("Enter name: ")
        address = input("Enter address: ")
        billing_info = input("Enter billing info: ")

        # Use the user-provided data to create a new user
        new_user = models.Buyer.create(
            username=username,
            name=name,
            address=address,
            billing_info=billing_info,
        )
        print("User added successfully!")

    elif choice == "2":
        file_path = input("Enter the path to the user data file (e.g., users.json): ")
        try:
            with open(file_path, "r") as file:
                user_data = json.load(file)
                if isinstance(user_data, list):
                    for data in user_data:
                        # Use data from the file to create new users
                        new_user = models.Buyer.create(
                            username=data["username"],
                            name=data["name"],
                            address=data["address"],
                            billing_info=data["billing_info"],
                        )
                    print(f"{len(user_data)} users added successfully!")
                else:
                    print(
                        "Invalid file format. Please provide a JSON array of user data."
                    )

        except FileNotFoundError:
            print("File not found. Please provide a valid file path.")
        except json.JSONDecodeError:
            print("Error decoding JSON data in the file.")

    else:
        print("Invalid choice. Please choose '1' or '2'.")


def add_new_product():
    # Allows the user to add a new product to the existing database
    # from a JSON file
    # or manually by asking for user input
    print("Choose how to add a new product:")
    print("1. Enter product data interactively")
    print("2. Import product data from a file")

    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        name_of_new_product = input("Enter product name: ")
        description = input("Enter product description: ")
        price = float(input("Enter product price: "))
        quantity_in_stock = int(input("Enter product quantity: "))

        # Use the user-provided data to create a new product
        new_product = models.Product.create(
            product_name=name_of_new_product,
            description=description,
            price=price,
            quantity_in_stock=quantity_in_stock,
        )

        add_tags_to_product(new_product)

        print("Product added successfully!")

    elif choice == "2":
        file_path = input(
            "Enter the path to the product data file (e.g., products.json): "
        )
        try:
            with open(file_path, "r") as file:
                product_data = json.load(file)
                if isinstance(product_data, list):
                    for data in product_data:
                        # Use data from the file to create new products
                        new_product = models.Product.create(
                            product_name=data["product_name"],
                            description=data["description"],
                            price=data["price"],
                            quantity_in_stock=data["quantity_in_stock"],
                        )
                    print(f"{len(product_data)} products added successfully!")
                else:
                    print(
                        "Invalid file format. Please provide a JSON array of product data."
                    )

        except FileNotFoundError:
            print("File not found. Please provide a valid file path.")
        except json.JSONDecodeError:
            print("Error decoding JSON data in the file.")

    else:
        print("Invalid choice. Please choose '1' or '2'.")


def add_tags_to_product(new_product):
    # Adds tags to a product, creating new tags if they don't exist
    tags_input = input("Enter tags for the product (comma-separated): ")
    tag_names = [tag.strip() for tag in tags_input.split(",")]

    for tag_name in tag_names:
        tag_name = tag_name.strip().lower()  # Convert tag_name to lowercase
        try:
            tag = models.Tag.get(models.Tag.name == tag_name)
        except models.Tag.DoesNotExist:
            # If the tag doesn't exist, create a new one
            tag = models.Tag.create(name=tag_name)

        # Add the tag to the product
        new_product.tags.add(tag)


def remove_product_from_database(product_id):
    try:
        # Find the product by its primary key (ID)
        product = models.Product.get_by_id(product_id)

        # Delete the product from the database
        product.delete_instance()

        print(f"Product '{product.product_name}' removed from the database.")
    except models.Product.DoesNotExist:
        print(f"Product with ID {product_id} not found in the database.")


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
    product2 = models.Product.create(
        product_name="Beer",
        description="Beer in a bottle",
        price=8.99,
        quantity_in_stock=60,
    )
    product3 = models.Product.create(
        product_name="Shampoo",
        description="Bottle of shampoo",
        price=8.49,
        quantity_in_stock=30,
    )
    product4 = models.Product.create(
        product_name="Hat",
        description="Hat for the head",
        price=6.49,
        quantity_in_stock=20,
    )
    product5 = models.Product.create(
        product_name="Book Title",
        description="Book to read",
        price=19.99,
        quantity_in_stock="50",
    )

    product1.owners.add(example_user1)
    product2.owners.add(example_user2)
    product4.owners.add(example_user2)

    tag1 = models.Tag.create(name="Personal care")
    tag2 = models.Tag.create(name="Entertainment")
    tag3 = models.Tag.create(name="Food & Drink")
    tag4 = models.Tag.create(name="Clothing")

    product1.tags.add([tag1, tag2])
    product2.tags.add(tag3)
    product3.tags.add(tag1)
    product4.tags.add(tag4)
    product5.tags.add(tag2)

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


if __name__ == "__main__":
    main()
