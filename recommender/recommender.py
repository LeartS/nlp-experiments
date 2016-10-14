import numpy as np
import redis


hashtags_dict = {
    'casa': 0,
    'cucina': 1,
    'camera': 2,
    'sole': 3,
    'mare': 4,
    'blessed': 5,
}
matrix = [
    [0, 10, 9, 2, 3, 6],
    [10, 0, 3, 1, 0, 3],
    [9, 3, 0, 2, 1, 3],
    [2, 1, 2, 0, 12, 5],
    [3, 0, 1, 12, 0, 5],
    [6, 3, 3, 5, 5, 0],
]
total_tweets = [120000, 73200, 84593, 184399, 174503, 4038432]
user_tweets = [60, 42, 27, 23, 32, 42, ]


matrix = np.array(matrix)


class HashtagRecommender(object):

    def __init__(self, n_correlated_hashtags=50, n_best_to_return=5):
        self.N_CORRELATED_HASHTAGS = n_correlated_hashtags
        self.N_BEST_TO_RETURN = n_best_to_return

    def _preload_user_data(self, user):
        # TODO: replace hardcoded data with loading from disk/DB
        self.hashtags_dict = hashtags_dict
        self.matrix = matrix
        self.total_tweets = total_tweets
        self.user_tweets = user_tweets

    def _retrieve_top_related_hashtags(self, hashtag):
        redis_client = redis.StrictRedis()
        return redis_client.zrevrangebyscore(
            'nht.tw.nhts:{}'.format(hashtag), '+inf', 1, start=0,
            num=self.N_CORRELATED_HASHTAGS, withscores=True)

    def go(self, user, hashtags_with_weight=[]):
        self._preload_user_data(user)
        new_hashtags = []
        cell_values = []
        for hashtag, weight in hashtags_with_weight:
            if hashtag not in self.hashtags_dict:
                self.hashtags_dict[hashtag] = len(self.hashtags_dict)
                new_hashtags.append(hashtag)
            for rel_ht, score in self._retrieve_top_related_hashtags(hashtag):
                cell_values.append((hashtag, rel_ht, score))
                if rel_ht not in self.hashtags_dict:
                    new_hashtags.append(rel_ht)
                    self.hashtags_dict[rel_ht] = len(self.hashtags_dict)
        # expand the matrix in a single operation, than fill the new values
        # individually
        # TODO: try scipy sparse matrices, they have methods to fill them
        # exactly like this
        nr, nc = self.matrix.shape
        new_nr, new_nc = nr + len(new_hashtags), nc + len(new_hashtags)
        augmented_matrix = np.zeros((new_nr, new_nc), dtype=np.int)
        augmented_matrix[:nr, :nc] = self.matrix
        for ht1, ht2, score in cell_values:
            augmented_matrix[self.hashtags_dict[ht1]][self.hashtags_dict[ht2]] = score
            augmented_matrix[self.hashtags_dict[ht2]][self.hashtags_dict[ht1]] = score

        # per-row normalization
        # this is not the same normalization as the one in the
        # matrix_normalized_correlation_from_common_tweets method
        # but this should work. I don't remember linear algebra and I'm tired
        normalized_augmented_matrix = augmented_matrix / augmented_matrix.sum(axis=0, keepdims=True)
        weights_vector = np.zeros(new_nr)
        for hashtag, weight in hashtags_with_weight:
            weights_vector[self.hashtags_dict[hashtag]] = weight
        step1 = np.dot(normalized_augmented_matrix, weights_vector)
        step2 = np.dot(normalized_augmented_matrix, step1)
        final_scores = []

        # TODO: super stupido fatto di fretta, inutile andare a guardarsi 10k
        # hashtags per ritornare i migliori N
        for hashtag, index in self.hashtags_dict.items():
            final_scores.append((hashtag, step2[self.hashtags_dict[hashtag]]))
        return {
            'vector': step2,
            'best': sorted(final_scores, key=lambda x: x[1], reverse=True)[:self.N_BEST_TO_RETURN]}
