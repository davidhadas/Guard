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
    n = guardSpec["my_n"] + 1
    guardSpec["my_n"] = n
    n += guardSpec["base_n"
    p = []
    for m in modelers:
        p += m.assess(data)
        m.verbose()

    if
        return self.p.tolist()

    print ("**********> Results: p =",p, serviceId, gateId)
    print("**********> LearnLimit", LearnLimit, "AllowLimit", AllowLimit)

    if minimumLearning < n:
        if now > unlearnUntil:
            if now < learnUntil:
                print("Learning enforced until", serviceId, gateId, learnUntil)
                for m in modelers:
                    m.learn()
            elif sum(i > LearnLimit for i in p) < 2:
                print("Learning OKed by Ensemble", serviceId, gateId)
                for m in modelers:
                    m.learn()
            else:
                print("Learning NOKed by Ensemble", serviceId, gateId)
        else:
            print("Unlearning is activated until ", serviceId, gateId, unlearnUntil)
    else:
        print("minimumLearning not met", serviceId, gateId, minimumLearning, n)

    if unblockUntil > time.time():
        print("Allow OK until", serviceId, gateId, unblockUntil, flush=True)
        return True
    elif sum(i > AllowLimit for i in p) < 2:
        print("Allow OK by ensemble", serviceId, gateId, flush=True)
        return True

    print("Allow NOK by ensemble", serviceId, gateId, flush=True)
    return False


