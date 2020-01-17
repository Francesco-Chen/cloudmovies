import jwt
import datetime
import os
import mysql.connector
from flask import (
    Blueprint, request, make_response, jsonify
)
from flask.views import MethodView

from . import bcrypt, app


auth_blueprint = Blueprint('auth', __name__)
SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')

cnx = None
def get_cnx():
    global cnx
    if cnx and cnx.is_connected():
        return cnx
    else:
        cnx = mysql.connector.connect(
            host='userdbsvc',
            user='userdb_user',
            passwd='userdb_pwd',
            database='userdb'
        )
        return cnx


def encode_auth_token(user_id, username, user_role):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=1800),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
            'username': username,
            'role': user_role
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e
#
def decode_auth_token(auth_token):
    """
    Validates the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, SECRET_KEY)
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


class LoginAPI(MethodView):
    """
    User Login Resource
    """
    def post(self):

        try:
            # get the post data
            form_user = request.form['user']
            form_pwd = request.form['pwd']

            # fetch the user data
            cursor = get_cnx().cursor(buffered=True)
            cursor.execute('select * from users where username like "%s"' %form_user)
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                user_username = user[1]
                user_pwd = user[2]
                user_role = user[3]
            if user and bcrypt.check_password_hash(
                user_pwd, form_pwd
            ):
                auth_token = encode_auth_token(user_id,user_username,user_role)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User or password are incorrect.'
                }
                return make_response(jsonify(responseObject)), 401
        except Exception as e:
            app.logger.info(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500

#
class UserAPI(MethodView):
    """
    User Resource
    """
    def get(self,dummy):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            payload = decode_auth_token(auth_token) # if there is an error then payload is a string
            if not isinstance(payload, str):
                responseObject = {
                    'status': 'success',
                    'data': payload
                }
                resp = make_response(jsonify(responseObject))
                resp.headers['Cloudmovie-UserId'] = payload['sub']
                return resp, 200
            responseObject = {
                'status': 'fail',
                'message': payload
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401
#

# define the API resources
login_view = LoginAPI.as_view('login_api')
check_token_view = UserAPI.as_view('check_token_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/<path:dummy>',
    view_func=check_token_view,
    methods=['GET']
)

