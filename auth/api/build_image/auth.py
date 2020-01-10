import jwt
import datetime
import os

from flask import (
    Blueprint, request, make_response, jsonify
)
from flask.views import MethodView

from . import bcrypt, app, cursor


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
            app.logger.info('request: ' + str(request))
            app.logger.info('request.content_length: ' + str(request.content_length))
            app.logger.info('request.content_type: ' + str(request.content_type))
            app.logger.info('request.get_data: ' + str(request.get_data().decode()))
            app.logger.info('request.values: ' + str(request.values))
            app.logger.info('request.form: ' + str(request.form))
            form_user = request.form['user']
            form_pwd = request.form['pwd']

            # fetch the user data
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
                auth_token = encode_auth_token(user_id)
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
            resp = decode_auth_token(auth_token)
            if not isinstance(resp, str):
                #user = User.query.filter_by(id=resp).first()
                cursor.execute("select * from users where id = " + str(resp))
                user = cursor.fetchone()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user[0],
                        'role': user[3]
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


@auth_blueprint.route('/test',methods=('GET', 'POST'))
def test():
    cursor.execute("select * from users where id=1")
    r = cursor.fetchone()
    app.logger.info(r)
    return make_response('Hello, World!\n'), 200

