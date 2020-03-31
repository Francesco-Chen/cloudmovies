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
    baseUrl = 'http://image.tmdb.org/t/p/original'
    movie = tmdb.Movies(movieid) # call TMDB API
    postersUrl = []
    #for poster in movie.images(include_image_language=['en'])['posters']:
    #    imageUrl = poster['file_path']
    #   postersUrl += [baseUrl + imageUrl]
    try:
        postersUrl = baseUrl + movie.images()['posters'][0]['file_path']
    except:
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }
    return {
        "statusCode": 200,
        "body": {"url": postersUrl},
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }
