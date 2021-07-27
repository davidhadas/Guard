ibmcloud cr login
docker build  --tag guardian . 
docker tag guardian us.icr.io/dev_sec_ops/guardian:latest
docker push us.icr.io/dev_sec_ops/guardian:latest
kubectl rollout restart deployment guardian -n knative-guardian

#Guardian role
kubectl apply -f kube/role.yaml
kubectl apply -f kube/serviceAccount.yaml
kubectl apply -f kube/roleBinding.yaml
#CRDs
kubectl apply -f kube/Gates.yaml
kubectl apply -f kube/Guardians.yaml
kubectl apply -f kube/envoy.gate.yaml
