ibmcloud cr login
docker build  --tag guardian . 
docker tag guardian us.icr.io/dev_sec_ops/guardian
docker push us.icr.io/dev_sec_ops/guardian
kubectl rollout restart deployment guardian -n knative-guardian


