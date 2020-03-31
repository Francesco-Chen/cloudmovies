import unittest
import requests
import logging
import sys
import urllib.parse

class MovieApiTest(unittest.TestCase):
    # /movie/
    def test_movie(self):
        resp = requests.get('http://localhost:8088/movie/19995')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['info']['title'],'Avatar')
        self.assertEqual(resp.json()['info']['id'],19995)

    def test_movie_not_existing(self):
        resp = requests.get('http://localhost:8088/movie/3333333')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['info']), 0)

    def test_movie_not_integer(self):
        resp = requests.get('http://localhost:8088/movie/aaaa')
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.json()['message'], 'Movie Id should be an integer')

    def test_movie_actors_directors(self):
       resp = requests.get('http://localhost:8088/movie/19995')
       self.assertEqual(resp.status_code, 200)
       self.assertTrue(resp.json()['info'].get('actors', ''))
       self.assertEqual(resp.json()['info']['director'],'James Cameron')

    # /search?id
    def test_search_single_id(self):
        resp = requests.get('http://localhost:8088/search?id=19995')
        log = logging.getLogger("TestLog")
        log.debug(resp.json())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 1)
        self.assertEqual(resp.json()['movies'][0]['title'], 'Avatar')

    def test_search_multiple_id(self):
        resp = requests.get('http://localhost:8088/search?id=19995,1995')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 2)
        self.assertEqual(resp.json()['movies'][0]['title'], 'Lara Croft: Tomb Raider')

    def test_search_id_not_existing(self):
        resp = requests.get('http://localhost:8088/search?id=3333333')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 0)

    def test_search_id_not_integer(self):
        resp = requests.get('http://localhost:8088/search?id=19995,aaa')
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.json()['message'], 'Movie Id should be integers')

    # /search?title
    def test_search_title_complete(self):
        resp = requests.get('http://localhost:8088/search?title=avatar')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 1)
        self.assertEqual(resp.json()['movies'][0]['title'], 'Avatar')
    
    def test_search_title_partial(self):
        resp = requests.get('http://localhost:8088/search?title=tomb')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 7)
        self.assertEqual(resp.json()['movies'][6]['id'], 17577)

    def test_search_title_with_special_chars(self):
        title = urllib.parse.quote("One Man's Hero")
        resp = requests.get('http://localhost:8088/search?title=' + title)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 1)
        self.assertEqual(resp.json()['movies'][0]['id'], 69848)

    def test_search_title_not_existing(self):
        resp = requests.get('http://localhost:8088/search?title=widch')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 0)


    # /search?genres
    def test_search_genres_single(self):
        resp = requests.get('http://localhost:8088/search?genres=horror')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 20)
        self.assertEqual(resp.json()['movies'][0]['title'], 'Psycho')

    def test_search_genres_multiple(self):
        resp1 = requests.get('http://localhost:8088/search?genres=horror,fantasy,adventure')
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(len(resp1.json()['movies']), 5)

        resp2 = requests.get('http://localhost:8088/movie/' + str(resp1.json()['movies'][0]['id']))
        genres = resp2.json()['info']['genres']
        self.assertTrue(
            'Horror' in genres and
            'Fantasy' in genres and
            'Adventure' in genres
        )

    def test_search_genres_not_existing(self):
        resp = requests.get('http://localhost:8088/search?genres=xxxxxx')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 0)

    def test_search_title_and_genres(self):
        resp = requests.get('http://localhost:8088/search?genres=adventure&title=pirates')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 6)
        self.assertEqual(resp.json()['movies'][5]['id'], 15511)


    # /getlist
    def test_getlist(self):
        resp = requests.get('http://localhost:8088/getlist')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 20)
        self.assertEqual(resp.json()['movies'][0]['id'], 40963)

    def test_getlist_start(self):
        resp = requests.get('http://localhost:8088/getlist?start=118')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 20)
        self.assertEqual(resp.json()['movies'][0]['id'], 11778)

    def test_getlist_start_not_integer(self):
        resp = requests.get('http://localhost:8088/getlist?start=aaa')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 20)
        self.assertEqual(resp.json()['movies'][0]['id'], 40963)

    def test_getlist_start_near_bottom(self):
        resp = requests.get('http://localhost:8088/getlist?start=4800')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 3)
        self.assertEqual(resp.json()['movies'][0]['id'], 433715)

    def test_getlist_start_out_bounds(self):
        resp = requests.get('http://localhost:8088/getlist?start=5000')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['movies']), 0)


