from kubernetes import client, config, watch
#from pprint import pprint
import threading
import random
import time
import os
import sys
import traceback

from Guard import Modeler
import Markers
import Integers
import Fingerprints
import Histograms

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

gates = {}
serviceSpec = {}
serviceModelers = {}
serviceStatus = {}
modelers = Modeler.modelers

reloadGuardians = True

def addService(serviceId):
    print("Controller  - serving a new service!!", serviceId)
    serviceModelers[serviceId] = {}
    serviceStatus[serviceId] = {}
    serviceSpec[serviceId] = {"learnUntil": 0,
                              "unblockUntil": 0,
                              "unlearnUntil": 0,
                              "my_n": 0,
                              "base_n": 0}
    for gId in gates:
        gate = gates[gId]
        gateSpec = gate["spec"]
        serviceModelers[serviceId][gId] = [m(gateSpec) for m in modelers]
        serviceStatus[serviceId][gId] = {}

def serve(serviceId, gateId):
    if (gateId not in gates):
        print("Gate is missing", gateId)
        return ({}, [])
    if serviceId not in serviceSpec:
        addService(serviceId)
        createGuardian(serviceId)

    return gates[gateId]["spec"], serviceSpec[serviceId], serviceModelers[serviceId][gateId]


def deleteGuardian(serviceId):
    print("Now in deleteGuardian",  serviceId)
    try:
        api.delete_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1",
            namespace="knative-guardian",
            name=serviceId,
            plural="guardians"
        )
        print("Guardian deleted", serviceId)
    except client.exceptions.ApiException as e:
        print("Guardian could not be deleted for", serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)

'''
def getGuardian(gateId, serviceId):
    resource = {}
    try:
        # get the resource and print out data

        resource = api.get_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1",
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



def createGuardian(serviceId):
    # custom resource defined as dict

    guardian = {
        "apiVersion": "ibmresearch.com/v1",
        "kind": "Guardians",
        "metadata": {
            "name": serviceId
        },
        "spec": {"serviceId": serviceId },
        "status": {}
    }
    try:

        api_response = api.create_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1",
            namespace="knative-guardian",
            plural="guardians",
            body= guardian
        )
        print("Guardian created for", serviceId, api_response)
    except client.exceptions.ApiException as e:
        print("Guardian could not be created for", serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)

    return guardian


def patchGuardian(serviceId, status):
    try:
        # patch the resource and print out data
        print ("patchGuardian", serviceId, status)
        api.patch_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1",
            name=serviceId,
            namespace="knative-guardian",
            plural="guardians",
            body=status
        )
        print("Guardian patched", serviceId, status)
    except client.exceptions.ApiException as e:
        print("Guardian not patched",  serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
        createGuardian(serviceId)


def configGuardian(serviceId, data):
    try:
        now = time.time()
        learnUntil = float(data["learnUntil"])*60+now;
        unlearnUntil = float(data["unlearnUntil"])*60+now;
        unblockUntil = float(data["unblockUntil"])*60+now;

        spec = {"spec": {"learn_until": learnUntil,
                          "unlearn_until": unlearnUntil,
                          "unblock_until": unblockUntil
                          }}

        print("Guardian spec patch", serviceId, spec)

        api.patch_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1",
            name= serviceId,
            namespace="knative-guardian",
            plural="guardians",
            body=spec
        )
        print("Guardian spec patched", serviceId, spec)
    except NameError:
        print("MIMIC: Guardian spec patched", serviceId, spec)
    except client.exceptions.ApiException as e:
        print("Guardian not patched", serviceId, e)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)


def getGate(gateId):
    try:
        # get the resource and print out data

        resource = api.get_namespaced_custom_object(
            group="ibmresearch.com",
            version="v1",
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
                                  version="v1",
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
                    if t == "DELETED":
                        del (serviceModelers[serviceId])
                        del (serviceStatus[serviceId])
                        del (serviceData[serviceId])

                    if t == "MODIFIED" or t == "ADDED":
                        num += 1
                        status = guardian["status"]
                        serviceId = guardian["spec"]["serviceId"]
                        print("Guardian new object",num, serviceId, flush=True)

                        learnUntil = unlearnUntil = unblockUntil = 0
                        if ("learn_until" in guardian["spec"]):
                            learnUntil = float(guardian["spec"]["learn_until"])
                        if ("unlearn_until" in guardian["spec"]):
                            unlearnUntil = float(guardian["spec"]["unlearn_until"])
                        if ("unblock_until" in guardian["spec"]):
                            unblockUntil = float(guardian["spec"]["unblock_until"])

                        if serviceId not in serviceSpec:
                            addService(serviceId)
                        serviceSpec[serviceId]["learnUntil"] = learnUntil
                        serviceSpec[serviceId]["unblockUntil"] = unblockUntil
                        serviceSpec[serviceId]["unlearnUntil"] = unlearnUntil


                        if "_n" not in status:
                            serviceSpec[serviceId]["base_n"] = 0
                        else:
                            values = status["_n"]
                            if not isinstance(values, int):
                                serviceSpec[serviceId]["base_n"] = 0
                            else:
                                serviceSpec[serviceId]["base_n"] = int(values)
                        for gateId in gates:
                            if gateId in status:
                                serviceStatus[serviceId][gateId] = status[gateId]
                                for m in serviceModelers[serviceId][gateId]:
                                    m.crdload(status[gateId])
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
            serviceIds = list(serviceSpec.keys())
            if len(serviceIds):
                serviceId = random.choice(serviceIds)
                print("watchGuardians storing..", serviceId)
                n = serviceSpec[serviceId]["base_n"] + serviceSpec[serviceId]["my_n"]
                serviceSpec[serviceId]["my_n"] = 0

                status = {"_n": n}
                for gateId in serviceStatus[serviceId]:
                    status[gateId] = {}
                    for m in serviceModelers[serviceId][gateId]:
                        m.crdstore(status[gateId])
                status = {"status": status}
                print("Patching guardian crd...", serviceId, status, flush=True)
                patchGuardian(serviceId, status)
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
            version="v1",
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
                     version="v1",
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

                        for serviceId in serviceSpec:
                            if gateId in serviceModelers[serviceId]:
                                for m in serviceModelers[serviceId][gateId]:
                                    m.configFromGate(gateSpec)

                    elif t == "DELETED":
                        for serviceId in serviceSpec:
                            if gateId in serviceModelers[serviceId]:
                                del(serviceModelers[serviceId][gateId])
                                del(serviceStatus[serviceId][gateId])
                        del (gates[gateId])
                    reloadGuardians = True

                    print("GGG... Gate added:", num, gateId, resourceVersion, LearnLimit, AllowLimit, minimumLearning, flush=True)

                    '''
                    We cant delete Guardians as they may include user configs
                    for serviceId, service in services.items():
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
    # v1 = client.CoreV1Api()
    api = client.CustomObjectsApi()

    gateWatcher = threading.Thread(target=watchGates)
    gateWatcher.start()
except:
    print("config.load_incluster_config() exception")


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
