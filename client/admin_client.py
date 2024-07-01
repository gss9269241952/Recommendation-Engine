# In client/admin_client.py
import socket

def send_request(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9998))
    client_socket.send(request.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response



def admin_menu():
    while True:
        admin_menu = """------------------------------->
    \nAdmin Menu:
    1. Add Meal
    2. Remove Meal
    3. Update Meal
    4. Change Price
    5. Check Availability
    6. Exit
    ------------------------------->
            """
        print(admin_menu)
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
            request = f"ADMIN|LOGOUT"
            response = send_request(request)
            print(response)
            if "Logout from Admin Successfull!!" in response:
                return True

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    admin_menu()
