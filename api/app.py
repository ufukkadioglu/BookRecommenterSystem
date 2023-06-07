from flask import Flask

from api.recommender.data_tools import get_users, get_books
from api.recommender.recommender_tools import get_user_similarity

app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/getSimilarity')
def get_similarity():
    user_book_matrix, user_similarity = get_user_similarity()

    user_ids = user_book_matrix.index.tolist()
    books = get_books()

    return f"""{{
        "user_book_matrix": {user_book_matrix.to_json(orient="records")},
        "user_similarity": {user_similarity.to_json(orient="records")},
        "user_ids": [{','.join(['"%s"' % u for u in user_ids])}],
        "books": {books.to_json(orient="records")}
    }}"""


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
