#! /usr/bin/env python3

from flask import Flask, request
import simplejson

from .managed_account_data import ManagedAccountData


app = Flask(__name__)


@app.route('/matrix', methods=['POST'])
def save_matrix():
    hashtags_names = simplejson.loads(request.form['hashtags_indexed_array'])
    hashtags_tweets = simplejson.loads(request.form['hashtags_tweets'])
    managed_account_id = int(request.form['managed_account_id'])
    matrix_file = request.files['common_tweets_file']
    ManagedAccountData.create_from_raw_data(
        managed_account_id, matrix_file, hashtags_names, hashtags_tweets)
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
