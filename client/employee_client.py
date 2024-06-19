from client.client import send_request

def employee_menu():
    while True:
        print("1. Vote for Meal")
        print("2. Give Feedback")
        print("3. View Notifications")
        print("4. View Today's Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            meal_id = input("Enter meal ID: ")
            request = f"VOTE_MEAL|{meal_id}"
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
            print("Returning to main menu...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    employee_menu()
