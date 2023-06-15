from flask import Flask, request
import json
from api.recommender.recommender_tools import CollaborativeFiltering, PopularityBasedRecommender, BaseRecommender

app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/getUsers')
def get_users():
    books_with_ratings = CollaborativeFiltering.get_books_with_ratings()

    # get users from similarity matrix because not all users are considered when collecting ratings
    # (to prevent memory issues)
    user_book_matrix, user_similarity, user_average_ratings = CollaborativeFiltering.get_user_similarity(
        books_with_ratings)
    user_ids = user_book_matrix.index.tolist()

    return json.dumps({
        "user_ids": user_ids
    })


@app.route('/getRecommendedBooks')
def get_recommended_books():
    picked_user_id = request.args.get('user_id')
    if not picked_user_id:
        return "User id is required"

    picked_user_id = int(picked_user_id)

    books_by_collaborating_filtering = CollaborativeFiltering.recommend(picked_user_id=picked_user_id)

    books_by_popularity = PopularityBasedRecommender.recommend(picked_user_id=picked_user_id)

    books_with_ratings = BaseRecommender.get_books_with_ratings()

    return f"""{{
        "collaborative_filtering": {books_by_collaborating_filtering.to_json(orient="records")},
        "popularity_based": {books_by_popularity.to_json(orient="records")}
    }}"""


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
