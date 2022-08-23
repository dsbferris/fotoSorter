from unittest import TestCase

from GpsClass import GpsClass


class TestGpsClass(TestCase):

    # TODO Create more test cases.
    # Like some with negative values in dd. Or another denominator.
    def test_some_coords1(self):
        sample_lat = ((43, 1), (24, 1), (66780, 10000))
        sample_lon = ((10, 1), (51, 1), (342756, 10000))
        sample_alt = (191248, 1000)

        sample_dd_lat = 43.4018546
        sample_dd_lon = 10.8595210
        sample_dd_alt = 191.248

        self.assertAlmostEqual(GpsClass.rela3_to_dd(sample_lat), sample_dd_lat, 6)
        self.assertAlmostEqual(GpsClass.rela3_to_dd(sample_lon), sample_dd_lon, 6)
        self.assertAlmostEqual(GpsClass.rela_to_dd(sample_alt), sample_dd_alt, 6)

        rela3 = GpsClass.dd_to_rela3(sample_dd_lat)
        self.assertEqual(rela3[0], sample_lat[0])
        self.assertEqual(rela3[1], sample_lat[1])
        seconds_denominator_factor_diff = rela3[2][1] / sample_lat[2][1]
        self.assertAlmostEqual(rela3[2][0], sample_lat[2][0] * seconds_denominator_factor_diff, delta=1)

        rela3 = GpsClass.dd_to_rela3(sample_dd_lon)
        self.assertEqual(rela3[0], sample_lon[0])
        self.assertEqual(rela3[1], sample_lon[1])
        self.assertAlmostEqual(rela3[2][0] / rela3[2][1], sample_lon[2][0] / sample_lon[2][1], delta=1)

        rela = GpsClass.dd_to_rela(sample_dd_alt)
        self.assertEqual(rela[0] * rela[1], sample_alt[0] * sample_alt[1])

    def test_init_and_equal(self):
        geoData = {
            "latitude": 43.4464783,
            "longitude": 10.7275112,
            "altitude": 191.248,
            "latitudeSpan": 0.0,
            "longitudeSpan": 0.0
        }
        GPS = {
            0: (2, 3, 0, 0),
            1: b'N',
            2: ((43, 1), (26, 1), (473220, 10000)),
            3: b'E',
            4: ((10, 1), (43, 1), (390402, 10000)),
            5: 0, 6: (191248, 1000)}
        gpsclass1 = GpsClass(geoData)
        gpsclass2 = GpsClass(GPS)
        self.assertEqual(gpsclass1, gpsclass2)
