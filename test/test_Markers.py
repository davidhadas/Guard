
from Guard import Markers
import unittest

import numpy
import time


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.nsamples = numpy.random.normal(0, 1, 1000)
        self.usamples = numpy.random.uniform(0, 1, 1000)
        pass

    def test_concept_per_featrue(self):
        m = Markers.Markers({
            "markers": ["ntest", "utest", "untest"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        for i in range(1000):
            nsample = self.nsamples[i]
            usample = self.usamples[i]
            nusample = usample * 10 + nsample + 300
            nsample = nsample * 10 + 100
            usample = usample * 10 + 200
            r = m.assess({'markers': [nsample, usample, nusample]})
            #print ([nsample, usample, nusample], r)
            #self.assertAlmostEqual(r[0], 0, delta = 4)
            #self.assertAlmostEqual(r[1], 0, delta = 4)
            #self.assertAlmostEqual(r[2], 0, delta = 4)
            m.learn()

        self.assertEqual(len(m.keys["ntest"]), 1)
        self.assertTrue(len(m.keys["utest"]) > 0)
        self.assertEqual(len(m.keys["untest"]), 1)

        self.assertAlmostEqual(m.mean[0][0], 100.0, delta=20)
        self.assertAlmostEqual(m.mean[1][0], 200.0, delta=20)
        self.assertAlmostEqual(m.mean[2][0], 300.0, delta=20)
        self.assertAlmostEqual(m.sdev[0][0], 10, delta=10)
        self.assertAlmostEqual(m.sdev[1][0], 10, delta=10)
        self.assertAlmostEqual(m.sdev[2][0], 10, delta=10)


    def test_concepts(self):
        m = Markers.Markers({
            "markers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        for i in range(1000):
            nsample = self.nsamples[i]
            usample = self.usamples[i]
            nusample = usample * 10 + nsample + 100
            nsample = nsample * 10 + 10100
            usample = usample * 10 + 20100
            r = m.assess({'markers': [nsample]})
            m.learn()
            r = m.assess({'markers': [usample]})
            m.learn()
            r = m.assess({'markers': [nusample]})
            m.learn()

        self.assertTrue(len(m.keys["test"]) > 2)

        self.assertAlmostEqual(m.mean[0][0] % 10000, 100.0, delta=20)
        self.assertAlmostEqual(m.mean[0][1] % 10000, 100.0, delta=20)
        self.assertAlmostEqual(m.mean[0][2] % 10000, 100.0, delta=20)
        self.assertAlmostEqual(m.sdev[0][0], 10.0, delta=10)
        self.assertAlmostEqual(m.sdev[0][1], 10.0, delta=10)
        self.assertAlmostEqual(m.sdev[0][2], 10.0, delta=10)

    def test_features1000(self):
        markers = [str(i) for i in range(1000)]

        m = Markers.Markers({
            "markers": markers
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        startTime = time.time()
        for i in range(1000):
            nsample = self.nsamples[i]
            sample = [nsample for i in range(1000)]
            r = m.assess({'markers': sample})
            m.learn()
        delta = time.time() - startTime

        #print ("Time:", delta, " processing 1K samples of 1000 features")
        self.assertLess(delta, 24)
        for i in range(1000):
            self.assertGreaterEqual(len(m.keys[str(i)]), 1)
            self.assertAlmostEqual(m.mean[i][0], 0, delta=0.5)
            self.assertAlmostEqual(m.sdev[i][0], 1, delta=1)

    def test_features100(self):
        markers = [str(i) for i in range(100)]

        m = Markers.Markers({
            "markers": markers
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        startTime = time.time()
        for j in range(10):
            for i in range(1000):
                nsample = self.nsamples[i]
                sample = [nsample for i in range(100)]
                r = m.assess({'markers': sample})
                m.learn()
        delta = time.time() - startTime

        #print ("Time:", delta, " processing 10K samples of 100 features" )
        self.assertLess(delta, 8)
        for i in range(100):
            self.assertGreaterEqual(len(m.keys[str(i)]), 1)
            self.assertAlmostEqual(m.mean[i][0], 0, delta=0.5)
            self.assertAlmostEqual(m.sdev[i][0], 1, delta=1)

    def test_concepts100(self):
        m = Markers.Markers({
            "markers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        m.maxConcepts = 100
        m.reset()
        startTime = time.time()
        for j in range(100):
            for i in range(1000):
                nsample = self.nsamples[i] + j*100
                r = m.assess({'markers': [nsample]})
                m.learn()
        delta = time.time() - startTime

        #print ("Time:", delta, "processing 1K samples of 1 feature with 100 concepts")
        self.assertLess(delta, 20)

        self.assertEqual(100, len(m.keys["test"]))
        for i in range(100):
            self.assertAlmostEqual(round(m.mean[0][i]) % 100, 0, delta=0.5)
            self.assertAlmostEqual(round(m.sdev[0][i]) % 100, 1, delta=1)

    def test_features10(self):
        markers = [str(i) for i in range(10)]

        m = Markers.Markers({
            "markers": markers
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        startTime = time.time()
        for j in range(100):
            for i in range(1000):
                nsample = self.nsamples[i]
                sample = [nsample for i in range(10)]
                r = m.assess({'markers': sample})
                m.learn()
        delta = time.time() - startTime

        #print ("Time:", delta, " processing 100K samples of 10 features" )
        self.assertLess(delta, 20)
        for i in range(10):
            self.assertGreaterEqual(len(m.keys[str(i)]), 1)
            self.assertAlmostEqual(m.mean[i][0], 0, delta=0.5)
            self.assertAlmostEqual(m.sdev[i][0], 1, delta=1)

    def test_learn(self):
        m = Markers.Markers({
            "markers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        for i in range(200):
            r = m.assess({'markers': [5]})
            #print(i,r)
            #self.assertAlmostEqual(r[0], 0.05, delta=0.05)
            m.learn()
        for i in range(800):
            r = m.assess({'markers': [5]})
            #print(i,r)
            self.assertAlmostEqual(r[0], 0.05, delta=0.05)
            m.learn()

        r = m.assess({'markers': [2]})
        self.assertNotAlmostEqual(r[0], 1, delta=1)
        m.learn()
        r = m.assess({'markers': [5]})
        self.assertAlmostEqual(r[0], 0.05, delta=0.05)

    def test_learnSingleton(self):
        for x in [1E-10, 0.1, 0, 10, 1E10, -1E-10, -0.1, -0, -10, -1E10, ]:
            print ("test_learnSingleton", x)
            m = Markers.Markers({
                "markers": ["test"]
                , "AllowLimit": 10
                , "LearnLimit": 3
                , "collectorId": "mygate"
                , "minimumLearning": 200
            })
            for i in range(200):
                r = m.assess({'markers': [x]})
                m.learn()
            for i in range(800):
                r = m.assess({'markers': [x]})
                self.assertLess(r[0], 2)
                m.learn()

            self.assertEqual(len(m.keys["test"]), 1)
            self.assertAlmostEqual(m.mean[0][0], x, delta=abs(x*0.01))
            self.assertAlmostEqual(m.sdev[0][0], 0.0, delta=0.01)


    def test_store_squeeze(self):
        m = Markers.Markers({
            "markers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })

        status = {"_n": 777777777
            , "markers": {
                "test": {
                      "a": {"c": 2222222, "s": 666666666, "s2": 88888888888}
                    , "b": {"c": 100, "s": 100, "s2": 100}
                }}}
        # print("Loading...")
        m.crdload(status)
        status = {}
        m.crdstore(status)

        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val,dict))
        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        self.assertEqual(len(keys), 2)
        val = values['a']
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertEqual(val["c"], 1111111)
        self.assertAlmostEqual(val["s"], 333333333, places=1)
        self.assertAlmostEqual(val["s2"], 100000009800, places=1)
        val = values['b']
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertEqual(val["c"], 100)
        self.assertAlmostEqual(val["s"], 100, places=1)
        self.assertAlmostEqual(val["s2"], 100, places=1)


    def test_store_load(self):
        m = Markers.Markers({
            "markers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        for i in range(200):
            r = m.assess({'markers': [5]})
            m.learn()
        for i in range(800):
            r = m.assess({'markers': [5]})
            self.assertTrue(r[0] < 0.1)
            m.learn()
        status = {}
        m.crdstore(status)
        #print(status)

        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val,dict))
        self.assertTrue("test" in val)
        val = val["test"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 1)
        key =  keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertEqual(val["c"], 1000)
        self.assertAlmostEqual(val["s"], 5000, places=1)
        self.assertAlmostEqual(val["s2"], 25000, places=1)

        status = {"_n": 555, "markers": {   "test": {
                      key: {"c": 555, "s": 555, "s2": 555}
                    , "a": {"c": 666, "s": 6660, "s2": 666}
                    , "b": 666
                    , "c": {"s": 666, "s2": 666}
                    , "d": {"c": {},  "s": 666, "s2": 666}
                    , "e": {"c": 0,  "s": 666, "s2": 666}
                    , "f": {"c": 666, "s2": 666}
                    , "g": {"c": 666, "s": [], "s2": 666}
                    , "h": {"c": 666, "s": 666}
                    , "i": {"c": 666, "s": 666, "s2": "x"}
        }}}
        #print("Loading...")
        m.crdload(status)

        status = {}
        #print("Storing...", status)
        m.crdstore(status)
        #print("Storing...", status)

        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        print(keys, values)
        self.assertEqual(len(keys), 2)
        # previous key
        val = values[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertEqual(val["c"], 555)
        self.assertAlmostEqual(val["s"], 555, places=1)
        self.assertAlmostEqual(val["s2"], 555, places=1)

        val = values["a"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertEqual(val["c"], 666)
        self.assertAlmostEqual(val["s"], 6660, places=1)
        self.assertAlmostEqual(val["s2"], 66600, places=1)

    def test_merge(self):
        m = Markers.Markers({
            "markers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        status = {}
        m.crdstore(status)
        #print("status", status)

        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        #print(keys, values)
        self.assertEqual(len(keys), 0)
        #print ("-----")
        status = {"_n": 555, "markers": {"test": {
              "x": {"c": 100, "s": 100, "s2": 100}
            , "a": {"c": 100, "s": 200, "s2": 1000}
            , "b": 666
            , "c": {"s": 666, "s2": 666}
            , "d": {"c": {}, "s": 666, "s2": 666}
            , "e": {"c": 0, "s": 666, "s2": 666}
            , "f": {"c": 666, "s2": 666}
            , "g": {"c": 666, "s": [], "s2": 666}
            , "h": {"c": 666, "s": 666}
            , "i": {"c": 666, "s": 666, "s2": "x"}
        }}}
        #print("Loading...")
        m.crdload(status)

        status = {}
        m.crdstore(status)
        #print("Storing...", status)

        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        #print(keys, values)
        self.assertEqual(len(keys), 1)
        self.assertTrue("x" in keys)
        # previous key
        val = values["x"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertEqual(val["c"], 200)
        self.assertAlmostEqual(val["s"], 300, places=1)
        self.assertAlmostEqual(val["s2"], 1100, places=1)

    def test_load_tombstone(self):
        m = Markers.Markers({
            "markers": ["test"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })
        for i in range(200):
            r = m.assess({'markers': [5]})
            m.learn()
        for i in range(800):
            r = m.assess({'markers': [5]})
            self.assertTrue(r[0] < 0.1)
            m.learn()
        status = {}
        m.crdstore(status)
        #print(status)


        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val,dict))
        self.assertTrue("test" in val)
        val = val["test"]
        self.assertTrue(isinstance(val, dict))
        keys = list(val.keys())
        self.assertEqual(len(keys), 1)
        key =  keys[0]
        val = val[key]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("c" in val)
        self.assertTrue("s" in val)
        self.assertTrue("s2" in val)
        self.assertEqual(val["c"], 1000)
        self.assertAlmostEqual(val["s"], 5000, places=1)
        self.assertAlmostEqual(val["s2"], 25000, places=1)

        status = {"_n": 555, "markers": {  "test": {
                      key: {"c": 555, "s": 555, "s2": 555}
                    , "tombstone": {}
                    , "a": {"c": 666, "s": 6660, "s2": 666}
                    , "b": 666
                    , "c": {"s": 666, "s2": 666}
                    , "d": {"c": {},  "s": 666, "s2": 666}
                    , "e": {"c": 0,  "s": 666, "s2": 666}
                    , "f": {"c": 666, "s2": 666}
                    , "g": {"c": 666, "s": [], "s2": 666}
                    , "h": {"c": 666, "s": 666}
                    , "i": {"c": 666, "s": 666, "s2": "x"}
        }}}
        #print("Loading...")
        m.crdload(status)

        status = {}
        #print("Storing...", status)
        m.crdstore(status)
        #print("Storing...", status)

        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("test" in val)
        values = val["test"]
        self.assertTrue(isinstance(values, dict))
        keys = list(values.keys())
        #print("**", keys, values)
        self.assertEqual(1, len(keys))
        self.assertTrue("tombstone" in keys)
        # previous key
        val = values["tombstone"]
        self.assertDictEqual(val, {})

    def test_load_manyconcepts(self):
        m = Markers.Markers({
            "markers": ["test2", "test3"]
            , "AllowLimit": 10
            , "LearnLimit": 3
            , "collectorId": "mygate"
            , "minimumLearning": 200
        })

        m.maxConcepts = 2

        status = {"_n": 555
            , "markers": {
                 "test3": {
                      "a": {"c": 666, "s": 6660, "s2": 66}
                    , "c": {"c": 666, "s": 666, "s2": 66}
                    , "d": {"c": 666,  "s": -6660, "s2": 66}
                }, "test2": {
                      "a": {"c": 666, "s": 6660, "s2": 66}
                    , "c": {"c": 666, "s": 666, "s2": 66}
        }}}
        #print("Loading...")
        m.crdload(status)

        status = {}
        m.crdstore(status)
        #print("Storing...", status)


        self.assertTrue("markers" in status)
        val = status["markers"]
        self.assertTrue(isinstance(val, dict))
        self.assertTrue("test2" in val)
        self.assertTrue("test3" in val)

        values = val["test2"]
        keys = list(values.keys())
        #print("**", keys, values)
        self.assertEqual(2, len(keys))
        self.assertFalse("tombstone" in keys)

        values = val["test3"]
        keys = list(values.keys())
        #print("**", keys, values)
        self.assertTrue("tombstone" in keys)

#t = unittest.TestLoader().loadTestsFromTestCase(MyTestCase)
#unittest.TextTestRunner(verbosity=2).run(t)
if __name__ == "__main":
    unittest.main()