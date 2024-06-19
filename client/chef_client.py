from client.client import send_request

def chef_menu():
    while True:
        print("1. Recommend Meals")
        print("2. Broadcast Meals")
        print("3. Publish Monthly Report")
        print("4. Show Today's Meal")
        print("5. Show Meal Ratings")
        choice = input("Enter your choice: ")

        if choice == '1':
            request = "RECOMMEND_MEALS"
            response = send_request(request)
            print(response)
        
        # Additional options...

if __name__ == "__main__":
    chef_menu()
