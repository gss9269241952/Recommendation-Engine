from database.database import get_db_connection
import datetime
class EmployeeDatabase:
    def __init__(self):
        self.connection = get_db_connection()
        self.cursor = self.connection.cursor()

    def get_feedback_meal(self):
        self.cursor.execute("""
            SELECT foodItemID, rating, comment,category
            FROM Feedback
        """)
        feedbacks = self.cursor.fetchall()
        return feedbacks

    def store_vote_response(self,food_item_id,user_id):
        today = datetime.date.today()
        self.cursor.execute("""
                INSERT INTO Votes (date, foodItemID,userID)
                VALUES (%s, %s,%s)
                
            """, (today, food_item_id,user_id),)
        self.connection.commit()
        return True

    def give_feedback(self,user_id,meal_id, rating, comment):
        self.cursor.execute("INSERT INTO Feedback (userID, foodItemID, rating, comment) VALUES (%s, %s, %s, %s)",
                           (user_id, meal_id, rating, comment))
        self.connection.commit()
        return True

    def get_today_menu(self):
        self.cursor.execute("""
                SELECT Votes.foodItemID, FoodItem.itemName, COUNT(*) as vote_count, FoodItem.category 
                FROM Votes
                JOIN FoodItem ON Votes.foodItemID = FoodItem.foodItemID
                WHERE DATE(Votes.date) = CURDATE() - INTERVAL 1 DAY
                GROUP BY Votes.foodItemID
                ORDER BY vote_count DESC
                LIMIT 1
            """)
        result = self.cursor.fetchone()
        return result

    def notifications(self,user_id):
        self.cursor.execute(
                "SELECT notificationID, message FROM notification WHERE userID = %s AND is_viewed = 0 ORDER BY date DESC LIMIT 10",
                (user_id,))
        notifications = self.cursor.fetchall()
        return notifications

    def viewed_notification(self,user_id,notification_ids):
        self.cursor.execute(
                    f"UPDATE notification SET is_viewed = 1 WHERE userID = %s AND notificationID IN ({notification_ids})",
                    (user_id,))
        self.connection.commit()

    def get_detailed_feedback_discard_item(self,user_id):
        self.cursor.execute("""
            SELECT notificationID, message 
            FROM Notification 
            WHERE userID = %s AND message LIKE 'We are trying to improve your experience with%'
        """, (user_id,))
        notifications = self.cursor.fetchall()
        return notifications

    def get_food_id(self,food_item_name):
        self.cursor.execute("""
                SELECT foodItemID 
                FROM FoodItem 
                WHERE itemName = %s
            """, (food_item_name,))
        result = self.cursor.fetchone()
        return result

    def update_profile(self,user_id,profile_data):
        self.cursor.execute("""
            INSERT INTO EmployeeProfile (userID, dietPreference, spiceLevel, cuisinePreference, sweetTooth)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                dietPreference = VALUES(dietPreference),
                spiceLevel = VALUES(spiceLevel),
                cuisinePreference = VALUES(cuisinePreference),
                sweetTooth = VALUES(sweetTooth)
        """, (
        user_id, profile_data['diet_preference'], profile_data['spice_level'], profile_data['cuisine_preference'],
        profile_data['sweet_tooth']))
        self.connection.commit()
        return True


    def recommend_meaals(self):
        self.cursor.execute("""
                   SELECT foodItemID, rating, comment
                   FROM Feedback
               """)
        feedbacks = self.cursor.fetchall()
        return feedbacks




