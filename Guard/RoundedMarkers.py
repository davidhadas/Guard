import numpy as np
#from scipy.stats import norm
from Guard import Modeler
from Guard import Markers


class RoundedMarkers(Markers.Markers):
    name = "roundedMarkers"
    def __init__(self, spec):
        super().__init__(spec)

    def reset(self):
        super().reset()
        pass

    def load(self, status):
        mystatus = super().load(status)


    def store(self, response):
        status = []

        super().crdstore(response, status)


    def calc(self, data):
        self.p = np.zeros(self.numFeatures)

    def learn(self):
        pass



Modeler.modelers.append(RoundedMarkers)
