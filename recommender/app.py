#! /usr/bin/env python3

from flask import Flask, jsonify, request
import numpy as np
from scipy import io
import simplejson
import os

from recommender import HashtagRecommender


app = Flask(__name__)


@app.route('/matrix', methods=['POST'])
def save_matrix():
    hashtags = simplejson.loads(request.form['hashtags_indexed_array'])
    m_graph_id = int(request.form['m_graph_id'])
    matrix = io.mmread(request.files['common_tweets_file'])
    os.mkdir('{}'.format(m_graph_id))
    data = {'hashtags': hashtags}
    np.save('{}/matrix.npy'.format(m_graph_id), matrix.toarray())
    with open('{}/data.json'.format(m_graph_id), 'w') as out:
        simplejson.dump(data, out)
    return 'ok'


if __name__ == '__main__':
    app.run(debug=True)
