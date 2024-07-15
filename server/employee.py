from server.database import get_db_connection
import datetime
import numpy as np
import json
from server.utils import get_top_meals_by_category,get_food_item_profile_data,get_user_profile_data

class Employee:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role
    #FUNCTION FOR RECOMMEND_MEALS
    def recommend_meaals(self):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Fetch meal ratings and comments from the feedback table
            cursor.execute("""
                SELECT foodItemID, rating, comment
                FROM Feedback
            """)
            feedbacks = cursor.fetchall()

            # Dictionary to hold the aggregated data
            meal_data = {}
            for foodItemID, rating, comment in feedbacks:
                if foodItemID not in meal_data:
                    meal_data[foodItemID] = {'ratings': [], 'comments': []}
                meal_data[foodItemID]['ratings'].append(rating)
                meal_data[foodItemID]['comments'].append(comment)

            # Calculate average ratings and sentiment scores
            meal_scores = []
            for meal_id, data in meal_data.items():
                ratings = data['ratings']
                comments = data['comments']

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
                    'recommendation_score': recommendation_score
                })

            # Sort meals by recommendation score and return top 5
            top_meals = sorted(meal_scores, key=lambda x: x['recommendation_score'], reverse=True)[:5]


            # Convert top_meals to JSON string
            top_meals_json = json.dumps(top_meals)
            cursor.close()
            connection.close()
            return top_meals_json

        except Exception as e:
            print(f"Error recommending meals: {e}")
            return []

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
            # Sort meals by recommendation score and return top 5
            top_meals_by_category = get_top_meals_by_category(meal_scores)
            # Convert top_meals to JSON string
            top_meals_json = json.dumps(top_meals_by_category)
            cursor.close()
            connection.close()
            return top_meals_json
        except Exception as e:
            print(f"Error recommending meals: {e}")
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

    def vote_for_meal(self):
        user_id = self.user_id
        top_recommendations = self.recommend_meals()

        j_top_recommendations = json.loads(top_recommendations)

        try:
            # Step 1: Fetch user profile data
            user_profile = get_user_profile_data(user_id)

            # Step 2: Fetch food item profile data
            meal_ids = [meal['meal_id'] for category, meals in j_top_recommendations.items() for meal in meals]
            food_item_profiles = get_food_item_profile_data(meal_ids)

            # Step 3: Prepare the recommendations list with added food item profile data
            recommendations = []
            index = 1
            for category, meals in j_top_recommendations.items():
                for meal in meals:
                    food_item_profile = food_item_profiles[meal['meal_id']]
                    recommendations.append({
                        'index': index,
                        'meal_id': meal['meal_id'],
                        'recommendation_score': meal['recommendation_score'],
                        'Category': meal['Category'],
                        'diet_preference': food_item_profile['dietPreference'],
                        'spice_level': food_item_profile['spiceLevel'],
                        'cuisine_preference': food_item_profile['cuisinePreference'],
                        'sweet_tooth': food_item_profile['sweetTooth']
                    })
                    index += 1

            # Step 4: Sort the recommendations based on user profile
            def sort_key(recommendation):
                score = 0
                if recommendation['diet_preference'] == user_profile['dietPreference']:
                    score += 3
                if recommendation['spice_level'] == user_profile['spiceLevel']:
                    score += 2
                if recommendation['cuisine_preference'] == user_profile['cuisinePreference']:
                    score += 2
                if recommendation['sweet_tooth'] == user_profile['sweetTooth']:
                    score += 1
                return score

            recommendations.sort(key=sort_key, reverse=True)
            print("recommendations_sorted_based_on_profile", recommendations)
            return json.dumps({
                'status': 'success',
                'recommendations': recommendations
            })
        except Exception as e:
            print("Error in generating recommendations: ", str(e))
            return json.dumps({
                'status': 'failure',
                'error': str(e)
            })

    def store_vote(self, food_item_id,user_id):
        try:
            # Insert or update the vote in the Vote table
            connection = get_db_connection()
            cursor = connection.cursor()

            today = datetime.date.today()
            cursor.execute("""
                INSERT INTO Votes (date, foodItemID,userID)
                VALUES (%s, %s,%s)
                
            """, (today, food_item_id,user_id),)

            connection.commit()
            cursor.close()
            connection.close()
            return f"Voted Successfully for foodItemID : {food_item_id}!!!"


        except Exception as e:
            print(f"Error storing vote: {e}")


    def fetch_item_name(self, food_item_id):
        # Dummy method to fetch item name from FoodItem table based on foodItemID
        # Replace with actual logic to fetch item name
        return "Dummy Item Name"

    def give_feedback(self, meal_id, rating, comment):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Feedback (userID, foodItemID, rating, comment) VALUES (%s, %s, %s, %s)",
                           (self.user_id, meal_id, rating, comment))
            print("in give employee/feedback")
            connection.commit()
            cursor.close()
            connection.close()
            return f"Feedback for meal ID {meal_id} submitted successfully."

        except Exception as e:
            return f"Error submitting feedback: {e}"

    def get_notifications(self):
        # Retrieve notifications for the employee
        pass

    def get_today_menu(self):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Query to find the most voted food item for today
            cursor.execute("""
                SELECT Votes.foodItemID, FoodItem.itemName, COUNT(*) as vote_count, FoodItem.category 
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
                category = result[3]

                print(f"Today's Menu:")
                print(f"Most Voted Food Item: {food_item_name} (Food Item ID: {food_item_id}) Category: {category}")
                print(f"Votes Received: {vote_count}")

                return f"""Today's Menu:
Most Voted Food Item: {food_item_name} Food Item ID: {food_item_id} Category: {category}
Votes Received: {vote_count}
                """
            else:
                error_msg = "No votes recorded for today yet."
                return error_msg
        except Exception as e:
            print(f"Error fetching today's menu: {e}")

        finally:
            cursor.close()
            connection.close()

    def notification(self, user_id):
        connection = get_db_connection()
        cursor = connection.cursor()
        notifications = []

        try:
            cursor.execute(
                "SELECT notificationID, message FROM notification WHERE userID = %s AND is_viewed = 0 ORDER BY date DESC LIMIT 10",
                (user_id,))
            notifications = cursor.fetchall()

            if notifications:
                notification_ids = ','.join(str(n[0]) for n in notifications)
                cursor.execute(
                    f"UPDATE notification SET is_viewed = 1 WHERE userID = %s AND notificationID IN ({notification_ids})",
                    (user_id,))
                connection.commit()
            else:
                return "No new notifications."

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()

        j_notifications = json.dumps([n[1] for n in notifications])
        return j_notifications

    import mysql.connector

    def get_detailed_feedback_discard_item(self, user_id):
        connection = get_db_connection()
        cursor = connection.cursor()
        # Step 1: Retrieve notifications related to detailed feedback for the given user
        cursor.execute("""
            SELECT notificationID, message 
            FROM Notification 
            WHERE userID = %s AND message LIKE 'We are trying to improve your experience with%'
        """, (user_id,))
        notifications = cursor.fetchall()


        if not notifications:
            print("No detailed feedback requests found.")
            return json.dumps([])  # Return an empty list if no notifications are found

        food_item_list = []

        for notification in notifications:

            message = notification[1]



            # Extract the food item name from the message
            food_item_name = message.split("with")[1].split(".")[0].strip()
            # Fetch the foodItemID using the food item name
            cursor.execute("""
                SELECT foodItemID 
                FROM FoodItem 
                WHERE itemName = %s
            """, (food_item_name,))
            result = cursor.fetchone()

            if result:
                food_item_id = result[0]
                food_item_list.append({
                    "foodItemID": food_item_id,
                    "foodItemName": food_item_name
                })

        connection.commit()
        cursor.close()
        connection.close()
        return json.dumps(food_item_list)

####complexity 2
    def update_profile(self, profile_data):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO EmployeeProfile (userID, dietPreference, spiceLevel, cuisinePreference, sweetTooth)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                dietPreference = VALUES(dietPreference),
                spiceLevel = VALUES(spiceLevel),
                cuisinePreference = VALUES(cuisinePreference),
                sweetTooth = VALUES(sweetTooth)
        """, (
        self.user_id, profile_data['diet_preference'], profile_data['spice_level'], profile_data['cuisine_preference'],
        profile_data['sweet_tooth']))

        connection.commit()
        cursor.close()
        connection.close()
        return json.dumps({'status': 'success', 'message': 'Profile updated successfully.'})

