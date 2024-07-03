import socket
import json

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
5. Logout
------------------------------->
            """
        print(employee_menu)
        choice = input("Enter your choice: ")
        if choice == '1':
            request = f"EMPLOYEE|VOTE_MEAL|{user_id}"
            response = send_request(request)
            if response:
                response_data = json.loads(response)
                if response_data['status'] == 'success':
                    recommendations = response_data['recommendations']
                    print("\n=== Today's Top Meal Recommendations ===")
                    print("Please vote for your preferred meal by entering the number:")
                    print("========================================\n")
                    for recommendation in recommendations:
                        print(
                            f"{recommendation['index']}. Meal ID: {recommendation['meal_id']}, Recommendation Score: {recommendation['recommendation_score']}, Category : {recommendation['Category']}")

                    selected_option = int(input("\nEnter your choice (1-6): "))
                    selected_meal = recommendations[selected_option - 1]
                    print("selected_meal", selected_meal)

                    # Sending vote back to the server
                    vote_request = f"EMPLOYEE|STORE_VOTE|{selected_meal['meal_id']}|{user_id}"
                    vote_response = send_request(vote_request)
                    if vote_response:
                        print(vote_response)
                    else:
                        print("Failed to store vote.")
                else:
                    print(response_data['message'])
                    print(f"Error details: {response_data['error_details']}")
            else:
                print("Failed to get recommendations.")
            # print(response)

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
            request = f"EMPLOYEE|LOGOUT"
            response = send_request(request)
            print(response)
            if "Logout from Admin Successfull!!" in response:
                return True

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    employee_menu()
