import socket
import json
from client.client_utils import handle_questions,update_profile, handle_client_vote_meal
def send_request(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9998))
    client_socket.send(request.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response
def employee_menu(user_id):
    while True:
        employee_menu = """------------------------------->
\nEmployee Menu:
1. Vote for Meal
2. Give Feedback
3. View Notifications
4. View Today's Menu
5. Give Detailed Feedback for Discard Item
6. Update your Profile
7. Logout
------------------------------->
            """
        print(employee_menu)
        choice = input("Enter your choice: ")
        if choice == '1':
            request = f"EMPLOYEE|VOTE_MEAL|{user_id}"
            response = send_request(request)
            selected_meal = handle_client_vote_meal(response)
            # Sending vote back to the server
            vote_request = f"EMPLOYEE|STORE_VOTE|{selected_meal['meal_id']}|{user_id}"
            vote_response = send_request(vote_request)
            if vote_response:
                print(vote_response)
            else:
                print("Failed to store vote.")


        elif choice == '2':
            meal_id = input("Enter meal ID to give feedback for: ")
            rating = input("Enter rating (1-5): ")
            comment = input("Enter your comment: ")
            request = f"EMPLOYEE|GIVE_FEEDBACK|{meal_id}|{rating}|{comment}|{user_id}"
            response = send_request(request)
            print(response)

        elif choice == '3':
            request = f"EMPLOYEE|NOTIFICATION|{user_id}"
            response = send_request(request)
            print(response)

        elif choice == '4':
            request = "EMPLOYEE|VIEW_TODAY_MENU"
            response = send_request(request)
            print(response)

        elif choice == '5':
            request = f"EMPLOYEE|GET_DETAILED_FEEDBACK_DISCARD_ITEM|{user_id}"
            response = send_request(request)
            updated_response = handle_questions(response,user_id)
            print(updated_response)

        elif choice == '6':
            user_profile_data = update_profile()
            request = f"EMPLOYEE|UPDATE_PROFILE|{json.dumps(user_profile_data)}|{user_id}"
            response = send_request(request)
            print(response)

        elif choice == '7':
            request = f"EMPLOYEE|LOGOUT"
            response = send_request(request)
            print(response)
            if "Logout from Employee Successfull!!" in response:
                return True

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    employee_menu()
