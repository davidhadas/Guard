

from Guard import gvu2
import unittest

import numpy
import time
import random


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.usamples = numpy.random.uniform(0, 0.9, 100)
        pass

    def test_pos(self):
        m = gvu2.gvu2()
        m.addPoint([9 , 2 ])
        for i in range(99):
            m.addPoint([9+self.usamples[i],2+self.usamples[i]])
            m.addPoint([2 + self.usamples[i], 9 + self.usamples[i]])
        #print(len(m.points))
        points1, points2 = m.getGuassian()
        self.assertEqual(100, len(points1))
        self.assertEqual(100, len(points2))

        for i in range(100):
            self.assertAlmostEqual(9.5, points1[i], delta=0.6)
            self.assertAlmostEqual(2.5, points2[i], delta= 0.6)

    def test_singleton(self):
        m = gvu2.gvu2()
        m.addPoint([9 , 2 ])
        for i in range(99):
            m.addPoint([9,2])
            m.addPoint([2, 9])
        #print(len(m.points))
        points1, points2 = m.getGuassian()
        self.assertEqual(100, len(points1))
        self.assertEqual(100, len(points2))


        for i in range(100):
            self.assertAlmostEqual(9, points1[i], delta=0.1)
            self.assertAlmostEqual(2, points2[i], delta= 0.1)
