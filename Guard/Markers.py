import numpy as np
# from scipy.stats import norm
import math
# import statistics

from Guard import Modeler
from Guard import gvu


class Markers(Modeler.Modeler):
    name = ["markers", "integers", "histograms"]
    maxConcepts = 4
    minSdev2Vals = [1E-20, 0.0625, 0.0625]
    noise = [1E-10, 0.25, 0.25]
    expand = [1, 1, 8]
    adjusted3Stddevs = [3.0009015323972648, 3.4399251966400537, 3.762361686930365, 4.031940947451361, 4.267351452930073,
                        4.479967979795997, 4.674375684341177, 4.8561403436466595, 5.025745559845473, 5.186364038411227,
                        5.339664503813593, 5.486382701563869, 5.627180177961487, 5.763642812678808, 5.893025139475057,
                        6.019482867955014, 6.141829509675763, 6.259437443791814, 6.374556711870281, 6.488039261091831,
                        6.59765041990006, 6.703772708966981, 6.80749557002031, 6.910096066371198, 7.011865780063083,
                        7.109135663499208, 7.20634995174296, 7.300935061856111, 7.394199928147074, 7.486169878092473,
                        7.576803103836148, 7.66504088199838, 7.752230331118843, 7.838033909731235, 7.922144218766907,
                        8.006497956851886, 8.08802556917874, 8.169268153284635, 8.24968067516429, 8.32853490964042]

    def __init__(self, spec):
        super().__init__(spec)
        self.threeStdQuantile = self.adjusted3Stddevs[0]


    def reset(self):
        self.mean = np.ones((self.numFeatures, self.maxConcepts))*np.finfo(np.float64).min
        self.sdev = np.ones((self.numFeatures, self.maxConcepts))

        self.z = np.zeros((self.numFeatures, self.maxConcepts))
        self.currentSample = np.zeros((self.numFeatures, self.maxConcepts))
        #self.c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)

        self.base_s = np.zeros((self.numFeatures, self.maxConcepts))
        self.base_s2 = np.zeros((self.numFeatures, self.maxConcepts))
        self.base_c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)


        self.my_s = np.zeros((self.numFeatures, self.maxConcepts))
        self.my_s2 = np.zeros((self.numFeatures, self.maxConcepts))
        self.my_c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)

        self.skippedSamples = [[] for _ in range(self.numFeatures)]
        self.g = [gvu.gvu() for _ in range(self.numFeatures)]
        self.minSdev2 = np.zeros((self.numFeatures, self.maxConcepts))
        i = 0
        for name_i in range(len(self.name)):
            name = self.name[name_i]

            for x in range(self.numExpandedFeaturesByName[name]):
                for j in range(self.maxConcepts):
                    self.minSdev2[i,j] = self.minSdev2Vals[name_i]
                self.g[i].clear()
                self.g[i].setNoise(self.noise[name_i])
                i = i + 1

    def load(self, fname_idx, key_idx, val):
        #print (val)
        c = int(val["c"])
        s = float(val["s"])
        s2 = float(val["s2"])
        if c<1:
            raise Modeler.CrdError("c", val["c"], "c must be 1 or more")

        # Squeeze down - TBD if 10,000 is the right place to squeeze
        if c > 10000:
            print ("Squeeze down", self.featureNames[fname_idx], c,s,s2)
            c /= 2
            s /= 2
            s2 /= 2

        s2 = max(s2, self.minSdev2[fname_idx, key_idx] * c + (s **2 ) / c )

        self.base_c[fname_idx, key_idx] = c
        self.base_s[fname_idx, key_idx] = s
        self.base_s2[fname_idx, key_idx] = s2

        c  += self.my_c[fname_idx, key_idx]
        s  += self.my_s[fname_idx, key_idx]
        s2 += self.my_s2[fname_idx, key_idx]

    def drift(self):
        w = np.where(self.base_c>0)
        c = self.base_c[w]
        s = self.base_s[w]
        s2 = self.base_s2[w]
        minSdev2 = self.minSdev2[w]

        m = s / c
        sdev = np.sqrt(np.maximum(s2 / c - np.square(m), minSdev2))

        #self.c[fname_idx, key_idx] = c
        self.mean[w] = m
        self.sdev[w] = sdev
        self.printCurrentFeatures()

    def store(self):
        #print("store starts with self.base_c + self.my_c", self.base_c,  self.my_c, self.base_c + self.my_c)

        self.base_c += self.my_c
        self.base_s += self.my_s
        self.base_s2 += self.my_s2

        for fname_idx in range(self.numFeatures):
            for key_idx in range(self.maxConcepts):
                c  = int(self.base_c[fname_idx, key_idx])
                if (c<=0):
                    continue
                # merge
                for key_idx_other in range(key_idx + 1, self.maxConcepts):
                    c_other = int(self.base_c[fname_idx, key_idx_other])
                    if (c_other <= 0):
                        continue
                    mu1 = self.mean[fname_idx][key_idx]
                    sdev1 = self.sdev[fname_idx][key_idx]
                    mu2 = self.mean[fname_idx][key_idx_other]
                    sdev2 = self.sdev[fname_idx][key_idx_other]
                    if ((mu1 - 3 * sdev1 < mu2 < mu1 + 3 * sdev1) or
                        (mu2 - 3 * sdev2 < mu1 < mu2 + 3 * sdev2)):
                        print("*** MERGING START ***", fname_idx, mu1, sdev1, mu2, sdev2)
                        c += c_other
                        s = self.base_s[fname_idx][key_idx] + self.base_s[fname_idx][key_idx_other]
                        s2 = self.base_s2[fname_idx][key_idx] + self.base_s2[fname_idx][key_idx_other]

                        self.base_c[fname_idx, key_idx] = c
                        self.base_s[fname_idx, key_idx] = s
                        self.base_s2[fname_idx, key_idx] = s2
                        self.base_c[fname_idx, key_idx_other] = 0

                        m = s / c
                        sdev = math.sqrt(max(s2 / c - m ** 2, self.minSdev2[fname_idx, key_idx]))
                        self.mean[fname_idx, key_idx] = m
                        self.sdev[fname_idx, key_idx] = sdev
                        self.delKeyIdx(fname_idx, key_idx_other)
                        print("*** MERGING END ***", fname_idx, m, sdev)

                val = {
                      "s2": float(self.base_s2[fname_idx, key_idx])
                    , "s":  float(self.base_s[fname_idx, key_idx])
                    , "c":  c
                }
                self.storeItem(fname_idx, key_idx, val)

        self.my_c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)
        self.my_s = np.zeros((self.numFeatures, self.maxConcepts))
        self.my_s2 = np.zeros((self.numFeatures, self.maxConcepts))

        self.printCurrentFeatures()

    def calc(self, data):
        self.currentSample = sarray = np.tile(data, (self.maxConcepts, 1)).T

        self.z = np.divide(np.absolute(sarray - self.mean), self.sdev)
        #print("markers self.z", self.z)
        self.p = np.amin(self.z, axis=1)
        #print ("markers self.p", self.p, sarray,  self.mean, np.absolute(sarray - self.mean), self.sdev, self.z)

    def learn(self):
        #print ("learn",self.p)
        for fname_idx in np.where(self.p >= self.threeStdQuantile)[0]:
            #print("*** Markers *** Learn ", fname_idx, self.p[fname_idx], self.g[fname_idx])
            self.p[fname_idx] = self.threeStdQuantile
            g = self.g[fname_idx]
            if (g.addPoint(self.currentSample[fname_idx][0]) > 100):
                #print("*** Markers *** Learn MEAN and SDEV")
                key_idx = self.getKeyIdx(fname_idx)
                if key_idx is not None:
                    #print("*** Markers *** Learn MEAN and SDEV - free slot", key_idx)
                    result = g.getGuassian()
                    mu = result["driftedGuassian"]["mu"]
                    sdev = max(result["driftedGuassian"]["sdev"], self.minSdev2[fname_idx, key_idx])
                    c = result["driftedGuassian"]["c"]
                    s = mu*c
                    s2 = (sdev**2 + mu**2)*c
                    self.my_c[fname_idx][key_idx] = c
                    self.my_s[fname_idx][key_idx] = s
                    self.my_s2[fname_idx][key_idx] = s2

                    #self.c[fname_idx][key_idx] = c
                    self.mean[fname_idx][key_idx] = mu
                    self.sdev[fname_idx][key_idx] = sdev
                    #print("driftedGuassian sdev ", sdev)
                    val = {
                        "s2": s2
                        , "s": s
                        , "c": c
                    }

                    self.storeItem(fname_idx, key_idx, val)
                    self.printCurrentFeatures()
                #print("*** Markers *** Learn MEAN and SDEV - clear")
                g.clear()


        indexs = (self.z == np.tile(self.p, (self.maxConcepts, 1)).T)
        #print("drift all ", indexs)
        s = self.currentSample[indexs]
        self.my_c[indexs] += 1
        self.my_s[indexs] += s
        self.my_s2[indexs] += np.square(s)

    def printCurrentFeatures(self):
        return
        for idx, name in enumerate(self.featureNames):
            print("printCurrentFeatures", name, self.mean[idx], self.sdev[idx], self.cmask[idx], len(self.g[idx].points), self.base_c[idx], self.base_s[idx], self.base_s2[idx])


Modeler.modelers.append(Markers)
