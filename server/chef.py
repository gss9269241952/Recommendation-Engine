from server.database import get_db_connection
import numpy as np
import json
import datetime
class Chef:
    def __init__(self,  role,name):
        # self.user_id = user_id
        self.name = name
        self.role = role

    def pretty_print_recommend_meals(self,meals):
        if not meals:
            print("No meals to display.")
            return

        # Print table header
        print("\nRecommended Meals:\n")
        print("|| {:^10} || {:^12} || {:^15} || {:^22} ||".format("Meal ID", "Avg Rating", "Sentiment Score",
                                                                  "Recommendation Score"))
        print("||" + "-" * 14 + "++" + "-" * 14 + "++" + "-" * 17 + "++" + "-" * 24 + "||")

        # Print each meal row
        for meal in meals:
            print(
                f"|| {meal['meal_id']:>10} || {meal['avg_rating']:^12.1f} || {meal['sentiment_score']:^15.1f} || {meal['recommendation_score']:^22.1f} ||")

        # Print table footer
        print("||" + "-" * 14 + "++" + "-" * 14 + "++" + "-" * 17 + "++" + "-" * 24 + "||")

    #
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
            self.pretty_print_recommend_meals(top_meals)

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

    def broadcast_meals(self):
        try:
            recommended_meals = json.loads(self.recommend_meals())

            connection = get_db_connection()
            cursor = connection.cursor()

            print("\nBroadcasting recommended meals to employees:")
            for meal in recommended_meals:
                foodItemID = meal['meal_id']
                cursor.execute("""
                            select itemName from FoodItem where foodItemID = %s """, (foodItemID,))
                food_item_name = cursor.fetchone()
                print(f"Meal ID: {meal['meal_id']},Food Item Name: {food_item_name[0]} Average Rating: {meal['avg_rating']}, Sentiment Score: {meal['sentiment_score']}")

            # Finalize top 3 meals based on chef's choice (example: first three meals)
            top_meals = recommended_meals[:3]

            # Insert top 3 meals into the Recommendation table


            for meal in top_meals:
                meal_id = meal['meal_id']
                # chef_id = self.user_id
                date = datetime.date.today()
                chef_id = "5"
                cursor.execute("""
                    INSERT INTO Recommendation (date, chefID, foodItemID)
                    VALUES (%s, %s, %s)
                """, (date,chef_id,  meal_id))

                print(f"Meal ID {meal_id} broadcasted to employees.")

            connection.commit()
            cursor.close()
            connection.close()

            # Simulate sending selected items to all employees in their VOTE_FOR_MEAL menu
            response_message = "\nSending selected items to all employees in their VOTE_FOR_MEAL menu..."
            # print(response_message)

            return response_message

        except Exception as e:
            error_message = f"Error broadcasting meals: {e}"
            print(error_message)
            return error_message

    def publish_monthly_report(self):
        # Generate and publish a monthly report
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

                return {
                    'foodItemID': food_item_id,
                    'itemName': food_item_name,
                    'voteCount': vote_count
                }
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
            self.pretty_print_ratings(ratings)
            cursor.close()
            connection.close()
            j_ratings = json.dumps(ratings)
            return j_ratings

        except Exception as e:
            error_message = f"Error fetching ratings: {e}"
            print(error_message)
            return []

    def pretty_print_ratings(self, ratings):
        print("\nRatings and Comments for Food Items:\n")
        print("|| {:^10} || {:^30} || {:^10} || {:^50} ||".format("Food Item ID", "Food Item Name", "Rating", "Comment"))
        print("||" + "-" * 14 + "++" + "-" * 34 + "++" + "-" * 14 + "++" + "-" * 52 + "||")
        for rating in ratings:
            print(f"|| {rating['foodItemID']:>12} || {rating['itemName']:^30} || {rating['rating']:>10} || {rating['comment']:^50} ||")
        print("||" + "-" * 14 + "++" + "-" * 34 + "++" + "-" * 14 + "++" + "-" * 52 + "||")
