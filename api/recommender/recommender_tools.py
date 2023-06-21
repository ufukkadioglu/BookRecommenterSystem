import pandas as pd
import numpy as np
from api.recommender.data_tools import get_books, get_book_ratings, user_similarity_by_pearson_correlation, read_csv, \
    write_csv


class BaseRecommender:
    column_name_map = {
        'ISBN': 'isbn',
        'ScorePrediction': 'score',
        'Book-Title': 'bookTitle',
        'Book-Author': 'bookAuthor',
        'Year-Of-Publication': 'yearOfPublication',
        'Publisher': 'publisher',
        'Image-URL-S': 'imageUrl',
        'BayesianAverage': 'score',
        'Book-Rating': 'rating'
    }

    @staticmethod
    def get_books_with_ratings():
        # TODO: create generated file not to merge data everytime
        ratings = get_book_ratings()
        books = get_books()
        books_with_ratings = pd.merge(ratings, books, on='ISBN', how='inner')
        return books_with_ratings

    @classmethod
    def recommend(cls, picked_user_id, number_of_books_to_recommend=10):
        raise NotImplementedError


class CollaborativeFiltering(BaseRecommender):
    @staticmethod
    def get_normalized_rating_matrix(agg_ratings):
        # crate user book matrix
        user_book_matrix = agg_ratings.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')

        # normalize ratings, e.g. subtract average rating of each user from their ratings
        user_average_ratings = user_book_matrix.mean(axis=1)
        user_book_matrix = user_book_matrix.subtract(user_average_ratings, axis='rows')

        return user_book_matrix, user_average_ratings

    @staticmethod
    def get_user_similarity_matrix(user_book_matrix, similarity_type="pearson"):
        if similarity_type != "pearson":
            raise NotImplementedError

        user_similarity = read_csv(user_similarity_by_pearson_correlation)

        if user_similarity is not None:
            print("User similarity matrix exists on file, will not recalculate")
            user_similarity = user_similarity.set_index('User-ID')
            user_similarity = user_similarity.rename({c: int(c) for c in user_similarity.columns}, axis='columns')
            return user_similarity

        # User similarity matrix using Pearson correlation
        user_similarity = user_book_matrix.T.corr()

        write_csv(user_similarity, user_similarity_by_pearson_correlation)

        return user_similarity

    @staticmethod
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

    @staticmethod
    def get_user_similarity(books_with_ratings):
        # find number of ratings and rate count
        agg_ratings = books_with_ratings.groupby('ISBN').agg(mean_rating=('Book-Rating', 'mean'),
                                                             number_of_ratings=('Book-Rating', 'count')).reset_index()

        agg_ratings = pd.merge(books_with_ratings, agg_ratings[['ISBN']], on='ISBN', how='inner')

        user_book_matrix, user_average_ratings = CollaborativeFiltering.get_normalized_rating_matrix(agg_ratings)

        user_similarity = CollaborativeFiltering.get_user_similarity_matrix(user_book_matrix)

        return user_book_matrix, user_similarity, user_average_ratings

    @classmethod
    def recommend(cls, picked_user_id, number_of_books_to_recommend=10):
        user_similarity_threshold = 0.3
        number_of_similar_users_to_consider = 10

        books_with_ratings = CollaborativeFiltering.get_books_with_ratings()

        user_book_matrix, user_similarity, user_average_ratings = CollaborativeFiltering.get_user_similarity(
            books_with_ratings)

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
                            picked_user_id].sort_values(ascending=False)[:number_of_similar_users_to_consider]

        # get the books which picked user already rated
        picked_userid_read = user_book_matrix[user_book_matrix.index == picked_user_id].dropna(axis=1, how='all')

        # collect books from similar users
        similar_user_books = user_book_matrix[user_book_matrix.index.isin(similar_users.index)].dropna(axis=1,
                                                                                                       how='all')

        # remove the books which are already rated by picked user
        similar_user_books.drop(picked_userid_read.columns, axis=1, inplace=True, errors='ignore')

        recommended_books = CollaborativeFiltering.get_top_n_similar_books(similar_users, similar_user_books,
                                                                           number_of_books_to_recommend)

        books = get_books()

        recommended_books = pd.merge(recommended_books, books, on='ISBN', how='left')[
            ['ISBN', 'ScorePrediction', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher',
             'Image-URL-S']].rename(BaseRecommender.column_name_map, axis='columns')

        return recommended_books


class PopularityBasedRecommender(BaseRecommender):
    @classmethod
    def recommend(cls, picked_user_id, number_of_books_to_recommend=10):
        book_scores = PopularityBasedRecommender.calculate_bayesian_average()
        books = get_books()

        most_popular = pd.merge(book_scores, books, on='ISBN').sort_values('BayesianAverage', ascending=False).rename(
            BaseRecommender.column_name_map, axis='columns')
        return most_popular.head(number_of_books_to_recommend)

    @staticmethod
    def calculate_bayesian_average():
        # BayesianAverage = w*R + (1 - w)*c

        df = PopularityBasedRecommender.get_user_book_matrix()
        df['v'] = df.count(axis=1)
        m = np.mean(df['v'])
        df['w'] = df['v'] / (df['v'] + m)
        df['R'] = np.mean(df, axis=1)
        c = np.nanmean(df.values.flatten())
        df['BayesianAverage'] = df['w'] * df['R'] + (1 - df['w']) * c
        df = df[['BayesianAverage']].reset_index()

        return df

    @staticmethod
    def get_user_book_matrix():
        books_with_ratings = PopularityBasedRecommender.get_books_with_ratings()
        user_book_matrix = books_with_ratings.pivot_table(index='ISBN', columns='User-ID', values='Book-Rating')
        return user_book_matrix
