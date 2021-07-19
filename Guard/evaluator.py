import numpy as np

# import threading
import os
import sys
import traceback
import time


sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from Guard import controller

# globalData = threading.local()
count = 0


def resetService(serviceid):
    if serviceid not in controller.serviceStatus:
        return {}
    controller.deleteGuardian(serviceid)
    print("controller deletedGuardian", serviceid, flush=True)


def display():
    return list(controller.serviceStatus.keys())


def displayService(serviceId):
    if serviceid not in controller.serviceStatus:
        return {}
    data = {}
    for gateId in controller.serviceStatus[serviceId]:
        data[gateId] = controller.serviceStatus[serviceId][gateId]
    return data


def getConfigGuardian(serviceId):
    if serviceId in controller.serviceStatus:
        return controller.serviceSpec[serviceId]
    return {}

def configGuardian(serviceId, data):
    controller.configGuardian(serviceId, data)


def evaluate(serviceId, gateId, triggerInstance, data):
    # get the model for (serviceId, collectorId)
    global count
    count += 1
    print("*** Evaluate:", serviceId, gateId, triggerInstance, flush=True)

    gateSpec, guardSpec, modelers  = controller.serve(serviceId, gateId)

    try:
        LearnLimit = float(gateSpec["LearnLimit"])
        AllowLimit = float(gateSpec["AllowLimit"])
        minimumLearning = int(gateSpec["minimumLearning"])
        learnUntil = guardSpec["learnUntil"]
        unblockUntil = guardSpec["unblockUntil"]
        unlearnUntil = guardSpec["unlearnUntil"]

        now = time.time()
    except:
        print("Gate is not proper - missing data", gateSpec)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
        return np.array([True])

    n = guardSpec["my_n"] + 1
    guardSpec["my_n"] = n
    n += guardSpec["base_n"]
    p = []
    for m in modelers:
        p += m.assess(data)
        m.verbose()

    print ("**********> Results: p =",p, serviceId, gateId)
    print("**********> LearnLimit", LearnLimit, "AllowLimit", AllowLimit)

    if minimumLearning < n:
        if now > unlearnUntil:
            if now < learnUntil:
                print("Learning enforced until", serviceId, gateId, learnUntil, "Also allow!")
                for m in modelers:
                    m.learn()
                    return True
            elif sum(i > LearnLimit for i in p) < 2:
                print("Learning OKed by Ensemble", serviceId, gateId)
                for m in modelers:
                    m.learn()
            else:
                print("Learning NOKed by Ensemble", serviceId, gateId)
        else:
            print("Unlearning is activated until ", serviceId, gateId, unlearnUntil)
    else:
        print("minimumLearning not met - Allow", serviceId, gateId, minimumLearning, n)
        for m in modelers:
            m.learn()
        return True

    if unblockUntil >= now:
        print("Allow OK until", serviceId, gateId, unblockUntil, flush=True)
        return True
    elif sum(i > AllowLimit for i in p) < 2:
        print("Allow OK by ensemble", serviceId, gateId, flush=True)
        return True

    print("Allow NOK by ensemble", serviceId, gateId, flush=True)
    return False


