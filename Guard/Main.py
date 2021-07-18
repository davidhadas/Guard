from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
import random
import evaluator as evaluator
import numpy as np
import traceback
import sys
import os

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
    print("send_web", staticDir, path)
    return send_from_directory(staticDir, path)

@app.route('/data/', methods = ["GET"])
def display():
    print("** /display called")
    d = evaluator.display()
    return jsonify(d)


@app.route('/data/<serviceid>', methods = ["GET"])
def displayService(serviceid):
    print("**  /displayService called")
    d = evaluator.displayService(serviceid)
    return jsonify(d)


@app.route('/data/<serviceid>/<gateid>', methods = ["GET", "POST"])
def displayServiceGate(serviceid, gateid):
    if (request.method == "GET"):
        print ("** /displayServiceGate called")
        d = evaluator.displayServiceGate(serviceid, gateid)
        return jsonify(d)
    else: # "POST"
        print("** /displayServiceGate POST", request.json)
        evaluator.configGuardian(serviceid, gateid, request.json)
        return ""

@app.route('/reset/<serviceid>/<gateid>')
def resetServiceGate(serviceid, gateid):
    print("** /resetServiceGate called")
    evaluator.resetServiceGate(serviceid, gateid)
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
    evaluator.controller.services = {
        "myapp": {
            "gate1": {
                 "modelers": [m(gateSpec) for m in evaluator.controller.modelers],
                 "status": {},
                 "learnUntil": 0,
                 "unblockUntil": 0,
                 "unlearnUntil": 0,
                 "my_n": 0,
                 "base_n": 0}
            , "gate2": {
                 "modelers": [m(gateSpec) for m in evaluator.controller.modelers],
                 "status": {},
                 "learnUntil": 0,
                 "unblockUntil": 0,
                 "unlearnUntil": 0,
                 "my_n": 0,
                 "base_n": 0}
        },
        "myotherapp": {
            "gate1": {
                "modelers": [m(gateSpec) for m in evaluator.controller.modelers],
                "status": {},
                "learnUntil": 0,
                "unblockUntil": 0,
                "unlearnUntil": 0,
                "my_n": 0,
                "base_n": 0}
            , "gate2": {
                "modelers": [m(gateSpec) for m in evaluator.controller.modelers],
                "status": {},
                "learnUntil": 0,
                "unblockUntil": 0,
                "unlearnUntil": 0,
                "my_n": 0,
                "base_n": 0}
        }
    }
    app.run()

