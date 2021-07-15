from Guard import Fingerprints
import unittest

import numpy
import time



class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_learnSingleton(self):

        m = Fingerprints.Fingerprints({
            "fingerprints": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 10
        })
        startTime = time.time()
        for i in range(10000):
            r = m.assess({'fingerprints': ["ABC"]})
            #print(r)
            #print(m.mean)
            self.assertEqual(r[0], 0)
            m.learn()
        delta = time.time() - startTime
        self.assertLess(delta, 10)

        status = {}
        m.crdstore(status)
        m.crdload(status, 0)

        self.assertEqual(len(m.keys["test"]), 1)
        self.assertAlmostEqual(m.mean[0], 10000, delta=10)
        self.assertLess(m.std[0], 2)
        r = m.assess({'fingerprints': ["ABC"]})
        self.assertEqual(r[0], 0)
        r = m.assess({'fingerprints': ["XYZ"]})
        self.assertEqual(r[0], 100)

    def test_learnMultiKeys(self):
        m = Fingerprints.Fingerprints({
            "fingerprints": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        for i in range(1000):
            r = m.assess({'fingerprints': ["AAA"]})
            self.assertEqual(r[0], 0)
            m.learn()
            r = m.assess({'fingerprints': ["BBB"]})
            self.assertLess(r[0], 1.1)
            m.learn()
            r = m.assess({'fingerprints': ["AAA"]})
            self.assertEqual(r[0], 0)
            m.learn()
            r = m.assess({'fingerprints': ["CCC"]})
            self.assertLess(r[0], 1.1)
            m.learn()

        #print(m.mean)

        status = {}
        m.crdstore(status)
        m.crdload(status, 0)

        self.assertEqual(m.cmask[0], False)
        self.assertEqual(len(m.keys["test"]), 3)
        self.assertAlmostEqual(m.mean[0], 1500, delta=10)
        self.assertAlmostEqual(m.std[0], 500, delta=10)
        r = m.assess({'fingerprints': ["AAA"]})
        self.assertEqual(r[0], 0)
        r = m.assess({'fingerprints': ["BBB"]})
        self.assertLess(r[0], 2)
        r = m.assess({'fingerprints': ["CCC"]})
        self.assertLess(r[0], 2)
        r = m.assess({'fingerprints': ["XYZ"]})
        self.assertEqual(r[0], 100)

    def test_learnTooManyKeys(self):
        m = Fingerprints.Fingerprints({
            "fingerprints": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })

        for i in range(100):
            r = m.assess({'fingerprints': ["AAA"]})
            m.learn()
            r = m.assess({'fingerprints': ["X"+str(i)]})
            m.learn()

        self.assertEqual(m.cmask[0], True)
        self.assertEqual(len(m.keys["test"]), 0)
        r = m.assess({'fingerprints': ["AAA"]})
        self.assertEqual(r[0], 0)
        r = m.assess({'fingerprints': ["BBB"]})
        self.assertEqual(r[0], 0)

    def test_learnMultiFeatures(self):

        m = Fingerprints.Fingerprints({
            "fingerprints": ["test1", "test2", "test3"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        for i in range(1000):
            r = m.assess({'fingerprints': ["A1", "A2", "A3"]})
            self.assertEqual(r[0], 0)
            self.assertEqual(r[1], 0)
            self.assertEqual(r[2], 0)
            m.learn()
            r = m.assess({'fingerprints': ["B1", "B2", "A3"]})
            self.assertLess(r[0], 2)
            self.assertLess(r[1], 2)
            self.assertEqual(r[2], 0)
            m.learn()
            r = m.assess({'fingerprints': ["A1", "A2", "A3"]})
            self.assertEqual(r[0], 0)
            self.assertEqual(r[1], 0)
            self.assertEqual(r[2], 0)
            m.learn()
            r = m.assess({'fingerprints': ["C1", "A2", "A3"]})
            self.assertLess(r[0], 2)
            self.assertEqual(r[1], 0)
            self.assertEqual(r[2], 0)
            m.learn()

        #print(m.mean)
        self.assertEqual(len(m.keys["test1"]), 3)
        self.assertEqual(len(m.keys["test2"]), 2)
        self.assertEqual(len(m.keys["test3"]), 1)

        status = {}
        m.crdstore(status)
        m.crdload(status, 0)

        self.assertAlmostEqual(m.mean[0], 1500, delta=10)
        self.assertAlmostEqual(m.std[0], 500, delta=10)
        self.assertAlmostEqual(m.mean[1], 2500, delta=10)
        self.assertAlmostEqual(m.std[1], 866, delta=10)
        self.assertAlmostEqual(m.mean[2], 4000, delta=10)
        self.assertLess(m.std[2], 2)

        status = {}
        m.crdstore(status)
        #print(status)

    def test_store_squeeze(self):
        m = Fingerprints.Fingerprints({
            "fingerprints": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })

        status = {'fingerprints': {
            'test': {"key0": {'uid': 'A1', 'c': 2000000},
                     "key1": {'uid': 'B1', 'c': 2000}}},
            '_n': 5000000}


        # print("Loading...")
        m.crdload(status, 0)
        status = {}
        m.crdstore(status)
        print (status)

        self.assertTrue("fingerprints" in status)
        val = status["fingerprints"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        # print(keys, values)
        self.assertEqual(len(keys), 1)

        self.assertTrue("_n" in status)
        #        self.assertEqual(val["_n"], 5006000)

        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        print(val, keys, values)
        self.assertEqual(len(keys), 2)

        # previous keys
        val = values["key0"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(val["c"], 1000000)
        self.assertEqual(val["uid"], "A1")
        val = values["key1"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(val["c"], 2000)
        self.assertEqual(val["uid"], "B1")



    def test_store_load(self):
        Fingerprints.maxConcepts = 8
        m = Fingerprints.Fingerprints({
            "fingerprints": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        for i in range(100):
            r = m.assess({'fingerprints': ["A1"]})
            m.learn()
            r = m.assess({'fingerprints': ["A2"]})
            m.learn()
            r = m.assess({'fingerprints': ["A2"]})
            m.learn()
            r = m.assess({'fingerprints': ["A3"]})
            m.learn()
            r = m.assess({'fingerprints': ["A3"]})
            m.learn()
            r = m.assess({'fingerprints': ["A3"]})
            m.learn()
        status = {}
        m.crdstore(status)
        print(status)

        self.assertTrue("_n" in status)
        self.assertEqual(status["_n"], 600)

        self.assertTrue("fingerprints" in status)
        values = status["fingerprints"]
        self.assertTrue(isinstance(values, dict))


        self.assertTrue("test" in values)
        val = values["test"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 3)
        key0 = keys[0]
        val = values["test"][key0]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(100, val["c"])
        self.assertEqual("A1", val["uid"])
        key1 = keys[1]
        val = values["test"][key1]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(200, val["c"])
        self.assertEqual("A2", val["uid"])
        key2 = keys[2]
        val = values["test"][key2]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(300, val["c"])
        self.assertEqual("A3", val["uid"])


        for i in range(100):
            r = m.assess({'fingerprints': ["A1"]})
            m.learn()
            r = m.assess({'fingerprints': ["A2"]})
            m.learn()
            r = m.assess({'fingerprints': ["A2"]})
            m.learn()
            r = m.assess({'fingerprints': ["A3"]})
            m.learn()
            r = m.assess({'fingerprints': ["A3"]})
            m.learn()
            r = m.assess({'fingerprints': ["A3"]})
            m.learn()

        status = {'fingerprints': {
                    'test': {key0: {'uid': 'A1', 'c': 1000},
                             key1: {'uid': 'B1', 'c': 2000},
                             key2: {'uid': 'C1', 'c': 3000},
                             'dddddddddddddddd': {'uid': 'DD', 'c': 1000}}},
                    '_n': 5000}

        #print("Loading...")
        m.crdload(status, 0)

        status = {}
        #print("Storing...", status)
        m.crdstore(status)
        print("Storing...", status)

        self.assertTrue("fingerprints" in status)
        val = status["fingerprints"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        #print(keys, values)
        self.assertEqual(len(keys), 1)

        self.assertTrue("_n" in status)
#        self.assertEqual(val["_n"], 5006000)

        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        print(val, keys, values)
        self.assertEqual(len(keys), 4)

        # previous keys
        val = values[key0]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(val["c"], 1100)
        self.assertEqual(val["uid"], "A1")
        val = values[key1]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(val["c"], 2200)
        self.assertEqual(val["uid"], "B1")
        val = values[key2]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(val["c"], 3300)
        self.assertEqual(val["uid"], "C1")
        val = values["dddddddddddddddd"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(val["c"], 1000)
        self.assertEqual(val["uid"], "DD")

        m = Fingerprints.Fingerprints({
            "fingerprints": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 100
        })
        status = {'_n': 5000000, 'fingerprints': {
            'test': {'borke1': 11,
                     'broke2': [2, 3],
                     'broke3': {},
                     'broke4': {"c": 22},
                     'broke5': {"uid": "dd"},
                     'broke6': {"c": 22, "uid": 33},
                     'broke7': {"c": "22", "uid": "33"},
                     'broke8': {"c": [], "uid": "aa"},
                     'broke9': {"c": {33}, "uid": {}}}
            }}

        # print("Loading...")
        m.crdload(status, 0)

        status = {}
        # print("Storing...", status)
        m.crdstore(status)
        # print("Loaded...", status)

        self.assertTrue("fingerprints" in status)
        val = status["fingerprints"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        #print(keys, values)
        self.assertEqual(len(keys), 1)

        self.assertTrue("_n" in status)
        #        self.assertEqual(val["_n"], 5006000)

        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        #print(keys, values)
        self.assertEqual(len(keys), 1)

        # previous keys
        val = values['broke6']
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("uid" in val)
        self.assertEqual(val["c"], 22)
        self.assertEqual(val["uid"], "33")

        status = {'fingerprints': {
            'test': {'add1': {"c": 22, "uid": "xx"},
                     'add2': {"c": 22, "uid": "xx"},
                     'add3': {"c": 22, "uid": "xx"},
                     'add4': {"c": 22, "uid": "xx"},
                     'add5': {"c": 22, "uid": "xx"},
                     'add6': {"c": 22, "uid": "xx"},
                     'add7': {"c": 22, "uid": "xx"},
                     'add8': {"c": 22, "uid": "xx"},
                     'add9': {"c": 22, "uid": "xx"},
                     }},
            '_n': 5000000}

        # print("Loading...")
        m.crdload(status, 0)

        status = {}
        # print("Storing...", status)
        m.crdstore(status)
        # print("Loaded...", status)

        self.assertTrue("fingerprints" in status)
        val = status["fingerprints"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        #print(keys, values)
        self.assertEqual(len(keys), 1)

        self.assertTrue("_n" in status)
        #        self.assertEqual(val["_n"], 5006000)

        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        #print(keys, values)
        self.assertEqual(len(keys), 1)

        # previous keys
        #print("values", values)
        val = values['tombstone']
        self.assertTrue(isinstance(val, dict))
        self.assertEqual(len(val), 0)
