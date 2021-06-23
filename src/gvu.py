import numpy as np
import math
import random

class gvu():
    candidates = 20
    maxAccuracy = 1E-10
    noise = 1E-10

    def __init__(self):
        self.min = np.finfo(np.float64).max
        self.max = np.finfo(np.float64).min
        self.points = []

    def clear(self):
        self.min = np.finfo(np.float64).max
        self.max = np.finfo(np.float64).min
        self.points = []

    def setNoise(self, noise):
        self.noise = noise

    def addPoint(self, point):
        #point += random.uniform(0, self.noise)
        #point *= random.gauss(1, self.noise)

        self.points.append(point)
        if (point>self.max):
            self.max = point
        if (point < self.min):
            self.min = point
        return len(self.points)

    def getGuassian(self):
        if (len(self.points)<30):
            return {}
        self._findGuassian()
        #print ("finished")
        result = {
                    "guassian":{
                          "mu":self.gmu
                        , "sdev": self.gsdev
                        , "c":  self.gc
                        , "explains": self.gexplains
                    } , "driftedGuassian": {
                          "mu": self.dgmu
                        , "sdev": self.dgsdev
                        , "c": self.dgc
                        , "explains": self.gexplains * self.dgc/self.gc
                    }
                }
        #print(result)
        return result

    def _adjustGuassian(self):
        mu = self.gmu
        sdev = self.gsdev

        # calculate guassian based on non weighted points
        c = 0
        s = 0
        s2 = 0
        minpoint = self.max
        maxpoint = self.min
        points = self.points
        # loop over (remaining) points and calculate the guassian
        flag = True
        while flag:
            remainingpoints = []
            flag = False
            for p in points:
                z = np.divide(np.absolute(p - mu), sdev)
                #print (p, mu, sdev, z)
                if (z <= 3):
                    flag = True
                    c += 1
                    s += p
                    s2 += p ** 2
                    if (minpoint > p):
                        minpoint = p
                    if (maxpoint < p):
                        maxpoint = p
                else:
                    remainingpoints.append(p)
            if not flag:
                break

            mu = s / c
            #print("c, s2, s, mu, s * mu", c, s2, s, mu, s * mu, "s2 - s*mu", (s2 - s * mu))

            sdev = math.sqrt(max(self.noise*self.noise,(s2 - s*mu)/c))
            print ("Drifted Gaussian process c,mu,sdev", c, mu, sdev)
            #print("max-min", maxpoint - minpoint, "6sdev", 6 * sdev, "factor", (maxpoint - minpoint) * 1.1 / (6 * sdev))
            points = remainingpoints

        self.dgmu = mu
        self.dgsdev = sdev
        self.dgc = c #self._evaluatePoints(mu, sdev)
        self._filterCurrentPoints(mu, sdev)
        print("Drifted Gaussian", self.dgmu, "STD", self.dgsdev)


    def _filterCurrentPoints(self, mu, sdev):
        # Find which points this Guassian does not explain
        minimalP = mu-3*sdev
        maximalP = mu+3*sdev
        self.points = [p for p in self.points if p < minimalP or p > maximalP]

    def _evaluatePoints(self, mu, sdev):
        minimalP = mu - 3 * sdev
        maximalP = mu + 3 * sdev
        c = 0
        for p in self.points:
            if p >= minimalP and p <= maximalP:
                c += 1
        return c

    def _findGuassian(self):
        # The model looks to find a Guassian that explains the data in contrast to an "alternative source"
        # A uniform distribution is used as the "alternative source"
        # Here, EM finds a maximum likelihood combination of a Guassian and a Uniform disributions that fits the data
        # The implementation evaluates a set of candidate Guassians and choose the best one at the end

        # Normalize data to the range 0 and 1
        delta = max(self.max - self.min, self.noise)
        delta_min = self.min  #- delta
        points = (np.array(self.points).astype(np.double) - delta_min)/delta
        numPoints = len(points)

        # Add noise to points to avoid later numerical problems
        # As we add noise we normalize data only roughly to the range 0 and 1
        points += np.random.normal(0, self.maxAccuracy, numPoints)
        #print("points", points)
        # Array of points broadcasted to all candidates
        x = np.tile(points, (self.candidates,1))

        # EM initialization step - initialize a set of candidate Guassians
        # Choose randomly from our points potential Guassian centers and give them some initial variance
        mu = np.random.choice(points, size=self.candidates, replace=False).reshape(self.candidates,1)
        variance = np.random.uniform(0.001,0.5, size=self.candidates).reshape(self.candidates,1)

        # Choose an initial probability of a point to come from the Guassian (Uniform is therefore 1-pGaus)
        pGaus = np.tile(0.5, (1, self.candidates)).T.astype(np.double)

        # The probability of getting a point given a Uniform disribution from 0 to 1
        pxGivenAlt = 1

        #print("mu", mu, "\variance", variance, "\pGaus", pGaus)
        #print("Finding Guassian in a range of", delta, "with ", numPoints, "points")

        for i in range(100):
            # E_Step estimates w - the probability of each point to belong to each candidate Guassian
            # If it does not belong to a candidate Guassian, we assume it belongs to an "alternative source"
            # We use a uniform distribution as our "alternative source"

            pxGivenG = (1/np.sqrt(2*np.pi*variance))*np.exp(-np.square(x - mu)/(2*variance))
            if (np.any(np.isnan(pxGivenG))):
                mask = np.isnan(pxGivenG)

                print("Nan on pxGivenG")
                print("delta_min",delta_min)
                print("delta", delta)
                print("variance", variance)
                print("self.points", self.points)
                print("x", x)
                print("mu", mu)

                print("np.exp(-np.square(x - mu)/(2*variance))", np.exp(-np.square(x - mu)/(2*variance))[mask])
                break

            wtmp = pxGivenG*pGaus
            w = wtmp/(wtmp+pxGivenAlt*(1-pGaus))

            # M_Step maximizes the Likelihood of our model by adjusting the Guassian parameters to fit the data
            # Based on w of each point indicating the probability of this point to belong to the Guassian

            # Update the probability of a point to come from the Guassian (Uniform is therefore 1-pGaus)
            sumw = np.sum(w, axis=1).reshape((self.candidates,1))
            pGaus = sumw / numPoints
            #print("sumw", sumw)

            # Update the center of the Guassian
            mu = np.sum(w * x, axis=1).reshape((self.candidates,1)) / sumw

            # Update the variance of the Guassian
            variance = (np.sum(w * np.square(x-mu), axis=1).reshape((self.candidates,1))/sumw)+np.finfo(np.float64).eps

        # Now find the best candidate from all Guassian candidates
        #print("mu",mu, "\nsdev",np.sqrt(variance), "\npGaus",pGaus)
        #print("***** pxGivenAlt is", pxGivenAlt)
        sdev = np.sqrt(variance)
        #maximal = np.argmax(pGaus/sdev)
        maximal = np.argmax(pGaus)
        #print ("pGaus",pGaus, "\nsdev", sdev)
        self.gmu = mu[maximal][0]*delta + delta_min
        self.gsdev = sdev[maximal][0]*delta
        self.gexplains = pGaus[maximal][0]
        self.gc = self._evaluatePoints(self.gmu, self.gsdev)
        #print("Best Gaussian", self.gmu, "STD", self.gsdev, "explains", self.gexplains, "of points")

        self._adjustGuassian()


#import random
#g = gvu()

##for i in range(400):
#    g.addPoint(random.gauss(1E20, 1E19))
#for i in range(200):
#    g.addPoint(random.gauss(2E20, 1E19))
#for i in range(0):
#    g.addPoint(random.gauss(-1000, 1))

#print(g.getGuassian())
#print(g.getGuassian())


