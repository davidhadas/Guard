docker build  --tag guardian . 
docker tag guardian davidhadas/guardian 
docker push davidhadas/guardian
kubectl rollout restart deployment guardian -n knative-guardian


