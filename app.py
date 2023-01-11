import binascii
import datetime
import json
import logging
import os

import flask
from flask import Flask

from flask_pymongo import PyMongo, MongoClient

from bson.json_util import dumps

from bson.objectid import ObjectId

from flask import jsonify, request

import jwt

from dotenv import load_dotenv

from flask_cors import CORS

app = Flask(__name__)

CORS(app)

load_dotenv('/.env')

client = MongoClient(os.environ.get("DB_CON_STRING"))

db = client.get_database("film_db")


@app.route("/api", methods=['POST'])
def add_film():
    _json = request.json
    title = _json['title']
    desc = _json['description']
    rental_duration = _json['rental_duration']
    rental_rate = _json['rental_rate']
    length = _json['length']
    replacement_cost = _json['replacement_cost']
    rating = _json['rating']
    list_actors = _json['list_actors']
    if 'Authorization' in request.headers:
        try:
            token = request.headers['Authorization'].split(" ")
            auth = apiAuth(token[1])
            # print(auth)
            if 'token' in auth.keys():
                if title and desc and rental_duration and rental_rate and length and replacement_cost and rating and list_actors and request.method == 'PATCH':
                    film = db.film.insert_one({'title': title,
                                               'description': desc,
                                               'rental_duration': rental_duration,
                                               'rental_rate': rental_rate,
                                               'length': length,
                                               'replacement_cost': replacement_cost,
                                               'rating': rating,
                                               'list_actors': list_actors})
                    resp = jsonify("Film Inserted successfully.")
                    resp.status_code = 200
                    if film is None:
                        return not_found()
                    else:
                        return resp
            else:
                return invalid_token()
        except jwt.exceptions.InvalidSignatureError:
            return invalid_token()
        except jwt.exceptions.ExpiredSignatureError:
            return token_expired()
        except binascii.Error:
            return invalid_token()

    else:
        return unauthorised_error()


@app.route("/api", methods=['GET'])
def get_films():
    if 'Authorization' in request.headers:
        try:
            token = request.headers['Authorization'].split(" ")
            auth = apiAuth(token[1])
            # print(auth)
            if 'token' in auth.keys():
                films = db.film.find()
                resp = dumps(films)
                if films is None:
                    return not_found()
                else:
                    return resp
            else:
                return invalid_token()
        except jwt.exceptions.InvalidSignatureError:
            return invalid_token()
        except jwt.exceptions.ExpiredSignatureError:
            return token_expired()
        except jwt.exceptions.DecodeError:
            return invalid_token()

    else:
        return unauthorised_error()


@app.route("/api/<string:fname>", methods=['GET'])
def get_film(fname):
    if 'Authorization' in request.headers:
        try:
            token = request.headers['Authorization'].split(" ")
            auth = apiAuth(token[1])
            # print(auth)
            if 'token' in auth.keys():
                film = db.film.find_one({'title': fname})
                resp = dumps(film)
                if film is None:
                    return not_found()
                else:
                    return resp
            else:
                return invalid_token()
        except jwt.exceptions.InvalidSignatureError:
            return invalid_token()
        except jwt.exceptions.ExpiredSignatureError:
            return token_expired()
        except jwt.exceptions.DecodeError:
            return invalid_token()

    else:
        return unauthorised_error()


@app.route("/api/<string:fname>", methods=['DELETE'])
def delete_film(fname):
    if 'Authorization' in request.headers:
        try:
            token = request.headers['Authorization'].split(" ")
            auth = apiAuth(token[1])
            # print(auth)
            if 'token' in auth.keys():
                film = db.film.delete_one({'title': fname})
                resp = jsonify("Film " + fname + " Deleted successfully.")
                if film is None:
                    return not_found()
                else:
                    return resp
            else:
                return invalid_token()
        except jwt.exceptions.InvalidSignatureError:
            return invalid_token()
        except jwt.exceptions.ExpiredSignatureError:
            return token_expired()
        except jwt.exceptions.DecodeError:
            return invalid_token()

    else:
        return unauthorised_error()


@app.route("/api/<string:fname>", methods=['PATCH'])
def update_film(fname):
    _json = request.json
    title = _json['title']
    desc = _json['description']
    rental_duration = _json['rental_duration']
    rental_rate = _json['rental_rate']
    length = _json['length']
    replacement_cost = _json['replacement_cost']
    rating = _json['rating']
    list_actors = _json['list_actors']

    if 'Authorization' in request.headers:
        try:
            token = request.headers['Authorization'].split(" ")
            auth = apiAuth(token[1])
            # (auth)
            if 'token' in auth.keys():
                if title and desc and rental_duration and rental_rate and length and replacement_cost and rating and list_actors and request.method == 'PATCH':
                    film = db.film.update_one({'title': fname},
                                              {'$set': {'description': desc,
                                                        'rental_duration': rental_duration,
                                                        'rental_rate': rental_rate,
                                                        'length': length,
                                                        'replacement_cost': replacement_cost,
                                                        'rating': rating,
                                                        'list_actors': list_actors}
                                               })
                    resp = jsonify("Film Updated successfully.")
                    resp.status_code = 200
                    if film is None:
                        return not_found()
                    else:
                        return resp
            else:
                return invalid_token()
        except jwt.exceptions.InvalidSignatureError:
            return invalid_token()
        except jwt.exceptions.ExpiredSignatureError:
            return token_expired()
        except jwt.exceptions.DecodeError:
            return invalid_token()

    else:
        return unauthorised_error()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Data Not found for Route, ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


@app.errorhandler(401)
def unauthorised_error(error=None):
    message = {
        'status': 401,
        'message': 'HTTP 401 - Unauthorised'
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


def invalid_token(error=None):
    message = {
        'status': 401,
        'message': 'HTTP 401 - Invalid Auth Token.'
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


def invalid_key(error=None):
    message = {
        'status': 401,
        'message': 'HTTP 401 - Invalid API Key. Please contact the administrator.'
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


def token_expired(error=None):
    message = {
        'status': 401,
        'message': 'HTTP 401 - Authorization Token Expired.'
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


def apiAuth(token):
    api_secret = os.environ.get('API_SECRET')
    # print(token)
    # print(api_secret)
    json = jwt.decode(token, api_secret, algorithms=["HS256"])
    return json


@app.route("/auth/v1/tokens", methods=['GET'])
def generate_token():
    if 'Authorization' in request.headers:
        bearer = request.headers['Authorization'].split(" ")[1]
        tok_request = jsonify({'token': bearer})
        api_secret = os.environ.get('API_SECRET')
        db_tok = db.tokens.find_one({'token': str(bearer)})
        # print(db_tok)
        if db_tok is not None:
            token = jwt.encode({"token": str(bearer),
                                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=2)},
                               api_secret, algorithm="HS256")
            message = {
                'status': 200,
                'token': token
            }
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            return invalid_key()
    else:
        return unauthorised_error()


if __name__ == '__main__':
    app.run(debug=True)
