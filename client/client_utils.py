import json
import socket
from server.database import get_db_connection
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


def view_detailed_feedback(id):
    response = send_request(f'CHEF|VIEW_DETAILED_FEEDBACK_FROM_USER|{id}')
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
        print("3) View Detailed Feedback from Users")

        choice = input("Enter your choice 1 , 2 or 3 :").strip()
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
        elif choice == '3':
            id = int(input("Enter ID of the food item for which you want to see detailed feedback from User ").strip())
            if id in menu_id_list:
                view_detailed_feedback(id)
                break
            else:
                print("Invalid ID. Please enter a valid food ID from the discard menu.")
        else:
            print("Invalid choice. Please select 1 , 2 or 3")




def handle_questions(response,user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    food_item_id_name_dict = json.loads(response)


    print("this is the list of food items that are rolled out for detailed feedback :")
    for item in food_item_id_name_dict:
        print(item['foodItemName'])

    for item in food_item_id_name_dict:
        food_item_name = item['foodItemName']
        food_item_id = int(item['foodItemID'])
        questions = [
                f"What didn’t you like about {food_item_name}?",
                f"How would you like {food_item_name} to taste?",
                f"Share your mom’s recipe for {food_item_name}"
            ]

        print(f"\nPlease provide your feedback for {food_item_name}:")

        answers = []
        for question in questions:
            answer = input(f"{question}\n")
            answers.append(answer)

        # Step 4: Save the responses in the DetailedFeedback table
        for question, answer in zip(questions, answers):
            cursor.execute("""
                            INSERT INTO DetailedFeedback (foodItemID, question, answer, userID)
                            VALUES ((SELECT foodItemID FROM FoodItem WHERE itemName = %s), %s, %s, %s)
                        """, (food_item_id, question, answer, user_id))
        print("Thank you for your feedback. It has been recorded successfully.")


def update_profile():
    diet_preference = input("Please select one -\n1. Vegetarian\n2. Non Vegetarian\n3. Eggetarian\n")
    if diet_preference == '1':
        diet_preference = 'Vegetarian'
    elif diet_preference == '2':
        diet_preference = 'Non Vegetarian'
    else:
        diet_preference = 'Eggetarian'

    spice_level = input("Please select your spice level -\n1. High\n2. Medium\n3. Low\n")
    if spice_level == '1':
        spice_level = 'High'
    elif spice_level == '2':
        spice_level = 'Medium'
    else:
        spice_level = 'Low'

    cuisine_preference = input("What do you prefer most? -\n1. North Indian\n2. South Indian\n3. Other\n")
    if cuisine_preference == '1':
        cuisine_preference = 'North Indian'
    elif cuisine_preference == '2':
        cuisine_preference = 'South Indian'
    else:
        cuisine_preference = 'Other'

    sweet_tooth = input("Do you have a sweet tooth? -\n1. Yes\n2. No\n")
    if sweet_tooth == '1':
        sweet_tooth = 'Yes'
    else:
        sweet_tooth = 'No'

    profile_data = {
        'diet_preference': diet_preference,
        'spice_level': spice_level,
        'cuisine_preference': cuisine_preference,
        'sweet_tooth': sweet_tooth
    }

    return profile_data

def handle_client_vote_meal(response):
    if response:
        response_data = json.loads(response)
        if response_data['status'] == 'success':
            recommendations = response_data['recommendations']

            # Extract user preferences from the response
            user_preferences = {
                'diet_preference': recommendations[0]['diet_preference'],
                'spice_level': recommendations[0]['spice_level'],
                'cuisine_preference': recommendations[0]['cuisine_preference'],
                'sweet_tooth': recommendations[0]['sweet_tooth']
            }

            # Sort recommendations based on user preferences
            sorted_recommendations = sorted(
                recommendations,
                key=lambda x: (
                    x['diet_preference'] == user_preferences['diet_preference'],
                    x['spice_level'] == user_preferences['spice_level'],
                    x['cuisine_preference'] == user_preferences['cuisine_preference'],
                    x['sweet_tooth'] == user_preferences['sweet_tooth']
                ),
                reverse=True
            )

            print("\n=== Today's Top Meal Recommendations ===")
            print("Please vote for your preferred meal by entering the number:")
            print("========================================\n")
            print(f"Sorted list for user preferences ( diet_preference : {user_preferences['diet_preference']}, "
                  f"spice_level : {user_preferences['spice_level']}, cuisine_preference : {user_preferences['cuisine_preference']}, "
                  f"sweet_tooth : {user_preferences['sweet_tooth']}):\n")

            # Display the sorted list of recommendations
            for idx, recommendation in enumerate(sorted_recommendations, start=1):
                print(
                    f"{idx}. Meal ID: {recommendation['meal_id']}, "
                    f"Recommendation Score: {recommendation['recommendation_score']}, "
                    f"Category: {recommendation['Category']}, "
                    f"diet_preference: {recommendation['diet_preference']}, "
                    f"spice_level: {recommendation['spice_level']}, "
                    f"cuisine_preference: {recommendation['cuisine_preference']}, "
                    f"sweet_tooth: {recommendation['sweet_tooth']}, "
                )

            selected_option = int(input("\nEnter your choice (1-6): "))
            selected_meal = sorted_recommendations[selected_option - 1]
            return selected_meal


        else:
            print(response_data['message'])
            print(f"Error details: {response_data['error_details']}")
    else:
        print("Failed to get recommendations.")