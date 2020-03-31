import tmdbsimple as tmdb

def handle(event, context):
    # set api-key
    api_key_file = open("/var/openfaas/secrets/tmdb-api-key")
    tmdb.API_KEY = api_key_file.readline().rstrip('\n')
    
    # get movieid
    try:
        movieid = int(event.query['movieid'])
    except:
        responseObject = {
            'statusCode': 500,
            'status': 'fail',
            'message': 'parameter incorrect'
        }
        return responseObject
    
    # get urls
    baseUrl = 'https://www.youtube.com/watch?v='
    movie = tmdb.Movies(movieid) # call TMDB API
    trailerUrl = []
    #for poster in movie.images(include_image_language=['en'])['posters']:
    #    imageUrl = poster['file_path']
    #   postersUrl += [baseUrl + imageUrl]
    try:
        trailerUrl = baseUrl + movie.videos()['results'][0]['key']
    except:
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }
    return {
        "statusCode": 200,
        "body": {"trailerurl": trailerUrl},
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }
