import threading
import sys
import os

# Add the project's root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.server import start_server
from client.admin_client import admin_menu
from client.chef_client import chef_menu
from client.employee_client import employee_menu
from server.server import authenticate_user

def run_server():
    start_server()

def run_client():
    import time
    time.sleep(1)
    try:
        while True:
            username = input("Enter your username: ")
            password = input("Enter your password: ")

            # Authenticate user based on username and password
            user_id, role = authenticate_user(username, password)

            if user_id:
                break
            else:
                print("Invalid credentials. Please try again.")

        if role == "admin":
            admin_menu()
        elif role == "chef":
            chef_menu()
        elif role == "employee":
            employee_menu()
        else:
            print("Invalid role")


    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    client_thread = threading.Thread(target=run_client)
    client_thread.start()

    server_thread.join()
    client_thread.join()
