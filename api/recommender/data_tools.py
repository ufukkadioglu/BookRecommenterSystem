import pandas as pd
import os

data_dir = './data'
if not os.path.isdir(data_dir):
    data_dir = '../data'

books_file_path = f"{data_dir}/original/BX-Books.csv"
users_file_path = f"{data_dir}/original/BX-Users.csv"
books_ratings_file_path = f"{data_dir}/original/BX-Book-Ratings.csv"
user_similarity_by_pearson_correlation = f"{data_dir}/generated/user_similarity_by_pearson_correlation.csv"


def read_csv(path, **kwargs):
    return pd.read_csv(path, encoding='latin-1', sep=';', quotechar='"', escapechar='\\', **kwargs)


def write_csv(df, path):
    return df.to_csv(path, encoding='latin-1', sep=';', quotechar='"', escapechar='\\')


def get_books():
    return read_csv(books_file_path)


def get_users():
    return read_csv(users_file_path)


def get_book_ratings(rating_count=100000):
    ratings = read_csv(books_ratings_file_path)
    grouped = ratings.groupby('User-ID').agg(number_of_ratings=('User-ID', 'count')).reset_index()

    ratings = pd.merge(ratings, grouped, on='User-ID', how='inner')
    ratings = ratings.sort_values('number_of_ratings', ascending=False)

    return ratings.head(rating_count)
