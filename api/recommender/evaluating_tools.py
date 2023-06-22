from sklearn.metrics import mean_absolute_error as mae, mean_squared_error as mse
import pandas as pd


class RecommenderMetrics:
    @staticmethod
    def mean_absolute_error(actual_ratings, predictions):
        return mae(actual_ratings, predictions)

    @staticmethod
    def mean_square_error(actual_ratings, predictions):
        return mse(actual_ratings, predictions)

    @staticmethod
    def root_mean_square_error(actual_ratings, predictions):
        return mse(actual_ratings, predictions, squared=False)

    @staticmethod
    def get_mean_absolute_error_analysis(user_id, book_ratings, recommender_func, sample_size=100):
        sample_ratings_for_user = book_ratings[book_ratings['User-ID'] == user_id].sample(n=sample_size)
        book_ratings = book_ratings.drop(sample_ratings_for_user.index, axis=0)

        score_predictions = recommender_func(picked_user_id=user_id,
                                             number_of_books_to_recommend=999999,
                                             books_with_ratings=book_ratings,
                                             user_similarity_threshold=0)

        prediction_sample_intersection = pd.merge(
            sample_ratings_for_user, score_predictions, how='inner', left_on='ISBN', right_on='isbn')[
            ['isbn', 'Book-Rating', 'score']].rename(
            {
                'Book-Rating': 'actual_rating',
                'score': 'predicted_rating'
            }, axis='columns')

        if prediction_sample_intersection.empty:
            raise Exception(f"Recommender did not recommend any books for the user {user_id}!")

        mean_absolute_error = RecommenderMetrics.mean_absolute_error(
            prediction_sample_intersection['actual_rating'],
            prediction_sample_intersection['predicted_rating'])

        mean_square_error = RecommenderMetrics.mean_square_error(
            prediction_sample_intersection['actual_rating'],
            prediction_sample_intersection['predicted_rating'])

        root_mean_square_error = RecommenderMetrics.root_mean_square_error(
            prediction_sample_intersection['actual_rating'],
            prediction_sample_intersection['predicted_rating'])

        predicted_count = len(prediction_sample_intersection.index)
        sample_count = len(sample_ratings_for_user.index)
        message = f"Predictions include {predicted_count} " \
                  f"of {sample_count} items, unpredicted {sample_count - predicted_count} items are ignored."

        return {
            'mean_absolute_error': mean_absolute_error,
            'mean_square_error': mean_square_error,
            'root_mean_square_error': root_mean_square_error,
            'message': message
        }