class AuthApiTest(unittest.TestCase):
    # /login
    def test_login(self):
        resp = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        log = logging.getLogger("TestLog")
        log.debug(resp.json())
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get('auth_token', ''))
        self.assertEqual(resp.json()['message'], 'Successfully logged in.')
        self.assertEqual(resp.json()['status'], 'success')

    def test_login_incorrect_user(self):
        resp = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "adminxxxx",
                "pwd": "admin"
            }
        )
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(resp.json().get('auth_token', ''))
        self.assertEqual(resp.json()['message'], 'User or password are incorrect.')
        self.assertEqual(resp.json()['status'], 'fail')

    def test_login_incorrect_pwd(self):
        resp = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "adminxxxx"
            }
        )
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(resp.json().get('auth_token', ''))
        self.assertEqual(resp.json()['message'], 'User or password are incorrect.')
        self.assertEqual(resp.json()['status'], 'fail')

    def test_login_missing_data(self):
        resp = requests.post(
            'http://localhost:8088/auth/login',
        )
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.json()['message'], 'Try again')
        self.assertEqual(resp.json()['status'], 'fail')


    # /auth/register
    def test_register_user_already_existing(self):
        resp = requests.post(
            'http://localhost:8088/auth/register',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.json()['message'], 'User already exists. Please Log in.')
        self.assertEqual(resp.json()['status'], 'fail')

    def test_register_missing_data(self):
        resp = requests.post(
            'http://localhost:8088/auth/register',
        )
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.json()['message'], 'Try again')
        self.assertEqual(resp.json()['status'], 'fail')
        

