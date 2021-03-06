import jwt
import datetime
import os
import mysql.connector
from flask import (
    Blueprint, request, make_response, jsonify
)
from flask.views import MethodView
import requests

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


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        try:
            # get the post data
            form_user = request.form['user']
            form_pwd = request.form['pwd']
            
            # check if user already exists
            cursor = get_cnx().cursor(buffered=True)
            cursor.execute('select * from users where username like "%s"' %form_user)
            user = cursor.fetchone()
            
            # register user
            if not user:
                try:
                    query = (
                        "insert into users (username, pwd, role)"
                        " values('%s', '%s', 'guest')"
                        %(form_user, bcrypt.generate_password_hash(form_pwd,10).decode())
                    )
                    # insert the user
                    cursor.execute(query)
                    get_cnx().commit()
                    
                    # get user id
                    query = (
                        'select id from users where username like "%s"' %form_user
                    )
                    cursor.execute(query)
                    user_id = cursor.fetchone()[0]
                    
                    # generate the auth token
                    auth_token = encode_auth_token(user_id,form_user,"guest")
                    if auth_token:
                        responseObject = {
                            'status': 'success',
                            'message': 'Successfully registered.',
                            'auth_token': auth_token.decode()
                        }
                        return make_response(jsonify(responseObject)), 200
                
                # if some errors
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Some error occurred. Please try again./n' + str(e)
                    }
                    return make_response(jsonify(responseObject)), 401
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User already exists. Please Log in.',
                }
                return make_response(jsonify(responseObject)), 202
        
        except Exception as e:
            app.logger.info(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


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
class CheckTokenAPI(MethodView):
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

    def delete(self, dummy):
        try:
            app.logger.info('calling get function from delete function')
            return self.get(dummy)
        except Exception as e:
            app.logger.info(e)
#


class DeleteUserApi(MethodView):
    def delete(self):
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
                # call deleteall for clear user lists
                r = requests.delete(
                    'http://ambassador.default:8088/deleteall',
                    headers = {
                    'Authorization': 'Bearer ' + auth_token
                    }
                )
                app.logger.info(r)
                if (r.status_code == 200):
                    # delete user from db
                    userid = payload['sub']
                    cur = get_cnx().cursor()
                    query = "delete from users where id = %s" %userid
                    cur.execute(query)
                    if (cur.rowcount == 1): # if user was cancelled correctly
                        responseObject = {
                            'status': 'success',
                            'message': 'User %s deleted' %payload['username']
                        }
                        resp = make_response(jsonify(responseObject))
                        return resp, 200
                    else: 
                        responseObject = {
                            'status': 'fail',
                            'message': 'Some error occured while deleting user'
                        }
                        resp = make_response(jsonify(responseObject))
                        return resp, 500
                # if error during deleting user lists
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Some error occured while deleting user'
                    }
                    resp = make_response(jsonify(responseObject))
                    return resp, 500
            # if error in decoding the token
            responseObject = {
                'status': 'fail',
                'message': payload
            }
            return make_response(jsonify(responseObject)), 401
        # if no auth token
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401
#



# define the API resources
register_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
check_token_view = CheckTokenAPI.as_view('check_token_api')
delete_user_view = DeleteUserApi.as_view('delete_user_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/<path:dummy>',
    view_func=check_token_view,
    methods=['GET', 'DELETE']
)
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=register_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/deleteuser',
    view_func=delete_user_view,
    methods=['DELETE']
)
