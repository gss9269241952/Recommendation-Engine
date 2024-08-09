from database.EmployeeDatabase import EmployeeDatabase
import numpy as np
import json
from server.utils import get_top_meals_by_category,get_food_item_profile_data,get_user_profile_data

class Employee:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.emp_db = EmployeeDatabase()

    #FUNCTION FOR RECOMMEND_MEALS

    def recommend_meals(self):
        try:
            feedbacks = self.emp_db.get_feedback_meal()
            meal_data = {}
            for foodItemID, rating, comment,category in feedbacks:
                if foodItemID not in meal_data:
                    meal_data[foodItemID] = {'ratings': [], 'comments': [], 'category': []}
                meal_data[foodItemID]['ratings'].append(rating)
                meal_data[foodItemID]['comments'].append(comment)
                meal_data[foodItemID]['category'].append(category)
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
            top_meals_by_category = get_top_meals_by_category(meal_scores)
            top_meals_json = json.dumps(top_meals_by_category)
            return top_meals_json
        except Exception as e:
            print(f"Error recommending meals: {e}")
            return []
    def calculate_sentiment_score(self, comments):
        positive_keywords = [
            'good', 'great', 'excellent', 'amazing', 'delicious', 'fantastic',
            'wonderful', 'superb', 'impressive', 'brilliant', 'outstanding',
            'magnificent', 'fabulous', 'remarkable', 'exceptional', 'splendid',
            'awesome', 'terrific', 'phenomenal', 'delightful', 'lovely',
            'breathtaking', 'radiant', 'perfect', 'satisfying', 'top-notch',
            'thrilling', 'extraordinary'
        ]

        negative_keywords = [
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'not good', 'not great',
            'disappointing', 'dreadful', 'lousy', 'subpar', 'mediocre', 'unacceptable',
            'unsatisfactory', 'poor quality', 'not amazing', 'not delicious',
            'substandard', 'inferior', 'weak', 'unimpressive', 'regrettable',
            'flawed', 'lackluster', 'dismal', 'unpleasant', 'second-rate',
            'too oily', 'too spicy', 'too salty', 'too bland', 'too sweet',
            'too bitter', 'too sour'
        ]

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
        print("j_top_recommendations", j_top_recommendations)
        try:
            # Step 1: Fetch user profile data
            user_profile = get_user_profile_data(user_id)
            # print("user_profile",user_profile)
            meal_ids = [meal['meal_id'] for category, meals in j_top_recommendations.items() for meal in meals]
            food_item_profiles = get_food_item_profile_data(meal_ids)

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
            if self.emp_db.store_vote_response(food_item_id,user_id):
                return f"Voted Successfully for foodItemID : {food_item_id}!!!"
            else:
                return f"Something went wrong"

        except Exception as e:
            print(f"Error storing vote: {e}")




    def give_feedback(self, meal_id, rating, comment):
        try:
            if self.emp_db.give_feedback(self.user_id,meal_id, rating, comment):
                return f"Feedback for meal ID {meal_id} submitted successfully."
            else:
                return f"Something went wrong"

        except Exception as e:
            return f"Error submitting feedback: {e}"


    def get_today_menu(self):
        try:
            result = self.emp_db.get_today_menu()
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
                error_msg = "No votes recorded Yesterday"
                return error_msg
        except Exception as e:
            print(f"Error fetching today's menu: {e}")

    def notification(self, user_id):
        # connection = get_db_connection()
        # cursor = connection.cursor()
        notifications = []

        try:
            notifications = self.emp_db.notifications(self.user_id)
            if notifications:
                notification_ids = ','.join(str(n[0]) for n in notifications)
                self.emp_db.viewed_notification(self.user_id,notification_ids)
            else:
                return "No new notifications."

        except Exception as e:
            print(f"An error occurred: {e}")

        j_notifications = json.dumps([n[1] for n in notifications])
        return j_notifications

    def get_detailed_feedback_discard_item(self, user_id):
        notifications = self.emp_db.get_detailed_feedback_discard_item(self.user_id)
        if not notifications:
            print("No detailed feedback requests found.")
            return json.dumps([])  # Return an empty list if no notifications are found

        food_item_list = []

        for notification in notifications:

            message = notification[1]

            food_item_name = message.split("with")[1].split(".")[0].strip()
            result = self.emp_db.get_food_id(food_item_name)
            if result:
                food_item_id = result[0]
                food_item_list.append({
                    "foodItemID": food_item_id,
                    "foodItemName": food_item_name
                })
        return json.dumps(food_item_list)

####complexity 2
    def update_profile(self, profile_data):
        if self.emp_db.update_profile(self.user_id, profile_data):
            return json.dumps({'status': 'success', 'message': 'Profile updated successfully.'})
        else:
            return f"Something went wrong"

    def recommend_meaals(self):
        try:
            feedbacks = self.emp_db.recommend_meaals()

            # Dictionary to hold the aggregated data
            meal_data = {}
            for foodItemID, rating, comment in feedbacks:
                if foodItemID not in meal_data:
                    meal_data[foodItemID] = {'ratings': [], 'comments': []}
                meal_data[foodItemID]['ratings'].append(rating)
                meal_data[foodItemID]['comments'].append(comment)
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

            top_meals = sorted(meal_scores, key=lambda x: x['recommendation_score'], reverse=True)[:5]

            top_meals_json = json.dumps(top_meals)
            return top_meals_json

        except Exception as e:
            print(f"Error recommending meals: {e}")
            return []
