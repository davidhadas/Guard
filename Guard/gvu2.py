import numpy as np
import math
import random

class gvu2():
    candidates = 20
    maxAccuracy = 1E-5
    noise = 1E-5

    def __init__(self):
        self.min0 = np.finfo(np.float64).max
        self.max0 = np.finfo(np.float64).min
        self.min1 = np.finfo(np.float64).max
        self.max1 = np.finfo(np.float64).min
        self.points0 = []
        self.points1 = []

    def clear(self):
        self.min0 = np.finfo(np.float64).max
        self.max0 = np.finfo(np.float64).min
        self.min1 = np.finfo(np.float64).max
        self.max1 = np.finfo(np.float64).min
        self.points0 = []
        self.points1 = []


    def setNoise(self, noise):
        self.noise = noise

    def addPoint(self, point):
        point = list(point)
        #print(point)
        point[0] += 1E-10
        point[1] += 1E-10

        #point[0] *= random.gauss(1, self.noise)
        #point[1] *= random.gauss(1, self.noise)

        self.points0.append(point[0])
        self.points1.append(point[1])
        if (point[0]>self.max0):
            self.max0 = point[0]
        if (point[0] < self.min0):
            self.min0 = point[0]
        if (point[1] > self.max1):
            self.max1 = point[1]
        if (point[1] < self.min1):
            self.min1 = point[1]
        return len(self.points0)

    def getGuassian(self):
        if (len(self.points0)<30):
            return None
        return self._findGuassian()



    def _filterCurrentPoints(self, mu, sdev):
        # Find which points this Guassian does not explain
        minimalP = mu-3*sdev
        maximalP = mu+3*sdev
        self.points = [p for p in self.points if p < minimalP or p > maximalP]

    def _train(self, points0, points1):

        lr = 0.001
        ib = random.random()
        i0w = random.random()
        i1w = random.random()
        hb0 = random.random()
        hw0 = random.random()
        hb1 = random.random()
        hw1 = random.random()

        perror = 0.1
        for j in range(50):
            error = hd_all = out0d_all = out1d_all = 0

            for i in range(len(points0)):
                in0 = points0[i]
                in1 = points1[i]
                h = ib + i0w * in0 + i1w * in1
                if h<0:
                    h *= 0.01
                out0 = hb0 + hw0 * h
                if out0 < 0:
                    out0 *= 0.01
                out1 = hb1 + hw1 * h
                if out1 < 0:
                    out1 *= 0.01


                out0d = in0 - out0
                out1d = in1 - out1
                error +=  out0d**2 + out1d**2

                if (abs(out0d) > 1E10):
                    out0d = 1E10
                if (out0<0):
                    out0d *= 0.01
                out0d_all += out0d

                if (abs(out1d) > 1E10):
                    out1d = 1E10
                if (out1 < 0):
                    out1d *= 0.01
                out1d_all += out1d

                hd = hw0 * out0d + hw1 * out1d
                if (abs(hd) > 1E10):
                    hd = 1E10
                if (hd < 0):
                    hd *= 0.01
                hd_all += hd

            ib  += lr * hd_all
            i0w += lr * hd_all * in0
            i1w += lr * hd_all * in1
            hb0 += lr * out0d_all
            hw0 += lr * out0d_all * h
            hb1 += lr * out1d_all
            hw1 += lr * out1d_all * h
            print("train error", error, perror - error, (perror - error)/perror)
            derror =  perror - error
            if j>10 and derror>0 and derror/perror<0.01:
                break
            perror = error
        return ib, i0w, i1w, hb0, hw0, hb1, hw1

    def _findGuassian(self):
        # The model looks to find a Guassian that explains the data in contrast to an "alternative source"
        # A uniform distribution is used as the "alternative source"
        # Here, EM finds a maximum likelihood combination of a Guassian and a Uniform disributions that fits the data
        # The implementation evaluates a single candidate Guassian and choose the best one at the end

        # Normalize data to the range 0 and 1
        print ("gvu2 max0", self.max0, "min0",self.min0, "max1", self.max1, "min1",self.min1)
        delta0 = max(self.max0 - self.min0, self.noise)
        delta1 = max(self.max1 - self.min1, self.noise)
        delta_min0 = self.min0  # - delta
        delta_min1 = self.min1  # - delta
        points0 = (np.array(self.points0).astype(np.double) - delta_min0) / delta0
        points1 = (np.array(self.points1).astype(np.double) - delta_min1) / delta1
        numPoints = len(points0)



        # Add noise to points to avoid later numerical problems
        # As we add noise we normalize data only roughly to the range 0 and 1
        points0 += np.random.normal(0, self.maxAccuracy, numPoints)
        points1 += np.random.normal(0, self.maxAccuracy, numPoints)
        # print("points", points)
        # Array of points broadcasted to all candidates
        x0 = np.tile(points0, (self.candidates, 1))
        x1 = np.tile(points1, (self.candidates, 1))

        # EM initialization step - initialize a set of candidate Guassians
        # Choose randomly from our points potential Guassian centers and give them some initial variance
        initial_points = np.random.randint(len(points0)-1, size=self.candidates)
        mu0 = points0[initial_points].reshape(self.candidates, 1)
        mu1 = points1[initial_points].reshape(self.candidates, 1)
        variance0 = np.random.uniform(0.001, 0.05, size=self.candidates).reshape(self.candidates, 1)
        variance1 = np.random.uniform(0.001, 0.05, size=self.candidates).reshape(self.candidates, 1)

        # Choose an initial probability of a point to come from the Guassian (Uniform is therefore 1-pGaus)
        pGaus = np.array([0.5]).astype(np.double)

        # The probability of getting a point given a Uniform disribution from 0 to 1
        pxGivenAlt = 1

        #print("mu", mu, "\variance", variance, "\pGaus", pGaus)
        #print("Finding Guassian in a range of", delta, "with ", numPoints, "points")

        for i in range(100):
            # E_Step estimates w - the probability of each point to belong to each candidate Guassian
            # If it does not belong to a candidate Guassian, we assume it belongs to an "alternative source"
            # We use a uniform distribution as our "alternative source"

            pxGivenG = (1/(np.pi*variance0*variance1))*np.exp(-np.square(x0 - mu0)/(2*variance0)-np.square(x1 - mu1)/(2*variance1))
            if (np.any(np.isnan(pxGivenG))):
                mask = np.isnan(pxGivenG)
                print("Nan on pxGivenG")
                print("x0 - mu0",x0[mask] - mu0[mask])
                print("variance0", variance0[mask])
                print("x1 - mu1", x1[mask] - mu0[mask])
                print("variance1", variance1[mask])
                print("np.pi*variance0*variance1", np.pi*variance0[mask]*variance1[mask])
                break

            # calculate w - the probability of each of the points to come from the gaussian
            wtmp = pxGivenG*pGaus

            w = wtmp/(wtmp+pxGivenAlt*(1-pGaus))

            # M_Step maximizes the Likelihood of our model by adjusting the Guassian parameters to fit the data
            # Based on w of each point indicating the probability of this point to belong to the Guassian

            # Update the probability of a point to come from the Guassian (Uniform is therefore 1-pGaus)
            sumw = np.sum(w, axis=1).reshape((self.candidates, 1))

            pGaus = sumw / numPoints
            #print("sumw", sumw)

            # Update the center of the Guassian
            mu0 = np.sum(w * x0, axis=1).reshape((self.candidates, 1)) / sumw


            mu1 = np.sum(w * x1, axis=1).reshape((self.candidates, 1)) / sumw

            # Update the variance of the Guassian
            variance0 = (np.sum(w * np.square(x0 - mu0), axis=1).reshape((self.candidates, 1)) / sumw) + np.finfo(
                np.float64).eps
            variance1 = (np.sum(w * np.square(x1 - mu1), axis=1).reshape((self.candidates, 1)) / sumw) + np.finfo(
                np.float64).eps

        #print("mu0",mu0, "\nmu1",mu1, "\nsdev0",np.sqrt(variance0), "\nsdev1",np.sqrt(variance1), "\npGaus",pGaus)
        #print("***** pxGivenAlt is", pxGivenAlt)
        sdev0 = np.sqrt(variance0)
        sdev1 = np.sqrt(variance1)

        #maximal = np.argmax(pGaus/sdev)
        maximal = np.argmax(pGaus)
        #print ("pGaus",pGaus, "\nsdev", sdev)
        w = w[maximal]
        gmu0 = mu0[maximal] * delta0 + delta_min0
        gmu1 = mu1[maximal] * delta1 + delta_min1

        gsdev0 = sdev0[maximal]*delta0
        gsdev1 = sdev1[maximal]*delta1

        gexplains = pGaus[maximal]

        #self.gc = self._evaluatePoints(self.gmu0, self.gmu1, self.gsdev0, self.gsdev1)
        print("Best Gaussian", gmu0, gmu1, "STD", gsdev0, gsdev1, "explains", gexplains, "of points")
        where = w > 0.5

        #print (where.shape, points0.shape)
        #self._train(points0, points1)
        #print("---")

        points0 = points0[where] * delta0 + delta_min0
        points1 = points1[where] * delta1 + delta_min1

        # check covariance - if low co-variance, no need for auto-encoder
        corrcoef = np.corrcoef(points0, points1)
        print("corrcoef", corrcoef)

        return points0, points1 #, self._train(points0, points1)
        #self._adjustGuassian()


