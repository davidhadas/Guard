
from Guard import Markers
import unittest

import numpy
import time


class MyTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_learnSingleton(self):
        m = Markers.Markers({
            "integers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        for i in range(200):
            r = m.assess({'integers': [5]})
            m.learn()
        for i in range(800):
            r = m.assess({'integers': [5]})
            self.assertLess(r[0], 0.25)
            m.learn()
        self.assertEqual(len(m.keys[0]), 1)
        self.assertAlmostEqual(m.mean[0][0], 5.0, delta=0.2)
        self.assertLess(m.sdev[0][0], 1.5)
        self.assertGreater(m.sdev[0][0], 0.2)

    def test_store_load(self):
        m = Markers.Markers({
            "integers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        for i in range(200):
            r = m.assess({'integers': [5]})
            m.learn()
        for i in range(800):
            r = m.assess({'integers': [5]})
            self.assertLess(r[0], 0.2)
            m.learn()
        status = {}
        m.crdstore(status)
        #print(status)


        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("test" in val)
        val = val["test"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 1)
        key = keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertAlmostEqual(1000, val["c"], delta=10)
        self.assertAlmostEqual(val["s"], 5000, delta=50)
        self.assertAlmostEqual(val["s2"], 25000, delta=2500)

