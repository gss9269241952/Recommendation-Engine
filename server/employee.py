from server.database import get_db_connection
import datetime
import numpy as np
import json

class Employee:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role
    #FUNCTION FOR RECOMMEND_MEALS
    def recommend_meals(self):
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
        user_id =self.user_id
        top_recommendations = self.recommend_meals()

        j_top_recommendations = json.loads(top_recommendations)
        j_top_recommendation = j_top_recommendations[:3]
        print(j_top_recommendation)
        try:
            print("\n=== Today's Top Meal Recommendations ===")
            print("Please vote for your preferred meal by entering the number:")
            print("========================================\n")

            for idx, meal in enumerate(j_top_recommendation, start=1):
                print(
                    f"{idx}. Meal ID: {meal['meal_id']}, Recommendation Score: {meal['recommendation_score']}")

            selected_option = int(input("\nEnter your choice (1-3): "))
            selected_meal = j_top_recommendation[selected_option - 1]
            print(selected_meal)
            # Store the vote in the Vote table
            self.store_vote(selected_meal['meal_id'],user_id)

        except (IndexError, ValueError) as e:
            print(f"Invalid input. Please enter a valid number between 1 and 3.")
            print(f"Error details: {e}")
        response_message = " "
        return response_message
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
            print(f"Voted Successfully for foodItemID : {food_item_id}!!!")


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

                return f"""({
                    'foodItemID': food_item_id,
                    'itemName': food_item_name,
                    'voteCount': vote_count
                })"""
            else:
                error_msg = "No votes recorded for today yet."
                return error_msg
        except Exception as e:
            print(f"Error fetching today's menu: {e}")

        finally:
            cursor.close()
            connection.close()
