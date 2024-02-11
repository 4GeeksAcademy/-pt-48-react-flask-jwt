"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
@jwt_required()
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route("/user", methods=["GET"])
def get_users():
    users = User.query.all()
    users = list(map(lambda x: x.serialize(), users))
    return jsonify(users), 200

@api.route("/user", methods=["POST"])
def create_user():
    request_body = request.get_json()
    user = User(username=request_body["username"], email=request_body["email"], password=request_body["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 200

@api.route("/token", methods=["POST"])
def create_token():
    request_body = request.get_json()
    user = User.query.filter_by(username=request_body["username"]).first()
    if user is None:
        return jsonify({"msg": "Bad username or password"}), 401
    if user.check_password(request_body["password"]):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Bad username or password"}), 401
                
@api.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200
                    