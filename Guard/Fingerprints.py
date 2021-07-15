import numpy as np
#from scipy.stats import norm
from Guard import Modeler


class Fingerprints(Modeler.Modeler):
    name = "fingerprints"
    maxConcepts  = 4
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
        if (c>10000): # squeeze down
            print("Squeeze down fingerprint", self.featureNames[fname_idx], c)
            c /= 2

        self.featureValues[fname_idx][uid] = key_idx
        self.base_c[fname_idx, key_idx] = c
        #c += self.my_c[fname_idx, key_idx]
        #self.c[fname_idx, key_idx] = c

    def drift(self):
        c = self.base_c
        n = np.sum(c, axis=1)

        self.mean = np.sum(c ** 2, axis=1) / n
        self.std = np.maximum(np.sqrt(np.sum(c ** 3, axis=1) / n - self.mean ** 2), np.ones(self.numFeatures))

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
        #print ("fingerprints calc", self.p, c, self.mean, self.std)

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

        #print (">> Fingerprints learn", c, n, self.mean, np.sum(c ** 3, axis=1) / n - self.mean ** 2, self.std)


Modeler.modelers.append(Fingerprints)
