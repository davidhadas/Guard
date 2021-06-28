from kubernetes import client, config, watch
#from pprint import pprint
import threading
import random
import time
import os
import sys
import traceback

from Guard import Modeler
#import Markers
import Integers
#import Fingerprints
#import Histograms

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

#import Fingerprints


gates = {}
services = {}
modelers = Modeler.modelers

reloadGuardians = True




def serve(serviceId, gateId):
    if serviceId not in services:
        print("Controller  - serving a new service!!", serviceId)
        services[serviceId] = {}

    if (gateId not in gates):
        print("Gate is missing", gateId)
        return ({}, [])

    gate = gates[gateId]
    gateSpec = gate["spec"]
    if gateId not in services[serviceId]:
        print("Controller  - serving a new gate for service!!", serviceId, gateId)
        createGuardian(gateId, serviceId)
        services[serviceId][gateId] = {"modelers": [m(gateSpec) for m in modelers], "status": {}}

    return gateSpec, services[serviceId][gateId]["modelers"]

'''
def deleteGuardian(gateId, serviceId):
    print("Now in deleteGuardian", gateId + "." + serviceId)
    try:
        api.delete_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1beta1",
            namespace="knative-guardian",
            name=gateId+"."+serviceId,
            plural="guardians"
        )
        print("Guardian deleted", gateId+"."+serviceId)
    except client.exceptions.ApiException as e:
        print("Guardian could not be deleted for", gateId+"."+serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
'''
'''
def getGuardian(gateId, serviceId):
    resource = {}
    try:
        # get the resource and print out data

        resource = api.get_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1beta1",
            name=gateId+"."+serviceId,
            namespace="knative-guardian",
            plural="guardians",
        )
        print("Guardian found for", gateId+"."+serviceId)

    except client.exceptions.ApiException as e:
        print("Guardian not found for", gateId + "." + serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
        resource = createGuardian(gateId, serviceId)

    return resource
'''



def createGuardian(gateId, serviceId):
    # custom resource defined as dict
    guardian = {
        "apiVersion": "ibmresearch.com/v1beta1",
        "kind": "Guardians",
        "metadata": {
            "name": gateId + "." + serviceId
        },
        "spec": {
            "gateId": gateId
            , "serviceId": serviceId
        },
        "status": {}
    }
    try:

        api_response = api.create_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1beta1",
            namespace="knative-guardian",
            plural="guardians",
            body= guardian
        )
        print("Guardian created for", gateId+"."+serviceId, api_response)
    except client.exceptions.ApiException as e:
        print("Guardian could not be created for", gateId+"."+serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)

    return guardian


def patchGuardian(gateId, serviceId, status):
    try:
        # patch the resource and print out data
        print ("patchGuardian", gateId, serviceId, status)
        api.patch_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1beta1",
            name=gateId+"."+serviceId,
            namespace="knative-guardian",
            plural="guardians",
            body=status
        )
        print("Guardian patched", gateId+"."+serviceId)
    except client.exceptions.ApiException as e:
        print("Guardian not patched", gateId+"."+serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
        createGuardian(gateId, serviceId)


def getGate(gateId):
    try:
        # get the resource and print out data

        resource = api.get_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1beta1",
            name=gateId,
            namespace="knative-guardian",
            plural="gates"
        )
        return resource
    except:
        print("Cant find Gate", gateId)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
        return None




