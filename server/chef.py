from server.database import get_db_connection
import numpy as np
import json,re
import datetime
from server.utils import add_notification,get_all_employee_ids,get_top_meals_by_category

class Chef:
    def __init__(self,  role,name):
        # self.user_id = user_id
        self.name = name
        self.role = role


    #
    def recommend_meals(self):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Fetch meal ratings and comments from the feedback table
            cursor.execute("""
                SELECT foodItemID, rating, comment,category
                FROM Feedback
            """)
            feedbacks = cursor.fetchall()

            # Dictionary to hold the aggregated data
            meal_data = {}
            for foodItemID, rating, comment,category in feedbacks:
                if foodItemID not in meal_data:
                    meal_data[foodItemID] = {'ratings': [], 'comments': [], 'category': []}
                meal_data[foodItemID]['ratings'].append(rating)
                meal_data[foodItemID]['comments'].append(comment)
                meal_data[foodItemID]['category'].append(category)
            # Calculate average ratings and sentiment scores
            meal_scores = []
            for meal_id, data in meal_data.items():
                ratings = data['ratings']
                comments = data['comments']
                category = data['category'][0]

                if ratings:  # Check if there are ratings for this meal
                    avg_rating = np.mean(ratings)
                else:
                    avg_rating = 0  # Default to 0 if no ratings

                sentiment_score = self.calculate_sentiment_score(comments)

                # Handle cases where sentiment_score could be None
                if sentiment_score is None:
                    sentiment_score = 0

                recommendation_score = (avg_rating + sentiment_score) / 2
                meal_scores.append({
                    'meal_id': meal_id,
                    'avg_rating': avg_rating,
                    'sentiment_score': sentiment_score,
                    'recommendation_score': recommendation_score,
                    'Category': category
                })
            print("meal scores list : ", meal_scores)
            # Sort meals by recommendation score and return top 5
            top_meals_by_category = get_top_meals_by_category(meal_scores)
            # top_meals = sorted(meal_scores, key=lambda x: x['recommendation_score'], reverse=True)[:5]
            # self.pretty_print_recommend_meals(top_meals)
            print("top_meals_by_category", top_meals_by_category )

            # Convert top_meals to JSON string
            top_meals_json = json.dumps(top_meals_by_category)
            cursor.close()
            connection.close()
            return top_meals_json

        except Exception as e:
            print(f"Error recommending meals: {e}")
            return []
    def get_discard_list(self):
        discard_list = []
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT foodItemID, rating, comment,category
                FROM Feedback
            """)
            feedbacks = cursor.fetchall()
            # Dictionary to hold the aggregated data
            meal_data = {}
            for foodItemID, rating, comment,category in feedbacks:
                if foodItemID not in meal_data:
                    meal_data[foodItemID] = {'ratings': [], 'comments': [], 'category': []}
                meal_data[foodItemID]['ratings'].append(rating)
                meal_data[foodItemID]['comments'].append(comment)
                meal_data[foodItemID]['category'].append(category)
            # Calculate average ratings and sentiment scores
            meal_scores = []

            for meal_id, data in meal_data.items():
                ratings = data['ratings']
                comments = data['comments']
                category = data['category'][0]
                if ratings:  # Check if there are ratings for this meal
                    avg_rating = np.mean(ratings)
                else:
                    avg_rating = 0  # Default to 0 if no ratings

                sentiment_score = self.calculate_sentiment_score(comments)

                # Handle cases where sentiment_score could be None
                if sentiment_score is None:
                    sentiment_score = 0

                recommendation_score = (avg_rating + sentiment_score) / 2
                if recommendation_score < 2:
                    cursor.execute("""
                                        select itemName from fooditem where foodItemID = %s
                                    """, (meal_id, ))

                    result = cursor.fetchone()
                    meal_name = result[0]
                    print(meal_name)
                    l= []
                    l.append(meal_id)
                    l.append(meal_name)
                    discard_list.append(l)
                print("Discard list: ", discard_list)
            return json.dumps(discard_list)
        except Exception as e:
            print(f"Error in getting Discard Item List meals: {e}")
            return []


    def calculate_sentiment_score(self, comments):
        positive_keywords = ['good', 'great', 'excellent', 'amazing', 'delicious']
        negative_keywords = ['bad', 'terrible', 'awful', 'horrible', 'poor']

        sentiment_score = 0
        for comment in comments:
            comment = comment.lower()
            for word in positive_keywords:
                if word in comment:
                    sentiment_score += 1
            for word in negative_keywords:
                if word in comment:
                    sentiment_score -= 1

        # Normalize sentiment score
        if len(comments) > 0:
            sentiment_score /= len(comments)

        return sentiment_score

    def broadcast_meals(self):
        try:
            recommended_meals = json.loads(self.recommend_meals())

            connection = get_db_connection()
            cursor = connection.cursor()
            # print("Recommended meals : ",recommended_meals)
            print("\nBroadcasting recommended meals to employees:")
            top_meals = []
            for meal in recommended_meals:
                for list in recommended_meals[meal]:
                    foodItemID = list['meal_id']
                    cursor.execute("""
                                select itemName from FoodItem where foodItemID = %s """, (foodItemID,))
                    food_item_name = cursor.fetchone()
                    top_meals.append(f"Meal ID: {list['meal_id']},Food Item Name: {food_item_name} Average Rating: {list['avg_rating']}, Sentiment Score: {list['sentiment_score']}, Category: {list['Category']}")


            # Finalize top 3 meals based on chef's choice (example: first three meals)

            print("top meals: ", top_meals)

            # Insert top 3 meals into the Recommendation table

            meal_id_pattern = r'Meal ID: (\d+)'
            category_pattern = r'Category: (\w+)'

            for meal in top_meals:
                meal_id_match = re.search(meal_id_pattern, meal)
                category_match = re.search(category_pattern, meal)
                if meal_id_match and category_match:
                    meal_id = meal_id_match.group(1)
                    category = category_match.group(1)
                    date = datetime.date.today()
                    chef_id = "5"
                    cursor.execute("""
                    INSERT INTO Recommendation (date, chefID, foodItemID, category)
                    VALUES (%s, %s, %s,%s)
                """, (date, chef_id,  meal_id, category))
                    print(f"Meal ID {meal_id} broadcasted to employees.")
                else:
                    print(f"Could not extract information from meal: {meal}")
            connection.commit()
            cursor.close()
            connection.close()

            # Simulate sending selected items to all employees in their VOTE_FOR_MEAL menu
            response_message = json.dumps(top_meals)
            # print(response_message)
            employee_ids = get_all_employee_ids()
            for employee_id in employee_ids:
                add_notification(employee_id, "Chef had broadcasted top meals, You can vote now for your preference of tomorrow's meal.")
            return response_message

        except Exception as e:
            error_message = f"Error broadcasting meals: {e}"
            print(error_message)
            return error_message



    def get_today_menu(self):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Query to find the most voted food item for today
            cursor.execute("""
                SELECT Votes.foodItemID, FoodItem.itemName, COUNT(*) as vote_count
                FROM Votes
                JOIN FoodItem ON Votes.foodItemID = FoodItem.foodItemID
                WHERE DATE(Votes.date) = CURDATE() - INTERVAL 1 DAY
                GROUP BY Votes.foodItemID
                ORDER BY vote_count DESC
                LIMIT 1
            """)

            result = cursor.fetchone()

            if result:
                food_item_id = result[0]
                food_item_name = result[1]
                vote_count = result[2]

                print(f"Today's Menu:")
                print(f"Most Voted Food Item: {food_item_name} (Food Item ID: {food_item_id})")
                print(f"Votes Received: {vote_count}")
                response = {
                    'foodItemID': food_item_id,
                    'itemName': food_item_name,
                    'voteCount': vote_count
                }

                j_menu = json.dumps(response)
                return j_menu

            else:
                error_msg = "No votes recorded for today yet."
                return error_msg
        except Exception as e:
            print(f"Error fetching today's menu: {e}")

        finally:
            cursor.close()
            connection.close()

    def get_ratings(self):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # SQL query to join Feedback and FoodItem tables
            query = """
                SELECT Feedback.foodItemID, FoodItem.itemName, Feedback.rating, Feedback.comment
                FROM Feedback
                JOIN FoodItem ON Feedback.foodItemID = FoodItem.foodItemID
            """
            cursor.execute(query)
            ratings_data = cursor.fetchall()

            # Prepare the results in a structured format
            ratings = []
            for row in ratings_data:
                ratings.append({
                    'foodItemID': row[0],
                    'itemName': row[1],
                    'rating': row[2],
                    'comment': row[3]
                })
            # self.pretty_print_ratings(ratings)
            cursor.close()
            connection.close()
            j_ratings = json.dumps(ratings)
            return j_ratings

        except Exception as e:
            error_message = f"Error fetching ratings: {e}"
            print(error_message)
            return []

    def remove_meal(self, meal_id):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM FoodItem WHERE foodItemID = %s", (meal_id,))
        connection.commit()
        cursor.close()
        connection.close()
        employee_ids = get_all_employee_ids()
        for employee_id in employee_ids:
            add_notification(employee_id, f"Meal id: '{meal_id}' removed successfully by the admin.")
        return f"Meal with ID '{meal_id}' removed successfully."
