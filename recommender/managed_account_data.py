import numpy as np
import os
import scipy.io
import simplejson


class ManagedAccountData(object):

    def __init__(self, hashtagify_id, common_tweets_matrix,
                 hashtag_from_index, hashtags_tweets):
        self.hashtagify_id = hashtagify_id
        self.common_tweets_matrix = common_tweets_matrix
        self.hashtag_from_index = hashtag_from_index
        self.hashtags_tweets = hashtags_tweets
        self._create_index_from_hashtag()

    def _create_index_from_hashtag(self):
        self.index_from_hashtag = dict(
            (h, i) for i, h in enumerate(self.hashtag_from_index))

    def _get_data_dir(self):
        return 'data'

    @property
    def file_path(self):
        return '{}/{}'.format(self._get_data_dir(), self.hashtagify_id)

    @classmethod
    def create_from_raw_data(
            cls, hashtagify_id: int, common_tweets_matrix_file: 'file-like',
            hashtags_names: list, hashtags_tweets: list) -> 'ManagedAccountData':
        """Instantiate from raw post data and save to disk."""
        common_tweets_matrix = scipy.io.mmread(common_tweets_matrix_file).toarray()
        self = cls(hashtagify_id, common_tweets_matrix,
                   hashtags_names, hashtags_tweets)
        self._save_to_disk()
        return self

    @classmethod
    def load_from_disk(cls, hashtagify_id: int) -> 'ManagedAccountData':
        path = 'data/{}'.format(hashtagify_id)
        matrix = np.load(path + '/matrix.npy')
        with open(path+'/data.json') as inp:
            data = simplejson.load(inp)
        return cls(hashtagify_id, matrix,
                   data['hashtags_names'], data['hashtags_tweets'])

    def _save_to_disk(self):
        os.mkdir(self.file_path)
        os.mkdir(self.file_path+'/common_tweets')
        data = {
            'hashtags_names': self.hashtag_from_index,
            'hashtags_tweets': self.index_from_hashtag,
        }
        np.save(
            self.file_path+'/common_tweets/matrix.npy',
            self.common_tweets_matrix)
        with open(self.file_path+'/common_tweets/data.json', 'w') as out:
            simplejson.dump(data, out)
