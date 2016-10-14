#! /usr/bin/env python3

from flask import Flask, jsonify, request

from recommender import HashtagRecommender


app = Flask(__name__)


@app.route('/recommend', methods=['POST'])
def recommend():
    recommender = HashtagRecommender()
    recommender.go(request.json['username'], request.json['hashtags'])
    return jsonify({'ciao': [1, 2]})
    pass


if __name__ == '__main__':
    app.run(debug=True)
