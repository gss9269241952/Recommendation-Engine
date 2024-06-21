from client.client import send_request

def chef_menu():
    while True:
        print("1. Recommend Meals")
        print("2. Broadcast Meals")
        print("3. View Notification")
        print("4. Show Today's Meal")
        print("5. Show Meal Ratings")
        print("6. Exit")
        choice = input("Enter your choice: ")

        # if choice == '1':
        #     request = "RECOMMEND_MEALS"
        #     response = send_request(request)
        #     print(response)
        #


        if choice == '1':
            # request = f"CHEF|VOTE_FOR_MEAL|{meal_id}"
            request = f"CHEF|RECOMMEND_MEALS"
            response = send_request(request)
            # print(response)

        elif choice == '2':   #this is going to be BROADCAST_MEALS

            request = f"CHEF|BROADCAST_MEALS"
            response = send_request(request)
            # print(response)

        elif choice == '3':
            request = "CHEF|VIEW_NOTIFICATIONS"
            response = send_request(request)
            # print(response)

        elif choice == '4':
            request = "CHEF|VIEW_TODAYS_MENU"
            response = send_request(request)
            print(response)

        elif choice == '5':
            request = "CHEF|SHOW_MEAL_RATINGS"
            response = send_request(request)
            # print(response)
        elif choice == '6':
            request = f"CHEF|LOGOUT"
            response = send_request(request)
            print(response)
            if "Logout from Chef Successfull!!" in response:
                return True

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    chef_menu()
