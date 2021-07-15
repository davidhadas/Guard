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


def resetServiceGate(serviceid, gateid):
    if serviceid not in controller.services or gateid not in controller.services[serviceid]:
        return {}
    controller.deleteGuardian(gateid, serviceid)
    controller.services[serviceid][gateid] = []
    print("controller deletedGuardian", serviceid, gateid, flush=True)


def display():
    return list(controller.services.keys())


def displayService(serviceid):
    if serviceid not in controller.services:
        return {}
    return list(controller.services[serviceid].keys())


def displayServiceGate(serviceid, gateid):
    if serviceid not in controller.services or gateid not in controller.services[serviceid]:
        return {}
    return controller.services[serviceid][gateid]["status"]


def evaluate(serviceId, gateId, triggerInstance, data):
    # get the model for (serviceId, collectorId)
    global count
    count += 1
    print("*** Evaluate:", serviceId, gateId, triggerInstance, flush=True)

    gateSpec, guardSpec  = controller.serve(serviceId, gateId)


    try:
        LearnLimit = float(gateSpec["LearnLimit"])
        AllowLimit = float(gateSpec["AllowLimit"])
        minimumLearning = int(gateSpec["minimumLearning"])
        learnUntil = guardSpec["learnUntil"]
        unblockUntil = guardSpec["unblockUntil"]
        unlearnUntil = guardSpec["unlearnUntil"]
        modelers = guardSpec["modelers"]
        now = time.time()
    except:
        print("Gate is not proper - missing data", gateSpec)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
        return np.array([True])

    p = []
    for m in modelers:
        p += m.assess(data)
        m.verbose()

    print ("**********> Results: p =",p, serviceId, gateId)

    if now > unlearnUntil and (now < learnUntil or sum(i > LearnLimit for i in p) < 2):
        print("Learning OK", serviceId, gateId)
        for m in modelers:
            m.learn()
    else:
        print("Learning NOK", serviceId, gateId)

    if unblockUntil < time.time() or sum(i > AllowLimit for i in p) < 2:
        print("Allow OK", flush=True)
        return True
    else:
        print("Allow NOK", flush=True)
    return False


