from flask import Flask, request
import json
from api.recommender.recommender_tools import get_user_similarity, user_based_collaborative_filtering, \
    get_books_with_ratings

app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/getUsers')
def get_users():
    books_with_ratings = get_books_with_ratings()
    user_book_matrix, user_similarity = get_user_similarity(books_with_ratings)
    user_ids = user_book_matrix.index.tolist()

    return json.dumps({
        "user_ids": user_ids
    })


@app.route('/getRecommendedBooks')
def get_recommended_books():
    picked_user_id = request.args.get('user_id')
    if not picked_user_id:
        return "User id is required"

    books_to_recommend = user_based_collaborative_filtering(picked_user_id=picked_user_id)

    if books_to_recommend is None or books_to_recommend.empty:
        return "Could not recommend books"

    return f"""{{
        "books_to_recommend": {books_to_recommend.to_json(orient="records")}
    }}"""


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
