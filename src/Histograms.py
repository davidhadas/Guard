import Markers
import Modeler
import sys

class Histograms(Markers.Markers):
    name = "histograms"
    histLen = 8

    def expandFeatures(self, featureNames):
        fn = []
        for name in featureNames:
            for i in range(self.histLen):
                fn.append(name+"-"+str(i)+str((i+1)%self.histLen))
        return fn

    def expandData(self, data):
        d = []
        for hist in data:
            hist = hist[:self.histLen] + [0]*(self.histLen - len(hist))
            #print("expendData handling ", hist)

            for idx, val in enumerate(hist):

                val += sys.float_info.epsilon
                d.append(val/(sys.float_info.epsilon + hist[(idx+1)%self.histLen]))
                #print("While expendData", len(d), idx, val)
        #print("After expendData",len(d))
        return d

Modeler.modelers.append(Histograms)
