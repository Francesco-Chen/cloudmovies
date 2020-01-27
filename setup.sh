# before launching the automatic deployment job, make sure to create:
# /data/favoritesdb, /data/userdb, /data/moviedb
# for persistent storage


# create namespace
kubectl create namespace cloudmovies

## apply all yml files from project root
# deploying ambassador
kubectl apply -f ambassador/ambassador-rbac.yaml
kubectl apply -f ambassador/ambassador-service.yaml

# deployng the pv
kubectl apply -f auth/db/userdb_pv.yml
kubectl apply -f moviedb/db/moviedb_pv.yml
kubectl apply -f favorites/db/favoritesdb_pv.yml

# deploying the statefulsets
kubectl apply -f auth/db/userdb_statefulset.yml
kubectl apply -f moviedb/db/moviedb_statefulset.yml
kubectl apply -f favorites/db/favoritesdb_statefulset.yml

# deploying the deployments
kubectl apply -f auth/api/auth_deployment.yml 
kubectl apply -f moviedb/api/moviedbapi_deployment.yml
kubectl apply -f favorites/api/favorites_deployment.yml

# deploying the services
kubectl apply -f auth/api/auth_svc.yml
kubectl apply -f moviedb/api/moviedbapi_svc.yml
kubectl apply -f favorites/api/favorites_svc.yml
kubectl apply -f auth/db/userdb_svc.yml
kubectl apply -f favorites/db/favoritesdb_svc.yml
kubectl apply -f moviedb/db/moviedb_svc.yml

# deploying the mapping 
kubectl apply -f auth/api/auth_mapping.yml
kubectl apply -f moviedb/api/moviedbapi_mapping.yml
kubectl apply -f favorites/api/favorites_mapping.yml

## deployng openfaas function
export OPENFAAS_URL=http://127.0.0.1:31112
# create secret with tmdb api key
kubectl create secret generic tmdb-api-key --from-file=tmdb-api-key=tmdb_api_key.txt -n openfaas-fn
# run within posters floder
cd posters
faas-cli deploy -f getposters.yml
cd ..
# apply mapping
kubectl apply -f posters/getposters_mapping.yml

# deploying web interface
kubectl apply -f web/web_deployment.yml
kubectl apply -f web/web_svc.yml

# wait some seconds
sleep(20)

# portforward 
kubectl port-forward svc/ambassador 8088 &
kubectl port-forward -n cloudmovies svc/websvc 8080:80 &

# go to localhost:8080 and test!
