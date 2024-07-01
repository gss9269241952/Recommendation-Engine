def pretty_print_ratings(ratings):
    print("\nRatings and Comments for Food Items:\n")
    print("|| {:^10} || {:^30} || {:^10} || {:^50} ||".format("Food Item ID", "Food Item Name", "Rating", "Comment"))
    print("||" + "-" * 14 + "++" + "-" * 34 + "++" + "-" * 14 + "++" + "-" * 52 + "||")
    for rating in ratings:
        print(
            f"|| {rating['foodItemID']:>12} || {rating['itemName']:^30} || {rating['rating']:>10} || {rating['comment']:^50} ||")
    print("||" + "-" * 14 + "++" + "-" * 34 + "++" + "-" * 14 + "++" + "-" * 52 + "||")

def pretty_print_recommend_meals(meals):
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