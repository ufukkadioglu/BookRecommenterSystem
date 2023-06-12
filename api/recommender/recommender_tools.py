import pandas as pd
from api.recommender.data_tools import get_books, get_book_ratings, user_similarity_by_pearson_correlation, read_csv, \
    write_csv
import os.path


def get_books_with_ratings():
    ratings = get_book_ratings()
    books = get_books()
    books_with_ratings = pd.merge(ratings, books, on='ISBN', how='inner')
    return books_with_ratings


def get_normalized_rating_matrix(agg_ratings):
    # crate user book matrix
    user_book_matrix = agg_ratings.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')

    # normalize ratings, e.g. subtract average rating of each user from their ratings
    user_book_matrix = user_book_matrix.subtract(user_book_matrix.mean(axis=1), axis='rows')

    return user_book_matrix


def get_user_similarity_matrix(user_book_matrix, similarity_type="pearson"):
    if similarity_type != "pearson":
        raise NotImplementedError

    if os.path.isfile(user_similarity_by_pearson_correlation):
        print("User similarity matrix exists on file, will not recalculate")
        user_similarity = read_csv(user_similarity_by_pearson_correlation).set_index('User-ID')
        user_similarity = user_similarity.rename({c: int(c) for c in user_similarity.columns}, axis='columns')
        return user_similarity

    # User similarity matrix using Pearson correlation
    user_similarity = user_book_matrix.T.corr()

    write_csv(user_similarity, user_similarity_by_pearson_correlation)

    return user_similarity


def get_top_n_similar_books(similar_users, similar_user_books, number_of_books_to_recommend):
    # A dictionary to store item scores
    item_score = {}

    # Loop through items
    for i in similar_user_books.columns:
        # Get the ratings for book i
        book_rating = similar_user_books[i]
        # Create a variable to store the score
        total = 0
        # Create a variable to store the number of scores
        count = 0
        # Loop through similar users
        for u in similar_users.index:
            # If the book has rating
            if not pd.isna(book_rating[u]):
                # Score is the sum of user similarity score multiply by the book rating
                score = similar_users[u] * book_rating[u]
                # Add the score to the total score for the book so far
                total += score
                # Add 1 to the count
                count += 1
        # Get the average score for the item
        item_score[i] = total / count
    # Convert dictionary to pandas dataframe
    item_score = pd.DataFrame(item_score.items(), columns=['ISBN', 'ScorePrediction'])

    # Sort the books by score
    ranked_item_score = item_score.sort_values(by='ScorePrediction', ascending=False)

    return ranked_item_score.head(number_of_books_to_recommend)


def get_user_similarity(books_with_ratings):
    # find number of ratings and rate count
    agg_ratings = books_with_ratings.groupby('ISBN').agg(mean_rating=('Book-Rating', 'mean'),
                                                         number_of_ratings=('Book-Rating', 'count')).reset_index()

    agg_ratings = pd.merge(books_with_ratings, agg_ratings[['ISBN']], on='ISBN', how='inner')

    user_book_matrix = get_normalized_rating_matrix(agg_ratings)

    user_similarity = get_user_similarity_matrix(user_book_matrix)

    return user_book_matrix, user_similarity


def user_based_collaborative_filtering(picked_user_id,
                                       number_of_books_to_recommend=10,
                                       number_of_similar_users=10,
                                       user_similarity_threshold=0.1):
    books_with_ratings = get_books_with_ratings()

    user_book_matrix, user_similarity = get_user_similarity(books_with_ratings)

    if picked_user_id not in user_similarity.columns:
        try:
            picked_user_id = int(picked_user_id)

            if picked_user_id not in user_similarity.columns:
                return "User not found"
        except ValueError:
            return "User not found (tried casting)"

    # remove picked user
    user_similarity.drop(index=picked_user_id, inplace=True)

    # Get top n similar users
    similar_users = user_similarity[user_similarity[picked_user_id] > user_similarity_threshold][
                        picked_user_id].sort_values(ascending=False)[:number_of_similar_users]

    # get the books which picked user already rated
    picked_userid_read = user_book_matrix[user_book_matrix.index == picked_user_id].dropna(axis=1, how='all')

    # collect books from similar users
    similar_user_books = user_book_matrix[user_book_matrix.index.isin(similar_users.index)].dropna(axis=1, how='all')

    # remove the books which are already rated by picked user
    similar_user_books.drop(picked_userid_read.columns, axis=1, inplace=True, errors='ignore')

    recommended_books = get_top_n_similar_books(similar_users, similar_user_books, number_of_books_to_recommend)

    books = get_books()

    recommended_books = pd.merge(recommended_books, books, on='ISBN', how='left')[
        ['ISBN', 'ScorePrediction', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher',
         'Image-URL-S']].rename({'ISBN': 'isbn',
                                 'ScorePrediction': 'scorePrediction',
                                 'Book-Title': 'bookTitle',
                                 'Book-Author': 'bookAuthor',
                                 'Year-Of-Publication': 'yearOfPublication',
                                 'Publisher': 'publisher',
                                 'Image-URL-S': 'imageUrl'
                                 }, axis='columns')

    return recommended_books


if __name__ == "__main__":
    books_to_recommend = user_based_collaborative_filtering(
        picked_user_id=11676)  # 11676, 16795, 35859, 52584
    print(books_to_recommend)
