from client.client import send_request

def employee_menu():
    while True:
        print("1. Vote for Meal")
        print("2. Give Feedback")
        print("3. View Notifications")
        print("4. View Today's Menu")
        print("5. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            # meal_id = input("Enter meal ID: ")
            request = f"EMPLOYEE|VOTE_MEAL"
            response = send_request(request)
            print(response)

        elif choice == '2':
            meal_id = input("Enter meal ID to give feedback for: ")
            rating = input("Enter rating (1-5): ")
            comment = input("Enter your comment: ")
            request = f"EMPLOYEE|GIVE_FEEDBACK|{meal_id}|{rating}|{comment}"
            response = send_request(request)
            print(response)

        elif choice == '3':
            request = "EMPLOYEE|SEE_MENU"
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
