from server.database import get_db_connection

class Employee:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role

    def vote_meal(self, meal_id):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO votes (user_id, meal_id) VALUES (%s, %s)",
                       (self.user_id, meal_id))
        connection.commit()
        cursor.close()
        connection.close()

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
        # Get today's menu based on votes
        pass
