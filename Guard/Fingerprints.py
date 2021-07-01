import numpy as np
#from scipy.stats import norm
from Guard import Modeler


class Fingerprints(Modeler.Modeler):
    name = "fingerprints"
    maxConcepts = 4
    def __init__(self, spec):
        super().__init__(spec)


    def reset(self):
        self.indexes = np.array([ii for ii in range(self.numFeatures)])
        self.currentSample = np.zeros(self.numFeatures)

        self.featureValues = [{} for ii in range(self.numFeatures)]
        self.my_c = np.zeros([self.numFeatures, self.maxConcepts], dtype=int)
        self.base_c = np.zeros([self.numFeatures, self.maxConcepts], dtype=int)
        #self.c = np.zeros([self.numFeatures, self.maxConcepts], dtype=int)

        self.mean = np.zeros(self.numFeatures)
        self.std = np.ones(self.numFeatures)

    def load(self, fname_idx, key_idx, val):
        c = int(val["c"])
        uid = str(val["uid"])
        print(c, uid, type(c), type(uid))
        if c<1:
            raise Modeler.CrdError("c", val["c"], "c must be 1 or more")

        self.featureValues[fname_idx][uid] = key_idx
        self.base_c[fname_idx, key_idx] = c
        #c += self.my_c[fname_idx, key_idx]
        #self.c[fname_idx, key_idx] = c


    def store(self):
        # print("store starts with self.base_c + self.my_c", self.base_c,  self.my_c, self.base_c + self.my_c)
        self.base_c += self.my_c

        for fname_idx in range(self.numFeatures):
            for uid, key_idx in self.featureValues[fname_idx].items():
                c = int(self.base_c[fname_idx, key_idx])
                if (c <= 0):
                    continue
                val = {
                      "uid": uid
                    , "c": c
                }
                self.storeItem(fname_idx, key_idx, val)

        self.my_c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)

    def load2(self, mystatus):
        for i in range(len(mystatus)):
            for fv, m in mystatus[i].items():
                try:
                    if (fv == '*'):
                        self.featureValues[i] = ['*']
                        self.mask(i, "load2")
                        self.model[i] = np.zeros(self.maxConcepts, dtype=int)
                        self.base[i] = np.zeros(self.maxConcepts, dtype=int)
                        self.base[i, 0] = sum(mystatus[i].values())
                        break
                    j = self.featureValues[i].index(fv)
                    self.base[i, j] = int(m)
                    #print("load feature", fv, int(m))
                except:
                    if (self.maxConcepts > len(self.featureValues[i])):
                        j = len(self.featureValues[i])
                        self.featureValues[i].append(fv)
                        self.base[i, j] = int(m)
                    else:
                        self.featureValues[i] = ['*']
                        self.mask(i, "during load2")
                        self.model[i] = np.zeros(self.maxConcepts, dtype=int)
                        self.base[i] = np.zeros(self.maxConcepts, dtype=int)
                        self.model[i, 0] = self.n
                        self.base[i, 0] = sum(mystatus[i].values())
                        break

        self.n = np.sum(self.model + self.base, axis=1)[0]

        model = self.base + self.model

        self.mean = np.sum(model ** 2, axis=1) / self.n
        self.std = np.maximum(np.sqrt(np.sum(model ** 3, axis=1) / self.n - self.mean ** 2), np.ones(self.numFeatures))



    def store2(self, response):
        status = []
        self.base = self.base + self.model
        self.model = np.zeros([self.numFeatures, self.maxConcepts], dtype=int)

        for i in range(len(self.featureValues)):
            s = {}
            for fv, m in zip(self.featureValues[i], self.base[i]):
                s[str(fv)] = int(m)
                if (fv == '*'):
                    break
            status.append(s)

    def calc(self, data):
        idxarray = np.zeros(self.numFeatures, dtype=int)
        c = np.zeros(self.numFeatures, dtype=int)
        notfound = np.full(self.numFeatures, False)
        for fname_idx, uid in enumerate(data):
            if (uid in self.featureValues[fname_idx]):
                key_idx = self.featureValues[fname_idx][uid]
                idxarray[fname_idx] = key_idx
                c[fname_idx] = self.my_c[fname_idx, key_idx] + self.base_c[fname_idx, key_idx]
            else:
                notfound[fname_idx] = True

        self.currentSample = data
        self.currentIdx = idxarray
        self.notfound = notfound
        #print ("data, idxarray, notfound,  c, self.mean, self.std", data, idxarray, notfound,  c,  self.mean, self.std)

        p = (self.mean - np.minimum(c, self.mean)) / self.std
        p[notfound] = 100
        p[self.cmask] = 0
        self.p = p
        #print ("fingerprints self.p", self.p, c, self.mean)

    def learn(self):
        super().learn()
        newkeys = np.logical_and(self.notfound, np.logical_not(self.cmask))
        found = np.logical_not(self.notfound)

        for fname_idx in np.where(newkeys)[0]:
            uid = self.currentSample[fname_idx]
            print("*** Fingerprints *** Found new uid", uid)
            key_idx = self.getKeyIdx(fname_idx)
            if (key_idx != None):
                print("*** Fingerprints *** Learn new uid - free slot", key_idx)
                self.featureValues[fname_idx][uid] = key_idx
                self.currentIdx[fname_idx] = key_idx
                found[fname_idx] = True

                val = {
                    "uid": uid
                    , "c": 0
                }
                self.storeItem(fname_idx, key_idx, val)

        #print("Fingerprints drift all")


        indexes = self.indexes[found]
        currentIdx = self.currentIdx[found]
        #print("currentSample found", indexes, currentIdx)

        self.my_c[indexes, currentIdx] += 1

        c = self.base_c + self.my_c
        self.mean = np.sum(c ** 2, axis=1) / self.n
        self.std = np.maximum(np.sqrt(np.sum(c ** 3, axis=1) / self.n - self.mean ** 2), np.ones(self.numFeatures))
        #print ("Fingerprints learn", c, self.mean, self.std)

    def calc2(self, data):
        fprints = np.array(data, dtype=str)
        fprints[self.cmask] = '*'
        print ("fprints", fprints)
        featureValues = self.featureValues

        for i in range(self.numFeatures):
            value = fprints[i]
            try:
                self.currentSample[i] = featureValues[i].index(value)
            except:
                print("New fingerprint", i, " missing value", value, flush=True)
                if (self.maxConcepts > len(featureValues[i])):
                    self.currentSample[i] = len(featureValues[i])
                    featureValues[i].append(value)
                    print("New fingerprint", i, " is Now", len(featureValues[i]), " with value:", value)
                else:
                    featureValues[i] = ['*']
                    print("Masking out fingerprint", i)
                    self.mask(i, "during calc2")
                    self.currentSample[i] = 0
                    base_n = np.sum(self.base[i])
                    n = np.sum(self.model[i])
                    self.model[i] = np.zeros(self.maxConcepts, dtype=int)
                    self.base[i] = np.zeros(self.maxConcepts, dtype=int)
                    self.model[i, 0] = n
                    self.base[i, 0] = base_n


        #print (self.model)

        #print(std)

        #print(self.currentSample, self.model[self.indexes, self.currentSample], mean, std)
        #p = (self.model[self.indexes, self.currentSample]-mean)/std
        #print ("cdf of", self.model[self.indexes, self.currentSample]+1, (self.model[self.indexes, self.currentSample]+1 - self.mean)/self.std)
        #self.p = norm.cdf((self.model[self.indexes, self.currentSample]+1 - self.mean)/self.std)
        model = self.base[self.indexes, self.currentSample] + self.model[self.indexes, self.currentSample]+1
        self.p = -(model - self.mean)/self.std
        #self.p[self.n < self.minimumLearning] = 0




    def learn2(self):
        return


        indexes = self.indexes
        currentSample = self.currentSample
        print ("currentSample", currentSample)
        self.model[indexes, currentSample] += 1

        model = self.base + self.model
        #self.n[indexes] += 1
        self.n += 1
        self.mean = np.sum(model ** 2, axis=1) / self.n
        self.std = np.maximum(np.sqrt(np.sum(model ** 3, axis=1) / self.n - self.mean ** 2), np.ones(self.numFeatures))



Modeler.modelers.append(Fingerprints)
