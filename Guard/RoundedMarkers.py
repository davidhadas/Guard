import numpy as np
#from scipy.stats import norm
from Guard import Modeler
from Guard import Markers


class RoundedMarkers(Markers.Markers):
    name = "roundedMarkers"
    def __init__(self, spec):
        super().__init__(spec)

Modeler.modelers.append(RoundedMarkers)