import random

#import autoencoder
'''
g = gvu2()
for i in range(0):
    g.addPoint((random.gauss(100, 10), 5))
for i in range(0):
    g.addPoint((random.gauss(300, 2), 60))
for i in range(0):
    g.addPoint((random.gauss(300, 1), 40))

points0, points1 = g._findGuassian()
print("len(points0)",len(points0), points0, points1)
'''

#a = autoencoder.autoencoder(2,1)
#a.set(ib, i0w, i1w, hb0, hw0, hb1, hw1)
#print(g.getGuassian())
#print(g.getGuassian())
#print (a.network_error)
#print("data  ", a.forward_propagate((random.gauss(100, 10), 5))/a.network_error )
#print("nodata", a.forward_propagate((random.gauss(300, 10), 60))/a.network_error )

#b = autoencoder.autoencoder(2,1)
'''



for j in range(1):
    for i in range(len(points0)):
        row = [points0[i], points1[i]]
#        error = b.forward_propagate(row + [None])
#        b.backward_propagate_error(row)
#        b.update_weights(row)
'''

#print (b.network_error)
#print("b data  ", b.forward_propagate((random.gauss(100, 10), 5))/b.network_error )
#print("b nodata", b.forward_propagate((random.gauss(300, 10), 60))/b.network_error )