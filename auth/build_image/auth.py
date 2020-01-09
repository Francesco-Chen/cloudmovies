import jwt
import datetime
import os

from flask import (
    Blueprint, request, make_response, jsonify
)
from flask.views import MethodView

# from werkzeug.security import check_password_hash, generate_password_hash

# from flaskr.db import get_db
from . import bcrypt, app

# simulate db
db = [{
    'id': 1,
    'user': 'admin',
    'pwd': bcrypt.generate_password_hash('admin', 10).decode()}]



auth_blueprint = Blueprint('auth', __name__)
SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=300),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
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
        return payload['sub']
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
            user = None
            if (db[0]['user'] == form_user):
                user = db[0]
            if user and bcrypt.check_password_hash(
                user['pwd'], form_pwd
            ):
                auth_token = encode_auth_token(user['id'])
                print(str(auth_token))
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
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
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
            resp = decode_auth_token(auth_token)
            if not isinstance(resp, str):
                #user = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': resp
                        #'user_id': user.id,
                        #'email': user.email,
                        #'admin': user.admin,
                        #'registered_on': user.registered_on
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
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

@auth_blueprint.route('/hellopost',methods=('GET', 'POST'))
def hellopost():
    if request.method == 'POST':
        return 'Hello, World!'



@auth_blueprint.route('/hello',methods=('GET', 'POST'))
def hello():
    return make_response('Hello, World!'), 200


