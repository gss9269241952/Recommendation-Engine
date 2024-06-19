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
        
        # Additional options...

if __name__ == "__main__":
    employee_menu()
