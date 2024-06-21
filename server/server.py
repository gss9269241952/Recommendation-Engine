import socket
import threading
from server.admin import Admin
from server.chef import Chef
from server.employee import Employee
from server.database import get_db_connection

def authenticate_user(username, password):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Query to fetch user details based on username and password
        cursor.execute("""
            SELECT userID, role
            FROM User
            WHERE name = %s AND password = %s
        """, (username, password))

        user = cursor.fetchone()

        if user:
            user_id = user[0]
            role = user[1]
            return user_id, role.lower()
        else:
            return None, None

    except Exception as e:
        print(f"Error during authentication: {e}")
        return None, None

    finally:
        cursor.close()
        connection.close()
def handle_client(client_socket):
    # Receive and handle client requests
    request = client_socket.recv(1024).decode().strip()  # Ensure no leading/trailing whitespace
    if not request:
        client_socket.close()
        return

    parts = request.split('|')  # Split request by '|'
    print("parts",parts)
    #parts ['ADMIN', 'ADD_MEAL', 'keema', '340', 'yes']

    if len(parts) < 2:
        response = "Invalid request format"
    else:
        role = parts[0]  # First part is the command
        command = parts[1]
        args = parts[2:]  # Rest are arguments


        if role == "ADMIN":
            admin_handler = Admin(role, "gaurav")
            if command == "ADD_MEAL":
                if len(args) == 3:  # Ensure correct number of arguments
                    name = parts[2]
                    price = parts[3]
                    availability = parts[4]
                    response = admin_handler.add_meal(name, price, availability)
                else:
                    response = "Invalid number of arguments for ADD_MEAL command"


            elif command == "REMOVE_MEAL":
                if len(args) == 1:  # Ensure correct number of arguments
                    meal_id = int(args[0])  # Convert meal_id to int
                    response = admin_handler.remove_meal(meal_id)
                else:
                    response = "Invalid number of arguments for REMOVE_MEAL command"


            elif command == "UPDATE_MEAL":
                if len(args) >= 2:  # Ensure correct number of arguments
                    meal_id = int(args[0])  # Convert meal_id to int
                    meal_name = args[1]
                    price = float(args[2]) if len(args) >= 3 else None
                    availability = args[3] if len(args) >= 4 else None
                    response = admin_handler.update_meal(meal_id, meal_name, price, availability)
                else:
                    response = "Invalid number of arguments for UPDATE_MEAL command"


            elif command == "CHANGE_PRICE":
                if len(args) == 2:  # Ensure correct number of arguments
                    meal_id = int(args[0])  # Convert meal_id to int
                    new_price = float(args[1])  # Convert new_price to float
                    response = admin_handler.change_price(meal_id, new_price)
                else:
                    response = "Invalid number of arguments for CHANGE_PRICE command"

            elif command == "CHECK_AVAILABILITY":
                if len(args) == 1:  # Ensure correct number of arguments
                    meal_id = int(args[0])  # Convert meal_id to int
                    response = admin_handler.check_availability(meal_id)
                else:
                    response = "Invalid number of arguments for CHECK_AVAILABILITY command"
            elif command == "LOGOUT":
                response = "Logout from Admin Successfull!!"
            else:
                response = "Invalid command for Admin"



        # elif role == "CHEF":
        #     chef_handler = Chef()
        #     if command == "RECOMMEND_MEALS":
        #         response = chef_handler.recommend_meals(*args)
        #     else:
        #         response = "Invalid command for Chef"

        elif role == "CHEF":
            chef_handler = Chef(role, "gaurav")  # Adjust as needed
            if command == "RECOMMEND_MEALS":
                if len(args) == 0:  # Ensure correct number of
                    response = chef_handler.recommend_meals()
                else:
                    response = "Cannot fetch Recommended meals, Algo is down...."
            elif command == "BROADCAST_MEALS":
                if len(args) == 0:  # Ensure correct number of arguments
                    response = chef_handler.broadcast_meals()
                else:
                    response = "Can not Broadcastv meals Right now"
            elif command == "VIEW_NOTIFICATIONS":
                response = chef_handler.view_notifications()
            elif command == "VIEW_TODAYS_MENU":
                response = chef_handler.get_today_menu()
            elif command == "SHOW_MEAL_RATINGS":
                response = chef_handler.get_ratings()
            elif command == "LOGOUT":
                response = "Logout from Chef Successfull!!"
            else:
                response = "Invalid command for Chef"


        elif role == "EMPLOYEE":
            employee_handler = Employee(1,"gaurav", "Admin")  # Adjust as needed

            if command == "VOTE_MEAL":
                if len(args) == 0:  # Ensure correct number of arguments
                    # meal_id = int(args[0])  # Convert meal_id to int
                    response = employee_handler.vote_for_meal()
                else:
                    response = "Invalid number of arguments for VOTE_FOR_MEAL command"

            elif command == "GIVE_FEEDBACK":
                if len(args) == 3:  # Ensure correct number of arguments
                    # print("args ", args)
                    meal_id = int(args[0])
                    rating = int(args[1])
                    comment = args[2]
                    response = employee_handler.give_feedback(meal_id, rating, comment)
                else:
                    response = "Invalid number of arguments for GIVE_FEEDBACK command"

            elif command == "SEE_MENU":
                response = employee_handler.see_menu()
            elif command == "VIEW_TODAY_MENU":
                response = employee_handler.get_today_menu()
            elif command == "LOGOUT":
                response = "Logout from Employee Successfull!!"
            else:
                response = "Invalid command for Employee"

        else:
            response = "Invalid role"

    client_socket.send(response.encode())
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9998))
    server.listen(5)
    print("Server started on port 9998")

    while True:
        try:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        except Exception as e:
            print(f"Error accepting connection: {e}")

if __name__ == "__main__":
    start_server()
