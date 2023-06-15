import pandas as pd
import os

data_dir = './data'
if not os.path.isdir(data_dir):
    data_dir = '../data'

original_directory = "original"
generated_directory = "generated"
books_file = "BX-Books.csv"
users_file = "BX-Users.csv"
books_ratings_file = "BX-Book-Ratings.csv"
user_similarity_by_pearson_correlation = "user_similarity_by_pearson_correlation.csv"

csv_settings = {
    "encoding": 'latin-1',
    "sep": ';',
    "quotechar": '"',
    "escapechar": '\\'
}


def get_dataset_path(origin, file_name):
    return os.path.join(data_dir, origin, file_name)


def read_csv(file_name, **kwargs):
    generated_path = get_dataset_path(generated_directory, file_name)
    if os.path.isfile(generated_path):
        return pd.read_csv(generated_path, **csv_settings, **kwargs)

    original_path = get_dataset_path(original_directory, file_name)
    if os.path.isfile(original_path):
        return pd.read_csv(original_path, **csv_settings, **kwargs)

    return None


def write_csv(df, file_name):
    return df.to_csv(get_dataset_path(generated_directory, file_name), **csv_settings)


def get_books():
    return read_csv(books_file)


def get_users():
    return read_csv(users_file)


def get_book_ratings(rating_count=500000):
    ratings = read_csv(books_ratings_file)
    grouped = ratings.groupby('User-ID').agg(number_of_ratings=('User-ID', 'count')).reset_index()

    ratings = pd.merge(ratings, grouped, on='User-ID', how='inner')
    ratings = ratings.sort_values('number_of_ratings', ascending=False)

    return ratings.head(rating_count)
