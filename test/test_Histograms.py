

from Guard import Histograms
import unittest

import numpy
import time



class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_learnSingleton(self):
        m = Histograms.Histograms({
            "histograms": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        for i in range(1000):
            r = m.assess({'histograms': [[4, 4, 0, 1E10-1, 0, 0]]})
            #print(r)
            #print(m.mean)
            self.assertLess(r[0], 0.25)
            m.learn()
        return
        #print(m.keys)
        self.assertEqual(len(m.keys["test-01"]), 1)
        self.assertAlmostEqual(m.mean[0][0], 1.0, delta=0.05)
        self.assertLess(m.sdev[0][0], 0.2)


    def test_store_load(self):
        m = Histograms.Histograms({
            "histograms": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        for i in range(1000):
            r = m.assess({'histograms': [[4, 4, 0, 1E10-1, 0, 0]]})
            #print (r)
            self.assertLess(r[0], 0.25)
            m.learn()
        status = {}
        m.crdstore(status)
        #print(status)
        return
        self.assertTrue("histograms" in status)
        values = status["histograms"]
        self.assertTrue(isinstance(values, dict))
        self.assertTrue("_n" in values)
        self.assertEqual(values["_n"], 1000)

        self.assertTrue("test-01" in values)
        val = values["test-01"]
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
        self.assertAlmostEqual(1000, val["s"], delta=10)
        self.assertAlmostEqual(1000, val["s2"], delta=10)

        self.assertTrue("test-12" in values)
        val = values["test-12"]
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
        self.assertAlmostEqual(5000, val["s"], delta=10)
        self.assertAlmostEqual(25000, val["s2"], delta=100)


        self.assertTrue("test-23" in values)
        val = values["test-23"]
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
        self.assertAlmostEqual(1E-7, val["s"] , delta=1E-7)
        self.assertAlmostEqual(1E-10, val["s2"], delta=1E-6)


        self.assertTrue("test-34" in values)
        val = values["test-34"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertGreaterEqual(len(keys), 1)
        key = keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertAlmostEqual(1000, val["c"], delta=10)
        self.assertAlmostEqual(1000000, val["s"] , delta=100)
        self.assertAlmostEqual(10000000, val["s2"], delta=1000)


        self.assertTrue("test-45" in values)
        val = values["test-45"]
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
        self.assertAlmostEqual(10, val["s"] , delta=1)
        self.assertAlmostEqual(0.1, val["s2"], delta=0.01)
