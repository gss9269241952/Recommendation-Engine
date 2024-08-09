import hashlib
from database.database import get_db_connection


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


def get_user_profile_data(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print("user_id", user_id)
    cursor.execute("""
        SELECT dietPreference, spiceLevel, cuisinePreference, sweetTooth 
        FROM EmployeeProfile 
        WHERE userID = %s
    """, (user_id,))

    user_profile = cursor.fetchone()

    cursor.close()
    connection.close()

    return user_profile


def get_food_item_profile_data(meal_ids):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    format_strings = ','.join(['%s'] * len(meal_ids))
    cursor.execute(f"""
        SELECT foodItemID, dietPreference, spiceLevel, cuisinePreference, sweetTooth 
        FROM FoodItemProfile 
        WHERE foodItemID IN ({format_strings})
    """, tuple(meal_ids))

    food_item_profiles = cursor.fetchall()

    cursor.close()
    connection.close()

    return {item['foodItemID']: item for item in food_item_profiles}
