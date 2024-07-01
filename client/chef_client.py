import json
import socket
from client.client_utils import pretty_print_ratings,pretty_print_recommend_meals

def send_request(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9998))
    client_socket.send(request.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response

def chef_menu():
    while True:
        chef_menu = """
<---------------------------------->
1. Recommend Meals
2. Broadcast Meals
3. View Notification
4. Show Today's Meal
5. Show Meal Ratings
6. Exit
<---------------------------------->
        """
        print(chef_menu)
        choice = input("Enter your choice: ")


        if choice == '1':
            # request = f"CHEF|VOTE_FOR_MEAL|{meal_id}"
            request = f"CHEF|RECOMMEND_MEALS"
            response = send_request(request)
            print(pretty_print_recommend_meals(json.loads(response)))

        elif choice == '2':   #this is going to be BROADCAST_MEALS

            request = f"CHEF|BROADCAST_MEALS"
            response = send_request(request)
            print(response)

        elif choice == '3':
            request = "CHEF|VIEW_NOTIFICATIONS"
            response = send_request(request)
            # print(response)

        elif choice == '4':
            request = "CHEF|VIEW_TODAYS_MENU"
            response = send_request(request)
            response = json.loads(response)
            food_item_id = response['foodItemID']
            food_item_name = response['itemName']
            vote_count = response['voteCount']

            print(f"Today's Menu:")
            print(f"Most Voted Food Item: {food_item_name} (Food Item ID: {food_item_id})")
            print(f"Votes Received: {vote_count}")
            # print(response)

        elif choice == '5':
            request = "CHEF|SHOW_MEAL_RATINGS"
            response = send_request(request)
            print(pretty_print_ratings(json.loads(response)))
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