class FavoritesApiTest(unittest.TestCase):
    # /getfavorites
    def test_01_getfavorites(self):
        respAuth = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        token = respAuth.json()['auth_token']

        resp = requests.get(
            'http://localhost:8088/getfavorites',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(len(resp.json()), 0)

    def test_02_getfavorites_token_expired(self):
        token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1ODU0OTYyMTcsImlhdCI6MTU4NTQ5NDQxNywic3ViIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0.ZCNhXX-0ZK_gcuRXw1QidcGlEPgOLOCeHn5-tS1I6cE'

        resp = requests.get(
            'http://localhost:8088/getfavorites',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['message'], 'Signature expired. Please log in again.')
        self.assertEqual(resp.json()['status'], 'fail')

    def test_03_getfavorites_token_malformed(self):
        token = 'xxxxxxxeyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1ODU0OTYyMTcsImlhdCI6MTU4NTQ5NDQxNywic3ViIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0.ZCNhXX-0ZK_gcuRXw1QidcGlEPgOLOCeHn5-tS1I6cE'

        resp = requests.get(
            'http://localhost:8088/getfavorites',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['message'], 'Invalid token. Please log in again.')
        self.assertEqual(resp.json()['status'], 'fail')

    def test_04_getfavorites_missing_token(self):
        resp = requests.get(
            'http://localhost:8088/getfavorites',
        )
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['message'], 'Provide a valid auth token.')
        self.assertEqual(resp.json()['status'], 'fail')


    # /addfavorite
    def test_05_addfavorite(self):
        respAuth = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        token = respAuth.json()['auth_token']

        resp = requests.get(
            'http://localhost:8088/addfavorite?movieid=19995',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['message'], 'movie added')
        self.assertEqual(resp.json()['status'], 'success')

        respGet = requests.get(
            'http://localhost:8088/getfavorites',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(len(respGet.json()), 1)

    def test_06_addfavorite_already_present(self):
        respAuth = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        token = respAuth.json()['auth_token']

        resp = requests.get(
            'http://localhost:8088/addfavorite?movieid=19995',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.json()['message'], 'movie already added')
        self.assertEqual(resp.json()['status'], 'fail')

    # /deletefavorite
    def test_07_deletefavorite(self):
        respAuth = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        token = respAuth.json()['auth_token']

        resp = requests.get(
            'http://localhost:8088/deletefavorite?movieid=19995',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['message'], '1 record(s) deleted')
        self.assertEqual(resp.json()['status'], 'success')

        respGet = requests.get(
            'http://localhost:8088/getfavorites',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(len(respGet.json()), 0)

    def test_08_deletefavorite_not_present(self):
        respAuth = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        token = respAuth.json()['auth_token']

        resp = requests.get(
            'http://localhost:8088/deletefavorite?movieid=19995',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['message'], '0 record(s) deleted')
        self.assertEqual(resp.json()['status'], 'success')

        respGet = requests.get(
            'http://localhost:8088/getfavorites',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        self.assertEqual(len(respGet.json()), 0)

    # favorit limit
    def test_09_addfavorite_limit_exceedeed(self):
        respAuth = requests.post(
            'http://localhost:8088/auth/login',
            data = {
                "user": "admin",
                "pwd": "admin"
            }
        )
        token = respAuth.json()['auth_token']

        requests.get(
            'http://localhost:8088/addfavorite?movieid=19995',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        requests.get(
            'http://localhost:8088/addfavorite?movieid=1995',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        requests.get(
            'http://localhost:8088/addfavorite?movieid=40963',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        requests.get(
            'http://localhost:8088/addfavorite?movieid=550',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        requests.get(
            'http://localhost:8088/addfavorite?movieid=238',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )
        resp = requests.get(
            'http://localhost:8088/addfavorite?movieid=424',
            headers = {
                'Authorization': 'Bearer ' + token
                }
        )

        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.json()['message'], 'max number of favorites reached')
        self.assertEqual(resp.json()['status'], 'fail')

        resp = requests.get('http://localhost:8088/deletefavorite?movieid=19995', headers = {'Authorization': 'Bearer ' + token})
        resp = requests.get('http://localhost:8088/deletefavorite?movieid=1995', headers = {'Authorization': 'Bearer ' + token})
        resp = requests.get('http://localhost:8088/deletefavorite?movieid=40963', headers = {'Authorization': 'Bearer ' + token})
        resp = requests.get('http://localhost:8088/deletefavorite?movieid=550', headers = {'Authorization': 'Bearer ' + token})
        resp = requests.get('http://localhost:8088/deletefavorite?movieid=238', headers = {'Authorization': 'Bearer ' + token})



class GetposterApiTest(unittest.TestCase):
    def test_getposters(self):
        resp = requests.get('http://localhost:8088/function/getposters?movieid=19995')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['url'], 'http://image.tmdb.org/t/p/original/8Ic8rRVoVrDJJlXzVzGxAesufUV.jpg')
        
    def test_getposters_poster_not_found(self):
        resp = requests.get('http://localhost:8088/function/getposters?movieid=40963')
        self.assertEqual(resp.status_code, 404)

    def test_getposters_id_not_integer(self):
        resp = requests.get('http://localhost:8088/function/getposters?movieid=4aaa')
        self.assertEqual(resp.status_code, 500)


class GettrailerApiTest(unittest.TestCase):
    def test_gettrailer(self):
        resp = requests.get('http://localhost:8088/function/gettrailer?movieid=19995')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['trailerurl'], 'https://www.youtube.com/watch?v=5MB3Ea6L-gw')

    def test_gettrailer_id_not_integer(self):
        resp = requests.get('http://localhost:8088/function/gettrailer?movieid=4aaa')
        self.assertEqual(resp.status_code, 500)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    unittest.main()

