from database.database import get_db_connection
import json

from datetime import datetime
from server.utils import add_notification,get_all_employee_ids


class Admin:
    def __init__(self, name, role):
        # self.user_id = user_id
        self.name = name
        self.role = role

    def add_meal(self, meal_name, price, availability,category, diet_preference, spice_level, cuisine_preference, sweet_tooth):
        # print("called add_meal")
        connection = get_db_connection()
        cursor = connection.cursor()
        availability = availability.lower() == 'yes'
        current_datetime = datetime.now()


        cursor.execute(
            "INSERT INTO FoodItem (itemName, price, availability, date,category) VALUES (%s, %s, %s, %s, %s)",
            (meal_name, price, availability, current_datetime, category)
        )

        cursor.execute("SELECT LAST_INSERT_ID()")      # Get the newly inserted FoodItem
        food_item_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO FoodItemProfile (foodItemID, dietPreference, spiceLevel, cuisinePreference, sweetTooth)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (food_item_id, diet_preference, spice_level, cuisine_preference, sweet_tooth)
        )
        connection.commit()
        cursor.close()
        connection.close()
        employee_ids = get_all_employee_ids()
        for employee_id in employee_ids:
            add_notification(employee_id, f"New meal with name {meal_name} , price : {price} has been added by the admin.")
        return f"Meal '{meal_name}' added successfully."

    def remove_meal(self, meal_id):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM FoodItem WHERE foodItemID = %s", (meal_id,))
        connection.commit()
        cursor.close()
        connection.close()
        employee_ids = get_all_employee_ids()
        for employee_id in employee_ids:
            add_notification(employee_id,f"Meal id: '{meal_id}' removed successfully by the admin.")
        return f"Meal with ID '{meal_id}' removed successfully."

    def update_meal(self, meal_id, meal_name=None, price=None, availability=None):
        connection = get_db_connection()
        cursor = connection.cursor()

        if meal_name:
            cursor.execute("UPDATE FoodItem SET itemName = %s WHERE foodItemID = %s", (meal_name, meal_id))
        if price:
            cursor.execute("UPDATE FoodItem SET price = %s WHERE foodItemID = %s", (price, meal_id))
        if availability:
            availability_bool = availability.lower() == 'yes'
            cursor.execute("UPDATE FoodItem SET availability = %s WHERE foodItemID = %s", (availability_bool, meal_id))

        connection.commit()
        cursor.close()
        connection.close()
        employee_ids = get_all_employee_ids()
        for employee_id in employee_ids:
            add_notification(employee_id, f"Meal id: '{meal_id}' updated successfully by the admin.")
        return f"Meal with ID '{meal_id}' updated successfully."

    def change_price(self, meal_id, new_price):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("UPDATE FoodItem SET price = %s WHERE foodItemID = %s", (new_price, meal_id))
        connection.commit()
        cursor.close()
        connection.close()
        employee_ids = get_all_employee_ids()
        for employee_id in employee_ids:
            add_notification(employee_id, f"Price for meal with ID '{meal_id}' changed to {new_price}.")
        return f"Price for meal with ID '{meal_id}' changed to {new_price}."

    def get_menu(self):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # SQL query to fetch all menu items
            query = """
                SELECT foodItemID, itemName,  availability, category, price
                FROM FoodItem
            """
            cursor.execute(query)
            menu_data = cursor.fetchall()
            cursor.close()
            connection.close()
            menu_data_serializable = [
                {
                    "foodItemID": item[0],
                    "itemName": item[1],
                    "availability": item[2],
                    "category": item[3],
                    "price": float(item[4])  # Convert Decimal to float
                }
                for item in menu_data
            ]

            # Serialize to JSON
            j_menu = json.dumps(menu_data_serializable)
            print("worked", j_menu)
            return j_menu

        except Exception as e:
            error_message = f"Error fetching menu: {e}"
            print(error_message)
            return []
    def check_availability(self, meal_id):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT availability FROM FoodItem WHERE foodItemID = %s", (meal_id,))
        availability = cursor.fetchone()
        print("cursor.fetchone",cursor.fetchone())
        cursor.close()
        connection.close()
        return f"Meal with ID '{meal_id}' is {'available' if availability else 'not available'}."

    # Additional methods for updating, deleting meals, and changing prices...


# if __name__ == "__main__":
#     admin = Admin("gaurav", "admin")
#
#     # Adding a meal
#     result = admin.add_meal("Pasta", 12.5, "yes")
#     print(result)
#
#     # Removing a meal
#     result = admin.remove_meal(1)
#     print(result)
#
#     # Updating a meal
#     result = admin.update_meal(2, meal_name="Spaghetti", price=13.0, availability="no")
#     print(result)
#
#     # Changing price
#     result = admin.change_price(3, 15.0)
#     print(result)
#
#     # Checking availability
#     result = admin.check_availability(4)
#     print(result)
