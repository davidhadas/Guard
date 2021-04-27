from flask import Flask, request, jsonify
import random
import CF.cf.evaluator as evaluator
import numpy as np
import traceback
import sys

print("*** Guardian starts ***", flush=True)


def evaluate(serviceId, collectorId, triggerInstance, data):
    print ("evaluate ", serviceId, collectorId, triggerInstance, data)
    evaluator.evaluate(serviceId, collectorId, triggerInstance, data)
    return random.randint(0,1) == 1


app = Flask(__name__)


@app.route('/')
def index():
    print ("/ called")
    return 'Hello world!'


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

