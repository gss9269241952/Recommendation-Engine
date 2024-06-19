from client.client import send_request

def chef_menu():
    while True:
        print("1. Recommend Meals")
        print("2. Broadcast Meals")
        print("3. Publish Monthly Report")
        print("4. Show Today's Meal")
        print("5. Show Meal Ratings")
        choice = input("Enter your choice: ")

        # if choice == '1':
        #     request = "RECOMMEND_MEALS"
        #     response = send_request(request)
        #     print(response)
        #


        if choice == '1':
            meal_id = input("Enter meal ID to vote for: ")
            request = f"CHEF|VOTE_FOR_MEAL|{meal_id}"
            response = send_request(request)
            print(response)

        elif choice == '2':
            meal_id = input("Enter meal ID to give feedback for: ")
            rating = input("Enter rating (1-5): ")
            comment = input("Enter your comment: ")
            request = f"CHEF|GIVE_FEEDBACK|{meal_id}|{rating}|{comment}"
            response = send_request(request)
            print(response)

        elif choice == '3':
            request = "CHEF|VIEW_NOTIFICATIONS"
            response = send_request(request)
            print(response)

        elif choice == '4':
            request = "CHEF|VIEW_TODAYS_MENU"
            response = send_request(request)
            print(response)

        elif choice == '5':
            print("Returning to main menu...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    chef_menu()
