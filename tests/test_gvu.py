import sys
sys.path.append('../src/')
print(sys.path)

import gvu
import unittest

import numpy
import time


class MyTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_pos(self):
        m = gvu.gvu()
        for i in range(100):
            m.addPoint(5)
        print(len(m.points))
        result = m.getGuassian()
        print("result", result)
        mu = result["driftedGuassian"]["mu"]
        sdev = result["driftedGuassian"]["sdev"]
        c = result["driftedGuassian"]["c"]
        self.assertAlmostEqual(100,c, delta=10)
        self.assertAlmostEqual(5, mu, delta=0.5)
        self.assertAlmostEqual(1E-10, sdev,  delta=1E-5)

    def test_neg(self):
        m = gvu.gvu()
        for i in range(100):
            m.addPoint(-5)
        print(len(m.points))
        result = m.getGuassian()
        print("result", result)
        mu = result["driftedGuassian"]["mu"]
        sdev = result["driftedGuassian"]["sdev"]
        c = result["driftedGuassian"]["c"]
        self.assertAlmostEqual(100,c, delta=10)
        self.assertAlmostEqual(-5, mu)
        self.assertAlmostEqual(1E-10, sdev,  delta=1E-5)

    def test_small_pos(self):
        m = gvu.gvu()
        for i in range(100):
            m.addPoint(5E-10)
        print(len(m.points))
        result = m.getGuassian()
        print("result", result)
        mu = result["driftedGuassian"]["mu"]
        sdev = result["driftedGuassian"]["sdev"]
        c = result["driftedGuassian"]["c"]
        self.assertAlmostEqual(100,c, delta=10)
        self.assertAlmostEqual(5E-10, mu, delta=5E-10)
        self.assertAlmostEqual(1E-10, sdev, delta=1E-5)

    def test_small_neg(self):
        m = gvu.gvu()
        for i in range(100):
            m.addPoint(-5E-10)
        print(len(m.points))
        result = m.getGuassian()
        print("result", result)
        mu = result["driftedGuassian"]["mu"]
        sdev = result["driftedGuassian"]["sdev"]
        c = result["driftedGuassian"]["c"]
        self.assertAlmostEqual(100,c, delta=10)
        self.assertAlmostEqual(-5E-10, mu, delta=5E-10)
        self.assertAlmostEqual(1E-10, sdev, delta=1E-5)

    def test_large_pos(self):
        m = gvu.gvu()
        for i in range(100):
            m.addPoint(5E+11)
        print(len(m.points))
        result = m.getGuassian()
        print("result", result)
        mu = result["driftedGuassian"]["mu"]
        sdev = result["driftedGuassian"]["sdev"]
        c = result["driftedGuassian"]["c"]
        self.assertAlmostEqual(100,c, delta=10)
        self.assertAlmostEqual(5E+11, mu, delta=5E+9)
        self.assertAlmostEqual(1E+1, sdev, delta=1E+6)

    def test_large_neg(self):
        m = gvu.gvu()
        for i in range(100):
            m.addPoint(-5E+11)
        print(len(m.points))
        result = m.getGuassian()
        print("result", result)
        mu = result["driftedGuassian"]["mu"]
        sdev = result["driftedGuassian"]["sdev"]
        c = result["driftedGuassian"]["c"]
        self.assertAlmostEqual(100,c, delta=10)
        self.assertAlmostEqual(-5E+11, mu, delta=5E+9)
        self.assertAlmostEqual(1E+1, sdev, delta=1E+6)

    def test_zero(self):
        m = gvu.gvu()
        for i in range(100):
            m.addPoint(0)
        print(len(m.points))
        result = m.getGuassian()
        print("result", result)
        mu = result["driftedGuassian"]["mu"]
        sdev = result["driftedGuassian"]["sdev"]
        c = result["driftedGuassian"]["c"]
        self.assertAlmostEqual(100,c, delta=10)
        self.assertAlmostEqual(0, mu, delta=1E-9)
        self.assertAlmostEqual(1E-10, sdev, delta=1E-9)
