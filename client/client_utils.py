
import socket

def send_request(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9998))
    client_socket.send(request.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response

def pretty_print_ratings(ratings):
    print("\nRatings and Comments for Food Items:\n")
    print("|| {:^10} || {:^30} || {:^10} || {:^50} ||".format("Food Item ID", "Food Item Name", "Rating", "Comment"))
    print("||" + "-" * 14 + "++" + "-" * 34 + "++" + "-" * 14 + "++" + "-" * 52 + "||")
    for rating in ratings:
        print(
            f"|| {rating['foodItemID']:>12} || {rating['itemName']:^30} || {rating['rating']:>10} || {rating['comment']:^50} ||")
    print("||" + "-" * 14 + "++" + "-" * 34 + "++" + "-" * 14 + "++" + "-" * 52 + "||")

def pretty_print_recommend_meals(top_meals_by_category):
    if not top_meals_by_category:
        print("No meals to display.")
        return

    for category, meals in top_meals_by_category.items():
        if meals:
            print(f"\nRecommended Meals for {category}:\n")
            print("|| {:^10} || {:^10} || {:^15} || {:^20} ||".format("Meal ID", "Avg Rating", "Sentiment Score", "Recommendation Score"))
            print("||" + "-" * 12 + "++" + "-" * 12 + "++" + "-" * 17 + "++" + "-" * 22 + "||")
            for meal in meals:
                print(f"|| {meal['meal_id']:>8} || {meal['avg_rating']:^10.1f} || {meal['sentiment_score']:^15.1f} || {meal['recommendation_score']:^20.1f} ||")
            print("||" + "-" * 12 + "++" + "-" * 12 + "++" + "-" * 17 + "++" + "-" * 22 + "||")
        else:
            print(f"No recommended meals for {category}.")

def beautify_meals(meals):
    if not meals:
        print("No meals to display.")
        return

    # Print table header
    print("\nRecommended Meals:\n")
    print("|| {:^10} || {:^34} || {:^14} || {:^16} || {:^11} ||".format("Meal ID", "Food Item Name", "Avg Rating", "Sentiment Score", "Category"))
    print("||" + "-" * 12 + "++" + "-" * 36 + "++" + "-" * 16 + "++" + "-" * 18 + "++" + "-" * 13 + "||")

    # Extract and print each meal row
    for meal in meals:
        parts = meal.split(',')
        if len(parts) >= 4:
            try:
                meal_id = parts[0].split(': ')[1].strip()
                food_item_name = parts[1].split(': ')[1].strip()
                avg_rating = parts[2].split(': ')[1].strip()
                sentiment_score = parts[3].split(': ')[1].strip()
                category = parts[-1].split(': ')[1].strip()

                print("|| {:^10} || {:^34} || {:^14} || {:^16} || {:^11} ||".format(meal_id, food_item_name, avg_rating, sentiment_score, category))
            except IndexError as e:
                print(f"Malformed meal data: {meal.strip()}")
        else:
            print(f"Malformed meal data: {meal.strip()}")

    # Print table footer
    print("||" + "-" * 12 + "++" + "-" * 36 + "++" + "-" * 16 + "++" + "-" * 18 + "++" + "-" * 13 + "||")


def remove_food_item(id):
    response = send_request(f'CHEF|REMOVE_FOOD_ITEM|{id}')
    print(response)

def get_detailed_feedback(id):
    response = send_request(f'CHEF|GET_DETAILED_FEEDBACK|{id}')
    print(response)
def display_discard_menu( discard_items):
    # Print discard menu items
    print("Discard Menu Items:")
    print(f"{'FOOD ID':<5} {'FOOD NAME':<30}")
    menu_id_list = []
    for item in discard_items:
        menu_id_list.append(item[0])
        print(f"{item[0]:<15} {item[1]:<30}")

    while True:
        print("\nOptions:")
        print("1) Remove a Food Item from Menu List")
        print("2) Get Detailed Feedback")

        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == '1':
            id = int(input("Enter ID of the food item you want to discard (one at a time): ").strip())
            if id in menu_id_list:
                remove_food_item(id)
                break
            else:
                print("Invalid ID. Please enter a valid food ID from the discard menu.")
        elif choice == '2':
            id = int(input("Enter ID of the food item for which you want detailed feedback: ").strip())
            if id in menu_id_list:
                get_detailed_feedback(id)
                break
            else:
                print("Invalid ID. Please enter a valid food ID from the discard menu.")
        else:
            print("Invalid choice. Please select 1 or 2.")