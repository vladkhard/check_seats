import base64
import hashlib
import yaml

import pymongo
from flask import Flask, request, make_response, Response


app = Flask(__name__)
with open("config.yaml", "r") as file_obj:
    data = yaml.load(file_obj)
    mongo_login = data["MONGO_USERNAME"]
    mongo_password = data["MONGO_PASSWORD"]
client = pymongo.MongoClient(f"mongodb://{mongo_login}:{mongo_password}@localhost:27017")


def valid_credentials(token):
    decoded = base64.b64decode(token).decode()
    login, password = decoded.split(":")
    user = client.users.credentials.find_one({"_id": login, "password": hashlib.md5(password.encode()).digest()})
    return bool(user)


@app.route("/")
def main():
    return "Hello, World!"


@app.route("/register")
def register(methods=["GET"]):
    auth_type, credentials = request.headers.get("Authorization").split(" ")
    if auth_type == "Basic":
        decoded = base64.b64decode(credentials).decode()
        login, password = decoded.split(":")
        try:
            client.users.credentials.insert_one({"_id": login, "password": hashlib.md5(password.encode()).digest()})
            return make_response(Response("successfully registered!"), 200)
        except pymongo.errors.DuplicateKeyError:
            return make_response(Response("this username has been already taken!"), 400)
    else:
        return make_response(Response("wrong autorization type!"), 400)


@app.route("/test-registration")
def test_registration(methods=["GET"]):
    auth_type, credentials = request.headers.get("Authorization").split(" ")
    if auth_type == "Basic":
        if valid_credentials(credentials):
            return make_response(Response("user can log in!", 200))
        else:
            return make_response(Response("user can not log in!", 400))
    else:
        return make_response(Response("wrong autorization type!"), 400)
