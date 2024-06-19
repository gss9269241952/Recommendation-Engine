from server.database import get_db_connection
from datetime import datetime
class Admin:
    def __init__(self, name, role):
        # self.user_id = user_id
        self.name = name
        self.role = role

    def add_meal(self, meal_name, price, availability):
        print("called add_meal")
        connection = get_db_connection()
        cursor = connection.cursor()
        availability = availability.lower() == 'yes'

        # Get current date and time
        current_datetime = datetime.now()

        cursor.execute(
            "INSERT INTO FoodItem (itemName, price, availability, date) VALUES (%s, %s, %s, %s)",
            (meal_name, price, availability, current_datetime)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return f"Meal '{meal_name}' added successfully."

    def remove_meal(self, meal_id):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM FoodItem WHERE foodItemID = %s", (meal_id,))
        connection.commit()
        cursor.close()
        connection.close()
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
        return f"Meal with ID '{meal_id}' updated successfully."

    def change_price(self, meal_id, new_price):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("UPDATE FoodItem SET price = %s WHERE foodItemID = %s", (new_price, meal_id))
        connection.commit()
        cursor.close()
        connection.close()
        return f"Price for meal with ID '{meal_id}' changed to {new_price}."

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
