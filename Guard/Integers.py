from Guard import Markers
from Guard import Modeler
import sys

class Integers(Markers.Markers):
    name = "integers"
    minSdev2 = 0.0625
    def __init__(self, spec):
        super().__init__(spec)

    def reset(self):
        super().reset()
        for g in self.g:
            g.setNoise(0.25)


Modeler.modelers.append(Integers)