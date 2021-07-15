import numpy as np
import sys
import traceback
import secrets
import random
import math
import time
# from scipy.stats import norm

modelers = []

class CrdError(Exception):
    """Exception raised for errors in the CRD.

    Attributes:
        Param -- input  in which the error occurred
        Value -- the value
        message -- explanation of the error
    """

    def __init__(self, param, val, message):
        self.param = param
        self.val = val
        self.message = message


class Modeler:
    name = "<Modeler Virtual>"
    maxConcepts = 1

    def __init__(self, spec):
        #print("New", self.name)
        self.numExpandedFeatures = 0
        self.configFromGate(spec)
        self.modelerReset()

        #print("INIT self.numExpandedFeatures =", self.numExpandedFeatures)

    def configFromGate(self, spec):
        #print(spec)
        self.featureNames = spec[self.name]
        self.LearnLimit = spec["LearnLimit"]
        self.AllowLimit = spec["AllowLimit"]
        self.minimumLearning = max(spec["minimumLearning"],150)


        if (hasattr(self, 'expandFeatures') and hasattr(self, 'expandData')):
            self.numExpandedFeatures = len(self.featureNames)
            self.featureNames = self.expandFeatures(self.featureNames)

        self.numFeatures = len(self.featureNames)
        #print(self.name, "has been configFromGate with", self.numFeatures, "features", flush=True)
        #print("FROMGATE self.numExpandedFeatures =", self.numExpandedFeatures)

    def modelerReset(self):
        print("Reset", self.name, "numFeatures", self.numFeatures)
        self.my_n = 0
        self.base_n = 0
        self.p = np.zeros(self.numFeatures)
        self.cmask = [False for ii in range(self.numFeatures)]
        self.status = {}
        self.keys = {}
        for fname in self.featureNames:
            self.status[fname] = {}
            self.keys[fname] = []
        self.reset()

    def mask(self, fname_idx, text):
        fname = self.featureNames[fname_idx]
        print("Modeler", self.name, fname, text)

        self.cmask[fname_idx] = True
        self.keys[fname] = []
        self.status[fname] = {"tombstone": {}}


    def crdload(self, status):
        #print(" CRD Loading", self.name)
        if not self.name in status:
            self.modelerReset()
            return

        mystatus = status[self.name]
        if not isinstance(mystatus, dict):
            self.modelerReset()
            return

        if "_n" not in status:
            self.modelerReset()
            return

        values = status["_n"]
        if not isinstance(values, int):
            self.modelerReset()
            return
        self.base_n = int(values)


        for fname, values in mystatus.items():
            if (fname[0] == "_"): #only old _n for now
                continue
            if fname not in self.featureNames:
                continue
            fname_idx = self.featureNames.index(fname)
            if self.cmask[fname_idx]:
                continue

            # update existing concepts
            keys = values.keys()
            if "tombstone" in keys:
                self.mask(fname_idx, "has tombstone during crdload")
                continue

            newKeys = []
            for key in keys:
                if key not in self.keys[fname]:
                    newKeys.append(key)
                    continue
                key_idx = self.keys[fname].index(key)
                val = values[key]
                if not val or not isinstance(val, dict) or 'c' not in val:
                    continue
                c = val["c"]
                if (not isinstance(c, int)) or c < 1:
                    continue
                try:
                    self.load(fname_idx, key_idx, val)
                except Exception as e:
                    print("illegal value while updating existing key in load", fname_idx, key_idx, val, e)

            # add new concepts
            for key in newKeys:
                val = values[key]
                #print ("New Concept loaded", key, val)
                if not val or not isinstance(val, dict) or 'c' not in val:
                    continue
                c = val["c"]
                if (not isinstance(c, int)) or c < 1:
                    continue

                key_idx = self.getKeyIdx(fname_idx, key=key)
                #print("New Concept loaded c", c, fname_idx, key_idx)
                if key_idx is None:
                    break
                try:
                    #print("New Concept loading")
                    self.load(fname_idx, key_idx, val)
                except Exception as e:
                    self.delKeyIdx(fname_idx, key_idx)
                    print("ilegal value during new key in load", fname_idx, key_idx, val, e)
        self.drift()

    def storeItem(self, fname_idx, key_idx, val):
        fname = self.featureNames[fname_idx]
        if key_idx >= len(self.keys[fname]):
            print("Modeler", self.name, fname, "BUG BUG BUG - StoreItem with illegal index!")
            return

        #print("Modeler", self.name, fname, "storeItem", key_idx, val)
        key = self.keys[fname][key_idx]
        self.status[fname][key] = val

    def getKeyIdx(self, fname_idx, key=None):
        fname = self.featureNames[fname_idx]
        key_idx = len(self.keys[fname])
        if (self.maxConcepts > key_idx):
            #print("Modeler", self.name, fname, "asks for getKeyIdx", key_idx)
            if not key:
                key = secrets.token_hex(nbytes=8)
            self.keys[fname].append(key)
            return key_idx
        self.mask(fname_idx, "masked by getKeyIdx")
        return None

    def delKeyIdx(self, fname_idx, key_idx):
        keys = []
        fname = self.featureNames[fname_idx]
        key = self.keys[fname].pop(key_idx)
        self.status[fname].pop(key, None)

    def crdstore(self, status):
        #print("Storing", self.name)
        n = self.base_n + self.my_n
        self.store()
        status[self.name] = self.status
        status["_n"] = n
        self.my_n = 0

    def assess(self, data):
        #print("ASSES self.numExpandedFeatures =", self.numExpandedFeatures)
        #print(data)
        data = data[self.name]
        if not data:
            print("Modeler", self.name, "assess - No Data", data)
            return([])
        #print("Asses", self.name, "has",len(data), "expand", self.numExpandedFeatures)
        if (self.numExpandedFeatures):
            if (len(data) != self.numExpandedFeatures):
                print("Modeler", self.name, "assess - wrong num of expanded features in data", len(data), self.numExpandedFeatures)
                raise
            data = self.expandData(data)
        if (len(data) != self.numFeatures):
            print("Modeler",self.name, "assess - wrong num of features in data", len(data), self.numFeatures)
            raise
        with np.errstate(invalid='raise', divide='raise'):
            try:
                self.my_n += 1
                self.calc(data)
                self.p[self.cmask] = 0
                n = self.base_n + self.my_n
                if self.minimumLearning < n:
                    return self.p.tolist()
            except:
                print(self.name, "Calc except during assess")
                traceback.print_exc(file=sys.stdout)

        return np.zeros(self.numFeatures).tolist()

    def verbose(self):
        print("Verbose", self.name, self.p)
        for fname, p in zip(self.featureNames, self.p):
            if p>self.AllowLimit:
                print (self.name, "is blocking based on", fname)
            elif p>self.LearnLimit:
                print (self.name, "avoid learning based on", fname)

    def reset(self):
        # virtual function for a modeler to reset the model
        pass

    def load(self, fname_idx, key_idx, val):
        # virtual function for a modeler to update model[(fname_idx, key_idx)] = val
        pass

    def store(self):
        # virtual function for a modeler to storeItem(fname_idx, key_idx,  model[(fname_idx, key_idx)]) for all items
        pass

    def calc(self, data):
        # virtual function for a modeler to calculate self.p based on sample
        pass

    def learn(self):  # (self, mask):
        # virtual function for a modeler to learn from sample
        pass

    def drift(self):
        # virtual function for a modeler to drift concepts
        pass

    #def expandFeatures(self, featureNames):
        # virtual function for a modeler to expand the crd feature list
    #    pass

    #def expandData(self, data):
        # virtual function for a modeler to expand the received sample
    #    pass

