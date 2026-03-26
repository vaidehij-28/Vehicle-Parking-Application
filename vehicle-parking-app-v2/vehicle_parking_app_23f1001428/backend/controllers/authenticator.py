from flask_restful import Resource
from flask import request, make_response, jsonify
from flask_security import auth_token_required, utils, current_user
from flask_security.utils import hash_password

from models import db, user_datastore

class Register(Resource):
    def post(self):
        credentials = request.get_json()
        
        if not credentials:
            result={
                "message": "Please provide all the credentials required for registraion."
            }
            return make_response(jsonify(result), 400)
        
        username = credentials.get('username', None)
        password = credentials.get('password', None)
        fullname = credentials.get('fullname', None)
        address = credentials.get('address', None)
        pincode = credentials.get('pincode', None)

        if not username or not password:
            result = {
                "message": "Both username and password are required"
            }
            return make_response(jsonify(result), 400)
        if user_datastore.find_user(email=username):
            result = {
                "message": "User with this username is already registered."
            }
            return make_response(jsonify(result), 400)
        
        hashed_password = hash_password(password)
        user_role = user_datastore.find_role('user')
        user_datastore.create_user(
            email=username, 
            password=hashed_password, 
            fullname = fullname,
            address = address,
            pincode = pincode,
            roles=[user_role]
        )
        db.session.commit()
        result = {
            "message": "User successfully registered",
            "user_details": {
                "username": username,
                "roles": [user_role.name]
            }
        }
        return make_response(jsonify(result), 200)

class Login(Resource):
    def post(self):
        credentials = request.get_json()
        if not credentials:
            result = {
                'message': 'Login credentials are required'
            }
            return make_response(jsonify(result), 400) 
        username = credentials.get("username", None)
        password = credentials.get("password", None)
        
        if not username or not password:
            result = {
                'message': 'Both username and password are required'
            }
            return make_response(jsonify(result), 400) 
        
        user = user_datastore.find_user(email=username)

        if not user:
            result = {
                'message': 'User not found'
            }
            return make_response(jsonify(result), 400)
        
        if not utils.verify_password(password, user.password):
            result = {
                'message': 'Invalid Password'
            }
            return make_response(jsonify(result), 400) 
    
        auth_token = user.get_auth_token()

        utils.login_user(user)
        result = {
            'message': 'Sucessfully logged In',
            'user_details': {
                'userid': user.id,
                'username': user.email,
                'roles': [role.name for role in user.roles],
                'auth_token': auth_token 
            }
        } 
        return make_response(jsonify(result), 200) 

class CheckEmail(Resource):
    def post(self):
        credentials = request.get_json()

        if not credentials:
            result={
                'message': 'Request body is empty.'
            }
            return make_response(jsonify(result), 400)
        
        username = credentials.get('username', None)
        if not username:
            result={
                'message': 'Username is required'
            }
            return make_response(jsonify(result), 400)
        
        user = user_datastore.find_user(email = username)
        if user:
            return make_response(jsonify({'available':False}), 200)
        else:
            return make_response(jsonify({'available':True}), 200)
    
class Logout(Resource):
    @auth_token_required
    def post(self):
        utils.logout_user()

        response = {
            "message" : "Successfully logged out"
        }
        return make_response(jsonify(response), 200)
    
class Users(Resource):
    @auth_token_required
    def get(self, userid=None):
        if userid:
            user = user_datastore.find_user(id=userid)
            result = {
                'user_details': {
                'userid': user.id,
                'username': user.email,
                'fullname': user.fullname,
                'address': user.address,
                'pincode': user.pincode,
                'roles': [role.name for role in user.roles]
                }
            }
            return make_response(jsonify(result), 200)  
        else :    
            users = user_datastore.user_model.query.filter(user_datastore.user_model.id != 1).all()
            if not users:
                result={
                    "message": "No user registered till now."
                }
                return make_response(jsonify(result), 400)
            
            user_list = []
            for user in users:
                user_list.append({
                    "id": user.id,
                    "email": user.email,
                    "fullname": user.fullname,
                    "address": user.address,
                    "pincode": user.pincode,
                    "roles": [role.name for role in user.roles]
                })

            return jsonify(user_list)
        
    @auth_token_required
    def put(self):
        data = request.get_json()
        
        user = current_user
        if not user:
            return {"message": "User not found"}, 404
        
        data = request.get_json()

        user.fullname=data.get('fullname', user.fullname)
        user.address=data.get('address', user.address)
        user.pincode=data.get('pincode', user.pincode)

        db.session.commit()

        return {"message": "Profile updated successfully"}, 200
    
