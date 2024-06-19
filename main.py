import threading
import sys
import os

# Add the project's root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.server import start_server
from client.admin_client import admin_menu
from client.chef_client import chef_menu
from client.employee_client import employee_menu


def run_server():
    start_server()

def run_client():
    role = input("Enter your role (admin/chef/employee): ")
    if role == "admin":
        admin_menu()
    elif role == "chef":
        chef_menu()
    elif role == "employee":
        employee_menu()
    else:
        print("Invalid role")

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    client_thread = threading.Thread(target=run_client)
    client_thread.start()

    server_thread.join()
    client_thread.join()
