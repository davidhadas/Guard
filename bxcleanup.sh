ibmcloud cr images |grep guardian|grep main|awk '{ print $1":"$2 }'|xargs ibmcloud cr image-rm
