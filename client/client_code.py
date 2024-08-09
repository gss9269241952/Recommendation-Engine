import socket
import sys
import time
from client.admin_client import admin_menu
from client.chef_client import chef_menu
from client.employee_client import employee_menu
from server.server_code import authenticate_user

def send_request(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9998))
    client_socket.send(request.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response

def run_client():
    time.sleep(1)  # Ensure server starts first
    try:
        while True:
            username = input("Enter your username: ")
            password = input("Enter your password: ")

            user_id, role = authenticate_user(username, password)
            print("user id : ", user_id,"role :", role)

            if user_id:
                break
            else:
                print("Invalid credentials. Please try again.")

        if role == "admin":
            admin_menu(user_id,role)
        elif role == "chef":
            chef_menu()
        elif role == "employee":
            employee_menu(user_id)
        else:
            print("Invalid role")

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
