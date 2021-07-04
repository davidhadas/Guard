from flask import Flask, request, jsonify
import random
import evaluator as evaluator
import numpy as np
import traceback
import sys

print("*** Guardian starts ***", flush=True)


def evaluate(serviceId, collectorId, triggerInstance, data):
    print ("evaluate ", serviceId, collectorId, triggerInstance, data)
    evaluator.evaluate(serviceId, collectorId, triggerInstance, data)
    return random.randint(0,1) == 1


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True



@app.route('/reset/<serviceid>/<gateid>')
def resetServiceGate(serviceid, gateid):
    print ("/resetServiceGate called")
    evaluator.resetServiceGate(serviceid, gateid)
    return jsonify({"Reset": "OK"})

@app.route('/display/')
def display():
    print("/display called")
    d = evaluator.display()
    return jsonify(d)

@app.route('/display/<serviceid>')
def displayService(serviceid):
    print("/displayService called")
    d = evaluator.displayService(serviceid)
    return jsonify(d)


@app.route('/display/<serviceid>/<gateid>')
def displayServiceGate(serviceid, gateid):
    print ("/displayServiceGate called")
    d = evaluator.displayServiceGate(serviceid, gateid)
    return jsonify(d)


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

