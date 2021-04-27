import numpy as np

# import threading
import os
import sys
import traceback


sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import controller

# globalData = threading.local()
count = 0


def evaluate(serviceId, gateId, triggerInstance, data):
    # get the model for (serviceId, collectorId)
    global count
    count += 1
    print("evaluate count:", count, flush=True)

    gateSpec, modelers  = controller.serve(serviceId, gateId)

    try:
        LearnLimit = float(gateSpec["LearnLimit"])
        AllowLimit = float(gateSpec["AllowLimit"])
        minimumLearning = int(gateSpec["minimumLearning"])

    except:
        print("Gate is not proper - missing data", gateSpec)
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)
        return np.array([True])

    p = []
    for m in modelers:
        p += m.assess(data)
        m.verbose()

    print ("**********> Results: p =",p)
    if all(i <= LearnLimit for i in p):
        print("Learning OK")
        for m in modelers:
            m.learn()
    else:
        print("Learning NOK")

    if all(i <= AllowLimit for i in p):
        print("Allow OK", flush=True)
        return True
    else:
        print("Allow NOK", flush=True)
    return False


'''
register("c1", ["aa", "bb"])

for i in range(20):
    for i in range(100):
        p = evaluate("s1", "c1", "myuuid", ["abc", "xx"])
    for i in range(2):
        p = evaluate("s1", "c1", "myuuid", ["abc1", "xx"])
        print(p)
for i in range(0):
    p = evaluate("s1", "c1", "myuuid", ["abc1", "xx"])
    print(p)
'''

