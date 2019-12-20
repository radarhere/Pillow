import unittest

from PIL import Image

from .helper import PillowTestCase, hopper

try:
    import numpy
except ImportError:
    numpy = None


TEST_IMAGE_SIZE = (10, 10)


@unittest.skipIf(numpy is None, "Numpy is not installed")
class TestNumpy(PillowTestCase):
    def test_numpy_to_image(self):
        im = Image.open("Tests/images/SFP236719122017220.tif")
        nd = numpy.array(im)
        a = str(nd)
        b = str(numpy.array(im))
        self.assertTrue(a == b)

        im = Image.open("Tests/images/SFP236719122017220.tif")
        numpy.array(im)
        nd = numpy.array(im)
        a = str(nd)
        b = str(numpy.array(im))
        self.assertTrue(a == b)

        im = Image.open("Tests/images/SFP236719122017220.tif")
        nd1 = numpy.array(im)
        nd2 = numpy.array(im)
        a = str(nd2)
        b = str(numpy.array(nd1))
        self.assertTrue(a == b)

        im = Image.open("Tests/images/SFP236719122017220.tif")
        nd = numpy.asarray(im)
        a = str(nd)
        b = str(numpy.asarray(im))
        self.assertTrue(a == b)

        im = Image.open("Tests/images/SFP236719122017220.tif")
        numpy.asarray(im)
        nd = numpy.asarray(im)
        a = str(nd)
        b = str(numpy.asarray(im))
        self.assertTrue(a == b)