def watchGuardians():
    """thread worker function"""
    print('Started watching Guardians')
    global reloadGuardians
    num = 0
    resourceVersion = ''
    while (True):
        if (reloadGuardians):
            reloadGuardians = False
            resourceVersion = ''
        start = 0
        try:
            w = watch.Watch()
            print('--> Starting stream of Guardians with resourceVersion', resourceVersion, flush=True)
            stream = w.stream(api.list_namespaced_custom_object,
                                  group="ibmresearch.com",
                                  version="v1beta1",
                                  namespace="knative-guardian",
                                  plural="guardians",
                                  timeout_seconds=random.randint(50, 60),
                                  resource_version = resourceVersion
                                 )
            start = time.time()
            for event in stream:
                print("Guardians event:", flush=True)

                guardianId = "unknown"
                try:
                    #pprint(event)
                    t = event['type']
                    guardian = event['object']
                    if (resourceVersion < guardian["metadata"]["resourceVersion"]):
                        resourceVersion = guardian["metadata"]["resourceVersion"]
                    guardianId = guardian["metadata"]["name"]
                    print("Guardians event:",t, resourceVersion, guardianId,  flush=True)

                    num += 1

                    serviceId = guardian["spec"]["serviceId"]
                    gateId = guardian["spec"]["gateId"]
                    status = guardian["status"]

                    print("Guardian new object",num, gateId, serviceId, flush=True)
                    if (gateId in gates):
                        gate = gates[gateId]
                    else:
                        print("Guardian without Gate is ignored!", num, guardianId, flush=True)
                        continue

                    if serviceId not in services:
                        print("new Service found!!", serviceId, services, flush=True)
                        services[serviceId] = {}

                    if gateId not in services[serviceId]:
                        print("new Guardian found - initializing all modelers", serviceId, gateId, services[serviceId], flush=True)
                        services[serviceId][gateId] = {"modelers": [m(gate["spec"]) for m in modelers], "status": status}


                    if t == "DELETED":
                        status = {}
                        del services[serviceId][gateId]
                    if t == "MODIFIED" or t == "ADDED":
                        services[serviceId][gateId]["status"] = status
                        for m in services[serviceId][gateId]["modelers"]:
                            m.crdload(status)

                    print("GGG... Guradian successfuly updated", num, guardianId, resourceVersion, flush=True)
                except:

                    print("GGG... Guradian exception illegal object", num, guardianId, flush=True)
                    traceback.print_exc(file=sys.stdout)
                    print("---------Error-------", flush=True)


            print("Guardians - ended list_namespaced_custom_object watch stream", flush=True)


        except:
            e = sys.exc_info()[0]
            print("Guardians - list_namespaced_custom_object exception", flush=True)
            traceback.print_exc(file=sys.stdout)
            print("---------Error-------", flush=True)
            resourceVersion = ''

        end = time.time()
        print("Guardians Timeout:", end-start, "seconds", flush=True)
        if (end-start < 50):
            time.sleep(50+start-end)
            resourceVersion = ''
        try:
            serviceIds = list(services.keys())
            if len(serviceIds):
                serviceId = random.choice(serviceIds)
                gateIds = list(services[serviceId].keys())
                if len(gateIds):
                    gateId = random.choice(list(services[serviceId].keys()))
                    print("watchGuardians storing..", serviceId, gateId, services[serviceId][gateId])
                    status = {}
                    for m in services[serviceId][gateId]["modelers"]:
                        m.crdstore(status)
                    status = {"status": status}
                    print("Patching guardian crd...", gateId, serviceId, status, flush=True)
                    patchGuardian(gateId, serviceId, status)
                    print("Storing Guardians", flush=True)
        except:
            e = sys.exc_info()[0]
            print("Failed to store object", flush=True)
            traceback.print_exc(file=sys.stdout)
            print("---------Error-------", flush=True)

        print("Back to watching Guardians", flush=True)


