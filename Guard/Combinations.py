import numpy as np
# from scipy.stats import norm
import math
# import statistics

from Guard import Modeler
from Guard import gvu2


class Combinations(Modeler.Modeler):
    name = ["combinations"]
    maxConcepts = 4
    expand = [1]
    maxError = 3
    noise = [0.25]
    minSdev2 = 1E-20

    def __init__(self, spec):
        self.lr = 0.001
        super().__init__(spec)

    def config(self, spec):
        pass

    def reset(self):
        self.n = 0

        self.c  = np.zeros((self.numFeatures, self.maxConcepts))
        #self.serror  = np.zeros((self.numFeatures, self.maxConcepts))
        #self.s2error = np.zeros((self.numFeatures, self.maxConcepts))
        #self.muerror  = np.zeros((self.numFeatures, self.maxConcepts))
        #self.stderror = np.ones((self.numFeatures, self.maxConcepts))
        self.muerror = 0.01
        self.stderror = 0.03

        self.bih  = np.zeros((self.numFeatures, self.maxConcepts))
        self.wi1h = np.random.uniform(0.01,0.99, (self.numFeatures, self.maxConcepts))
        self.wi2h = np.random.uniform(0.01, 0.99, (self.numFeatures, self.maxConcepts))

        self.bho1 = np.zeros((self.numFeatures, self.maxConcepts))
        self.bho2 = np.zeros((self.numFeatures, self.maxConcepts))
        self.who1 = np.random.uniform(0.01, 0.99, (self.numFeatures, self.maxConcepts))
        self.who2 = np.random.uniform(0.01, 0.99, (self.numFeatures, self.maxConcepts))

        self.wi1hgradient = np.zeros((self.numFeatures, self.maxConcepts))
        self.wi2hgradient = np.zeros((self.numFeatures, self.maxConcepts))
        self.bihgradient  = np.zeros((self.numFeatures, self.maxConcepts))

        self.who1gradient = np.zeros((self.numFeatures, self.maxConcepts))
        self.bho1gradient = np.zeros((self.numFeatures, self.maxConcepts))
        self.who2gradient = np.zeros((self.numFeatures, self.maxConcepts))
        self.bho2gradient = np.zeros((self.numFeatures, self.maxConcepts))

        self.min1 = np.zeros((self.numFeatures, self.maxConcepts))
        self.delta1 = np.ones((self.numFeatures, self.maxConcepts))
        self.min2 = np.zeros((self.numFeatures, self.maxConcepts))
        self.delta2 = np.ones((self.numFeatures, self.maxConcepts))

        self.currentSample = np.zeros((self.numFeatures, self.maxConcepts))

        self.g2 = [gvu2.gvu2() for _ in range(self.numFeatures)]
        for g2 in self.g2:
            g2.clear()
            g2.setNoise(self.noise[0])

        self.network_error = 0.01 * np.ones((self.numFeatures, self.maxConcepts))

        self.indexes = np.array([ii for ii in range(self.numFeatures)])

    def load(self, fname_idx, key_idx, val):
        c = int(val["c"])
        if c < 1:
            raise Modeler.CrdError("c", val["c"], "c must be 1 or more")

            # Squeeze down - TBD if 10,000 is the right place to squeeze
        if c > 10000:
            print("Squeeze down", self.featureNames[fname_idx], c, s, s2)
            c /= 2

        self.c[fname_idx, key_idx] = c
        self.wi1h[fname_idx, key_idx] = float(val["wi1h"])
        self.wi2h[fname_idx, key_idx] = float(val["wi2h"])
        self.bih[fname_idx, key_idx] = float(val["bih"])
        self.who1[fname_idx, key_idx] = float(val["who1"])
        self.bho1[fname_idx, key_idx] = float(val["bho1"])
        self.who2[fname_idx, key_idx] = float(val["who2"])
        self.bho2[fname_idx, key_idx] = float(val["bho2"])
        self.min1[fname_idx, key_idx] = float(val["min1"])
        self.delta1[fname_idx, key_idx] = float(val["delta1"])
        self.min2[fname_idx, key_idx] = float(val["min2"])
        self.delta2[fname_idx, key_idx] = float(val["delta2"])

    def drift(self):
        pass
        self.printCurrentFeatures()

    def storeOne(self, fname_idx, key_idx):
        val = {
            "wi1h": float(self.wi1h[fname_idx, key_idx])
            , "wi2h": float(self.wi2h[fname_idx, key_idx])
            , "bih": float(self.bih[fname_idx, key_idx])
            , "who1": float(self.who1[fname_idx, key_idx])
            , "bho1": float(self.bho1[fname_idx, key_idx])
            , "who2": float(self.who2[fname_idx, key_idx])
            , "bho2": float(self.bho2[fname_idx, key_idx])
            , "min1": float(self.min1[fname_idx, key_idx])
            , "delta1": float(self.delta1[fname_idx, key_idx])
            , "min2": float(self.min2[fname_idx, key_idx])
            , "delta2": float(self.delta2[fname_idx, key_idx])
            , "c": int(self.c[fname_idx, key_idx])
        }
        self.storeItem(fname_idx, key_idx, val)

    def store(self):
        for fname_idx in range(self.numFeatures):
            for key_idx in range(self.maxConcepts):
                self.storeOne(fname_idx, key_idx)


    def calc(self, data):
        data = np.array(data)
        #print ("self.numFeatures", self.numFeatures)
        #print("data",data)
        self.currentSample1 = d1 = (data[:,0] - self.min1)/self.delta1
        self.currentSample2 = d2 = (data[:,1] - self.min2)/self.delta2
        #print("d1",d1)
        if self.dlevel >= 3:
            print("min1", self.min1, "min2", self.min2, "delta1", self.delta1, "delta2", self.delta2)

        if self.dlevel >= 2:
            print("d1",d1, "d2", d2)
        #sarray1 = np.tile(d1, (self.maxConcepts, 1)).T
        #sarray2 = np.tile(d2, (self.maxConcepts, 1)).T
        #print ("sarray1", sarray1)

        self.h = self.bih + np.multiply(self.wi1h, d1) +  np.multiply(self.wi2h, d2)
        self.h[self.h<0] *= 0.01

        self.o1 = self.bho1 + np.multiply(self.who1, self.h)
        self.o2 = self.bho2 + np.multiply(self.who2, self.h)
        self.o1[self.o1 < 0] *= 0.01
        self.o2[self.o2 < 0] *= 0.01


        e = (self.o1 - d1) ** 2 + (self.o2 - d2) ** 2

        #self.error = (e/self.network_error
        self.error = np.divide(np.maximum(e - self.muerror, 0), self.stderror)
        self.error[self.unused] = 1000

        self.minz = np.argmin(self.error, axis=1)
        self.p = self.error[self.indexes, self.minz]
        #print("In", d1[0][0], d2[0][0], "out", self.o1, self.o2)
        if self.p[0]> 0 and self.p[0] != 1000:
            print("self.p[0]", self.p[0], "data", data, "e", e, "minz", self.minz, "error", self.error)
        if self.dlevel >= 3:
            print ("self.error", self.error)
            print("self.minz", self.minz)
            print("self.p", self.p)

        #self.p = np.amin(self.error, axis=1)

    def addConcept1(self, fname_idx, key_idx, points0, points1):
        #print("*** Combinations ***", points0, points1)
        wi1h = self.wi1h[fname_idx, key_idx]
        wi2h = self.wi2h[fname_idx, key_idx]
        bih = self.bih[fname_idx, key_idx]

        who1 = self.who1[fname_idx, key_idx]
        bho1 = self.bho1[fname_idx, key_idx]
        who2 = self.who2[fname_idx, key_idx]
        bho2 = self.bho2[fname_idx, key_idx]



        for i in range(1000):
            for (i1, i2) in zip(points0, points1):
                wi1hgradient = wi2hgradient = bihgradient = 0
                who1gradient = who2gradient = bho1gradient = bho2gradient = 0
                h = bih + wi1h * i1 + wi2h * i2
                if (h < 0):
                    h *= 0.01

                o1 = bho1 + who1 * h
                o2 = bho2 + who2 * h
                if (o1 < 0):
                    o1 *= 0.01
                if (o2 < 0):
                    o2 *= 0.01

                o1error = i1 - o1
                o2error = i2 - o2

                o1delta = np.minimum(o1error, 1E10)
                if i1 < 0:
                    o1delta *= 0.01
                o2delta = np.minimum(o2error, 1E10)
                if i2 < 0:
                    o2delta *= 0.01

                hdelta = np.minimum(o1delta * who1 + o2delta * who2, 1E10)
                if h < 0:
                    hdelta *= 0.01

                wi1hgradient += hdelta * i1
                wi2hgradient += hdelta * i2
                bihgradient += hdelta

                who1gradient += o1delta * h
                who2gradient += o2delta * h
                bho1gradient += o1delta
                bho2gradient += o2delta
                wi1h += self.lr * wi1hgradient
                wi2h += self.lr * wi2hgradient
                bih += self.lr * bihgradient

                who1 += self.lr * who1gradient
                bho1 += self.lr * bho1gradient
                who2 += self.lr * who2gradient
                bho2 += self.lr * bho2gradient
            # val = {
            #    "wi1h": float(wi1h)
            #    , "wi2h": float(wi2h)
            #    , "bih": float(bih)
            #    , "who1": float(who1)
            #    , "bho1": float(bho1)
            #    , "who2": float(who2)
            #    , "bho2": float(bho2)
            # }
            # print(val)

        self.wi1h[fname_idx, key_idx] = wi1h
        self.wi2h[fname_idx, key_idx] = wi2h
        self.bih[fname_idx, key_idx] = bih

        self.who1[fname_idx, key_idx] = who1
        self.bho1[fname_idx, key_idx] = bho1
        self.who2[fname_idx, key_idx] = who2
        self.bho2[fname_idx, key_idx] = bho2


        print(fname_idx, key_idx, val)
        self.printCurrentFeatures()

    def addConcept (self, fname_idx, key_idx,  points1, points2):
        min1 = min2 = np.finfo(np.float64).max
        max2 = max1 = np.finfo(np.float64).min

        for (i1, i2) in zip(points1, points2):
            min1 = min(min1, i1)
            min2 = min(min2, i2)
            max1 = max(max1, i1)
            max2 = max(max2, i2)

        delta1 = max(max1 - min1, self.noise[0])
        delta2 = max(max2 - min2, self.noise[0])

        points = []
        for (i1, i2) in zip(points1, points2):
            points.append(((i1-min1)/delta1, (i2-min2)/delta2))

        print("*** Combinations ***", points)
        wi1h = self.wi1h[fname_idx, key_idx]
        wi2h = self.wi2h[fname_idx, key_idx]
        bih = self.bih[fname_idx, key_idx]

        who1 = self.who1[fname_idx, key_idx]
        bho1 = self.bho1[fname_idx, key_idx]
        who2 = self.who2[fname_idx, key_idx]
        bho2 = self.bho2[fname_idx, key_idx]

        for i in range(1000):
            #c = serror = s2error = 0
            wi1hgradient = wi2hgradient = bihgradient = 0
            who1gradient = who2gradient = bho1gradient = bho2gradient = 0
            for (i1, i2) in points:
                h = bih + wi1h * i1 + wi2h * i2
                if (h < 0):
                    h *= 0.01

                o1 = bho1 + who1 * h
                o2 = bho2 + who2 * h
                if (o1 < 0):
                    o1 *= 0.01
                if (o2 < 0):
                    o2 *= 0.01

                o1error = i1 - o1
                o2error = i2 - o2

                e = o1error**2+o2error**2
                #c += 1
                #serror += e
                #s2error += e**2

                o1delta = min(o1error, 1E10)
                if i1 < 0:
                    o1delta *= 0.01
                o2delta = min(o2error, 1E10)
                if i2 < 0:
                    o2delta *= 0.01

                hdelta = min(o1delta * who1 + o2delta * who2, 1E10)
                if h < 0:
                    hdelta *= 0.01

                wi1hgradient += hdelta * i1
                wi2hgradient += hdelta * i2
                bihgradient += hdelta

                who1gradient += o1delta * h
                who2gradient += o2delta * h
                bho1gradient += o1delta
                bho2gradient += o2delta
            wi1h += self.lr * wi1hgradient
            wi2h += self.lr * wi2hgradient
            bih += self.lr * bihgradient

            who1 += self.lr * who1gradient
            bho1 += self.lr * bho1gradient
            who2 += self.lr * who2gradient
            bho2 += self.lr * bho2gradient

            #muerror = serror / c
            #stderror = math.sqrt(max(s2error / c - muerror ** 2, self.minSdev2))
            #muerror = 0.01
            #stderror = 0.03
            #print("muerror", muerror, "stderror", stderror)

            # val = {
            #    "wi1h": float(wi1h)
            #    , "wi2h": float(wi2h)
            #    , "bih": float(bih)
            #    , "who1": float(who1)
            #    , "bho1": float(bho1)
            #    , "who2": float(who2)
            #    , "bho2": float(bho2)
            # }
            # print(val)


        #self.muerror[fname_idx, key_idx] = muerror
        #self.stderror[fname_idx, key_idx] = stderror
        c = len(points)

        self.c[fname_idx, key_idx] = c
        self.wi1h[fname_idx, key_idx] = wi1h
        self.wi2h[fname_idx, key_idx] = wi2h
        self.bih[fname_idx, key_idx] = bih

        self.who1[fname_idx, key_idx] = who1
        self.bho1[fname_idx, key_idx] = bho1
        self.who2[fname_idx, key_idx] = who2
        self.bho2[fname_idx, key_idx] = bho2

        self.min1[fname_idx, key_idx] = min1
        self.delta1[fname_idx, key_idx] = delta1
        self.min2[fname_idx, key_idx] = min2
        self.delta2[fname_idx, key_idx] = delta2

        self.storeOne(fname_idx, key_idx)
        self.printCurrentFeatures()

    def learn(self):
        #print ("self.p", self.p)
        #print("*** Combinations *** Learn ",self.p, np.where(self.p > self.maxError)[0])
        for fname_idx in np.where(self.p > self.maxError)[0]:
            minz = self.minz[fname_idx]
            if (self.g2[fname_idx].addPoint((self.currentSample1[fname_idx][minz], self.currentSample2[fname_idx][minz])) > 100):
                print("*** Combinations *** Learn MEAN and SDEV")
                key_idx = self.getKeyIdx(fname_idx)
                if key_idx is not None:
                    print("*** Combinations *** Learn MEAN and SDEV - free slot", key_idx)
                    points1, points2 = self.g2[fname_idx].getGuassian()
                    self.addConcept(fname_idx, key_idx, points1, points2)
                print("*** Combinations *** Learn MEAN and SDEV - clear")
                self.g2[fname_idx].clear()

        indexes = np.where(self.p <= self.maxError)[0]
        if indexes.shape[0] > 0:
            minz = self.minz[indexes]

            #print (indexes, minz)
            o1 = self.o1[indexes, minz]
            o2 = self.o2[indexes, minz]
            who2 = self.who2[indexes, minz]
            who1 = self.who1[indexes, minz]
            h = self.h[indexes, minz]
            i1 = self.currentSample1[indexes, minz]
            i2 = self.currentSample2[indexes, minz]

            o1error = i1 - o1
            o2error = i2 - o2

            o1delta = np.minimum(o1error, 1E10)
            o1delta[i1 < 0] *= 0.01
            o2delta = np.minimum(o2error, 1E10)
            o2delta[i2 < 0] *= 0.01

            hdelta = np.minimum(o1delta * who1 + o2delta * who2, 1E10)
            hdelta[h < 0] *= 0.01

            self.c[indexes, minz] += 1
            #self.serror[indexes, minz] += self.p
            #self.s2error[indexes, minz] += self.p ** 2

            self.network_error[indexes, minz] = 0.97 * self.network_error[indexes, minz] + 0.03 * self.p

            self.wi1hgradient[indexes, minz] += hdelta * i1
            self.wi2hgradient[indexes, minz] += hdelta * i2
            self.bihgradient[indexes, minz]  += hdelta

            self.who1gradient[indexes, minz] += o1delta * h
            self.who2gradient[indexes, minz] += o2delta * h
            self.bho1gradient[indexes, minz] += o1delta
            self.bho2gradient[indexes, minz] += o2delta

            #print("wi1hgradient", self.wi1hgradient)
            self.n +=1
            if (self.n % 100==0):
                print("Minibatch")
                # Mini batch - once in a while (maybe in crdstore) - done on all autoencoders in parallel
                self.wi1h += self.lr * self.wi1hgradient
                self.wi2h += self.lr * self.wi2hgradient
                self.bih +=  self.lr * self.bihgradient

                self.who1 += self.lr * self.who1gradient
                self.bho1 += self.lr * self.bho1gradient
                self.who2 += self.lr * self.who2gradient
                self.bho2 += self.lr * self.bho2gradient

                self.wi1hgradient = np.zeros((self.numFeatures, self.maxConcepts))
                self.wi2hgradient = np.zeros((self.numFeatures, self.maxConcepts))
                self.bihgradient  = np.zeros((self.numFeatures, self.maxConcepts))

                self.who1gradient  = np.zeros((self.numFeatures, self.maxConcepts))
                self.bho1gradient = np.zeros((self.numFeatures, self.maxConcepts))
                self.who2gradient  = np.zeros((self.numFeatures, self.maxConcepts))
                self.bho2gradient = np.zeros((self.numFeatures, self.maxConcepts))

                if (self.lr > 0.001):
                    self.lr = self.lr * 0.99

    def printCurrentFeatures(self):
        return
        for idx, name in enumerate(self.featureNames):
            print("printCurrentFeatures", name)

Modeler.modelers.append(Combinations)