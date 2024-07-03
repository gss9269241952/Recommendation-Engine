import hashlib
from server.database import get_db_connection
from datetime import datetime
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_notification(user_id, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notification (userID, message) VALUES (%s, %s)", (user_id, message))
    conn.commit()
    conn.close()

def get_all_employee_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT userID FROM user WHERE role = 'Employee'")
    employee_ids = cursor.fetchall()
    conn.close()
    return [employee_id[0] for employee_id in employee_ids]


def get_top_meals_by_category(meal_scores):
    from collections import defaultdict

    # Step 1: Group meals by category
    categorized_meals = defaultdict(list)
    for meal in meal_scores:
        categorized_meals[meal['Category']].append(meal)

    # Step 2: Sort each category group by recommendation_score in descending order
    top_meals_by_category = {}
    for category, meals in categorized_meals.items():
        sorted_meals = sorted(meals, key=lambda x: x['recommendation_score'], reverse=True)
        top_meals_by_category[category] = sorted_meals[:2]  # Take top 2 meals

    return top_meals_by_category
