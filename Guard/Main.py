from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
import random
import evaluator as evaluator
import numpy as np
import traceback
import sys
import os
import time

print("*** Guardian starts ***", flush=True)
def evaluate(serviceId, collectorId, triggerInstance, data):
    print ("evaluate ", serviceId, collectorId, triggerInstance, data)
    evaluator.evaluate(serviceId, collectorId, triggerInstance, data)
    return random.randint(0,1) == 1

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
staticDir = os.path.join(app.root_path, "..", "FrontEnd")


@app.route('/')
def send_homepage():
    print("** / called")
    return redirect('/web/index.html')


@app.route('/web/<path:path>')
def send_web(path):
    print("** /web/ called", staticDir, path)
    return send_from_directory(staticDir, path)


@app.route('/data/', methods = ["GET"])
def display():
    print("** /data called")
    d = evaluator.display()
    return jsonify(d)


@app.route('/data/<serviceid>', methods = ["GET", "POST"])
def displayService(serviceid):
    if (request.method == "GET"):
        spec = evaluator.getConfigGuardian(serviceid)
        print("** /dataService called GET", spec)

        now = time.time()
        data = {
            "learnUntil": max(spec.get("learnUntil", 0) - now, 0),
            "unblockUntil": max(spec.get("unblockUntil", 0) - now, 0),
            "unlearnUntil": max(spec.get("unlearnUntil", 0) - now, 0)
        }
        return jsonify(data)
    else: # "POST"
        print("** /dataService POST", request.json)
        spec = request.json
        data = {
            "learnUntil": spec.get("learnUntil", 0),
            "unblockUntil": spec.get("unblockUntil", 0),
            "unlearnUntil": spec.get("unlearnUntil", 0)
        }
        evaluator.configGuardian(serviceid, data)
        return ""

@app.route('/status/<serviceid>', methods = ["GET"])
def statusService(serviceid):
    print("** /statusService called GET")
    d = evaluator.displayService(serviceid)
    return jsonify(d)


@app.route('/reset/<serviceid>')
def resetService(serviceid):
    print("** /resetService called")
    evaluator.resetService(serviceid)
    return jsonify({"Reset": "OK"})


@app.route('/eval', methods=['POST'])
def eval():
    try:
        r = request.get_json()
        ret = evaluator.evaluate(    r["serviceId"]
                                   , r["gateId"]
                                   , r["triggerInstance"]
                                   , r["data"]
                                   )
        if (ret):
            return jsonify({"status": "OK"})
        print("Eval ended without success", flush=True)
        return jsonify({"status": "NOK"})

    except Exception as err:
        print("Error while processing eval")
        traceback.print_exc(file=sys.stdout)
        print("---------Error-------", flush=True)

    return jsonify({"status": "FAIL"})


'''
@app.route('/register', methods=['POST'])
def register():
        #print("Registration", flush=True)
    #try:
        r = request.get_json()
        if ("gateId" in r and "fingerprintNames" in r):
            evaluator.register(r["gateId"], r["fingerprintNames"]);
            return jsonify({"status": "OK"})
    #except Exception as err:
    #    print("Error while processing register", err)

    #return jsonify({"status": "NOK"})
'''

if __name__ == "__main__":
    print("Run in test mode")
    gateSpec = {
        "collectorId": "gate1test",
        "roundedMarkers": ["f1", "f2"],
        "minimumLearning": 1000,
        "fingerprints": ["f1", "f2"],
        "histograms": ["f1", "f2"],
        "AllowLimit": 10,
        "integers": ["f1", "f2"],
        "LearnLimit": 3,
        "markers": []
    }
    evaluator.controller.serviceSpec = {
        "myapp": {},
        "myotherapp": {}
    }
    evaluator.controller.serviceModelers = {
        "myapp": {
            "gate1":[m(gateSpec) for m in evaluator.controller.modelers],
            "gate2": [m(gateSpec) for m in evaluator.controller.modelers]
        },
        "myotherapp": {
                "gate1": [m(gateSpec) for m in evaluator.controller.modelers],
                "gate2": [m(gateSpec) for m in evaluator.controller.modelers]
        }
    }

    evaluator.controller.serviceStatus = {
        "myapp": {
            "gate1": {}
            , "gate2": {}
        },
        "myotherapp": {
            "gate1": {}
            , "gate2": {}
        }
    }
    app.run()

