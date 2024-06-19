# In client/admin_client.py
from client.client import send_request


def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Add Meal")
        print("2. Remove Meal")
        print("3. Update Meal")
        print("4. Change Price")
        print("5. Check Availability")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            meal_name = input("Enter meal name: ")
            price = input("Enter price: ")
            availability = input("Enter availability (yes/no): ")
            request = f"ADMIN|ADD_MEAL|{meal_name}|{price}|{availability}"
            response = send_request(request)
            print(response)

        elif choice == '2':
            meal_id = input("Enter meal ID to remove: ")
            request = f"ADMIN|REMOVE_MEAL|{meal_id}"
            response = send_request(request)
            print(response)

        elif choice == '3':
            meal_id = input("Enter meal ID to update: ")
            meal_name = input("Enter new meal name (leave blank to skip): ")
            price = input("Enter new price (leave blank to skip): ")
            availability = input("Enter new availability (yes/no, leave blank to skip): ")
            request = f"ADMIN|UPDATE_MEAL|{meal_id}|{meal_name}|{price}|{availability}"
            response = send_request(request)
            print(response)

        elif choice == '4':
            meal_id = input("Enter meal ID to change price: ")
            new_price = input("Enter new price: ")
            request = f"ADMIN|CHANGE_PRICE|{meal_id}|{new_price}"
            response = send_request(request)
            print(response)

        elif choice == '5':
            meal_id = input("Enter meal ID to check availability: ")
            request = f"ADMIN|CHECK_AVAILABILITY|{meal_id}"
            response = send_request(request)
            print(response)

        elif choice == '6':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    admin_menu()