def watchGates():
    global reloadGuardians
    """thread worker function"""
    print('watchGates get initial data about gates')
    num = 0
    resourceVersion = ''

    try:
        response = api.list_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1beta1",
            namespace="knative-guardian",
            plural="gates")

        items = response["items"]

        for i in range(len(items)):
            try:
                gate = items[i]
                gateId = gate["metadata"]["name"]

                LearnLimit = float(gate["spec"]["LearnLimit"])
                AllowLimit = float(gate["spec"]["AllowLimit"])
                minimumLearning = int(gate["spec"]["minimumLearning"])
                fingerprintNames = gate["spec"]["fingerprints"]
                markerNames = gate["spec"]["markers"]
                roundedMarkerNames = gate["spec"]["roundedMarkers"]
                histogramNames = gate["spec"]["histograms"]
                num += 1
                print ("GGG.. Gate Added:", num, gateId, LearnLimit, AllowLimit, minimumLearning,
                       fingerprintNames, markerNames, roundedMarkerNames, histogramNames, flush=True)
                gates[gateId] = gate


            except:
                print("GGG... Gate exception illegal object", flush=True)
                traceback.print_exc(file=sys.stdout)
                print("---------Error-------", flush=True)

    except:
        e = sys.exc_info()[0]
        print("GGG... Gate exception during list_namespaced_custom_object", resourceVersion, flush=True)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)

    guardianWatcher = threading.Thread(target=watchGuardians)
    guardianWatcher.start()


    print('Started watching Gates with resourceVersion', flush=True)

    while True:
        start = 0
        try:
            w = watch.Watch()
            start = time.time()
            stream = w.stream(api.list_namespaced_custom_object,
                     group="ibmresearch.com",
                     version="v1beta1",
                     namespace="knative-guardian",
                     plural="gates",
                     resource_version=resourceVersion
                     )
            start = time.time()
            for event in stream:
                print('Found Gates', flush=True)
                gateId = "unknown"
                try:
                    num += 1
                    #pprint(event)
                    gate = event['object']
                    t = event['type']
                    if (resourceVersion<gate["metadata"]["resourceVersion"]):
                        resourceVersion = gate["metadata"]["resourceVersion"]
                    print("Gate Event", num, resourceVersion, t, flush=True)
                    #pprint(gate)
                    gateId = gate["metadata"]["name"]
                    gateSpec = gate["spec"]

                    LearnLimit = float(gateSpec["LearnLimit"])
                    AllowLimit = float(gateSpec["AllowLimit"])
                    minimumLearning = int(gateSpec["minimumLearning"])

                    print("Gate Event", num, gateId, t, flush=True)
                    if t == "MODIFIED" or t == "ADDED":
                        gates[gateId] = gate
                    elif t == "DELETED":
                        del (gates[gateId])
                    for serviceId, service in services.items():
                        if (gateId in service):
                            for m in service[gateId]["modelers"]:
                                m.configFromGate(gateSpec)

                    reloadGuardians = True

                    print("GGG... Gate added:", num, gateId, resourceVersion, LearnLimit, AllowLimit, minimumLearning, flush=True)

                    '''
                    We cant delete Guardians as they may include user configs
                    for serviceId, service in services.items():
                        print(serviceId, service, flush=True)
                        if (gateId in service):
                            print(gateId, flush=True)
                            deleteGuardian(gateId, serviceId)
                            print(gateId, "deletedGuardian", flush=True)
                            services[serviceId][gateId] = []
                            print(gateId, "deleted the modelers", flush=True)
                    '''


                except:
                    print("Gate exception illegal object", gateId, resourceVersion, flush=True)
                    traceback.print_exc(file=sys.stdout)
                    print("---------Error-------", flush=True)

        except:
            print("Gates - list_namespaced_custom_object exception", resourceVersion, flush=True)
            traceback.print_exc(file=sys.stdout)
            print("---------Error-------", flush=True)
            resourceVersion = ''

        end = time.time()
        print("Guardians Timeout:", end - start, "seconds", flush=True)
        if (end - start < 50):
            time.sleep(50 + start - end)
            resourceVersion = ''

        print("Back to watching Gates with resourceVersion", resourceVersion, flush=True)



try:
    config.load_incluster_config()
except:
    print("config.load_incluster_config() exception")
# v1 = client.CoreV1Api()
api = client.CustomObjectsApi()

gateWatcher = threading.Thread(target=watchGates)
gateWatcher.start()


'''
    # delete it
    api.delete_namespaced_custom_object(
        group="stable.example.com",
        version="v1",
        name="my-new-cron-object",
        namespace="default",
        plural="crontabs",
        body=client.V1DeleteOptions(),
    )
    print("Resource deleted")
'''
