import flask
import io
import numpy as np
import numpy.testing
import os
import random
import requests
import scipy.io
from shutil import rmtree
import simplejson
import unittest

from ..app import app


class TestDataSaver(unittest.TestCase):

    def setUp(self):
        self.filename = os.path.join(os.path.dirname(__file__), 'matrix.txt')
        self.app = app.test_client()
        app.config['TESTING'] = True
        self.managed_account_id = random.randint(0, 1000)
        self.path = 'data/{}'.format(self.managed_account_id)
        matrix_file = open(self.filename, 'rb')
        data = {
            'm_graph_id': '894324',
            'managed_account_id': str(self.managed_account_id),
            'common_tweets_file': (matrix_file, 'common_tweets.txt'),
            'hashtags_tweets': simplejson.dumps([
                32, 21, 53, 23, 54, 82, 10, 32, 92,
                12, 4, 65, 93, 69, 23, 53]),
            'hashtags_indexed_array': simplejson.dumps([
                'casaleggio', 'pd', 'governo', 'italia', 'alfano', 'bersani',
                'farage', 'letta', 'berlusconi', 'grillo', 'boschi', 'm5s',
                'renzi', 'napolitano', 'salvini', 'vinciamonoi']),
        }
        # requests.post('http://localhost:5000/matrix', data=data, files=files)
        self.app.post('http://localhost:5000/matrix', data=data)

    def test_directories_are_created(self):
        self.assertTrue(os.path.exists(self.path))
        self.assertTrue(os.path.exists(self.path+'/common_tweets'))

    def test_saved_matrix(self):
        original_matrix = scipy.io.mmread(self.filename).toarray()
        saved_matrix = np.load(self.path+'/common_tweets/matrix.npy')
        numpy.testing.assert_array_equal(original_matrix, saved_matrix)

    def tearDown(self):
        # self.matrix_file.close()
        rmtree(self.path, ignore_errors=True)
        pass


if __name__ == '__main__':
    unittest.main()
