import numpy as np
# from scipy.stats import norm
import Modeler
import math
# import statistics



class Markers(Modeler.Modeler):
    name = "markers"
    maxConcepts = 4
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
        self.c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)

        self.base_s = np.zeros((self.numFeatures, self.maxConcepts))
        self.base_s2 = np.zeros((self.numFeatures, self.maxConcepts))
        self.base_c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)


        self.my_s = np.zeros((self.numFeatures, self.maxConcepts))
        self.my_s2 = np.zeros((self.numFeatures, self.maxConcepts))
        self.my_c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)

        self.skippedSamples = [[] for _ in range(self.numFeatures)]

    def load(self, fname_idx, key_idx, val):
        c = int(val["c"])
        s = float(val["s"])
        s2 = float(val["s2"])
        if c<1:
            raise Modeler.CrdError("c", val["c"], "c must be 1 or more")

        self.base_c[fname_idx, key_idx]  = c
        self.base_s[fname_idx, key_idx]  = s
        self.base_s2[fname_idx, key_idx] = s2

        c  += self.my_c[fname_idx, key_idx]
        s  += self.my_s[fname_idx, key_idx]
        s2 += self.my_s2[fname_idx, key_idx]
        m = s / c
        sdev = math.sqrt(max(s2 / c - m ** 2, np.finfo(np.float64).eps))

        self.c[fname_idx, key_idx] = c
        self.mean[fname_idx, key_idx] = m
        self.sdev[fname_idx, key_idx] = sdev
        print("mean is now", self.mean)
        print("sdev is now", self.sdev)



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
                val = {
                      "s2": float(self.base_s2[fname_idx, key_idx])
                    , "s":  float(self.base_s[fname_idx, key_idx])
                    , "c":  c
                }
                self.storeItem(fname_idx, key_idx,val)

        self.my_c = np.zeros((self.numFeatures, self.maxConcepts), dtype=int)
        self.my_s = np.zeros((self.numFeatures, self.maxConcepts))
        self.my_s2 = np.zeros((self.numFeatures, self.maxConcepts))


    def calc(self, data):
        self.currentSample = sarray = np.tile(data, (self.maxConcepts, 1)).T

        self.z = np.divide(np.absolute(sarray - self.mean), self.sdev)
        #print("markers self.z", self.z)
        self.p = np.amin(self.z, axis=1)
        #print ("markers self.p", self.p)

    def learn(self):
        super().learn()
        for fname_idx in np.where(self.p >= self.threeStdQuantile)[0]:
            self.p[fname_idx] = self.threeStdQuantile
            samples = self.skippedSamples[fname_idx]
            samples.append(self.currentSample[fname_idx][0])
            c = len(samples)
            #print("skip ", fname_idx, self.p[fname_idx], c)

            if c > 100:
                print("*** Markers *** Learn MEAN and SDEV")
                key_idx = self.getKeyIdx(fname_idx)
                if (key_idx != None):
                    print("*** Markers *** Learn MEAN and SDEV - free slot", key_idx)
                    s = float(np.sum(samples))
                    s2 = float(np.sum(np.square(samples)))
                    m = s/c
                    self.my_c[fname_idx][key_idx] = c
                    self.my_s[fname_idx][key_idx] = s
                    self.my_s2[fname_idx][key_idx] = s2

                    self.c[fname_idx][key_idx] = c
                    self.mean[fname_idx][key_idx] = m
                    self.sdev[fname_idx][key_idx] = max(np.sqrt(s2/c - np.square(m)), np.finfo(np.float64).eps)
                    val = {
                        "s2": s2
                        , "s": s
                        , "c": c
                    }
                    self.storeItem(fname_idx, key_idx, val)
                    print("mean is now", self.mean)
                    print("sdev is now", self.sdev)

                print("*** Markers *** Learn MEAN and SDEV - clear")
                self.skippedSamples[fname_idx] = []



        indexs = (self.z == np.tile(self.p, (self.maxConcepts, 1)).T)
        #print("drift all ", indexs)
        s = self.currentSample[indexs]
        self.my_c[indexs] += 1
        self.my_s[indexs] += s
        self.my_s2[indexs] += np.square(s)




Modeler.modelers.append(Markers)
