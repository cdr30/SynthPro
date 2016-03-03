"""
Unit tests for functions in tools module.

"""
import unittest
import numpy as np
import matplotlib.pyplot as plt
import sys

import tools

class TestMapCores(unittest.TestCase):
    """ Unit tests for <tools.mapcores> """

    def test_mapcores_complete(self):
        """ Ensures that all regions of model data are correctly indexed
        following mapping to different cores """
        nj, ni = 1000, 2000
        nycores, nxcores = 7, 3
        ncores = nxcores * nycores
        dat = np.zeros(nj * ni).reshape(nj, ni)
        imins, imaxs, jmins, jmaxs = tools.mapcores(ni, nj, nxcores, nycores)

        for ncore in range(ncores):
            imin, imax = imins[ncore], imaxs[ncore] + 1
            jmin, jmax = jmins[ncore], jmaxs[ncore] + 1
            dat[jmin:jmax, imin:imax] += 1

        self.assertTrue((dat == 1).all())

class TestIdxIsValid(unittest.TestCase):
    """ Unit tests for <tools.idx_is_valid> """

    def test_invalid_1d(self):
        nmax = 5
        a = np.arange(nmax)
        self.assertFalse(tools.idx_is_valid(np.where(a > nmax)))
                
    def test_invalid_2d(self):
        nmax = 5
        a = np.arange(nmax)
        self.assertFalse(tools.idx_is_valid(np.where(a > nmax**2)))

    def test_with_valid_1d(self):
        nmax = 5
        a = np.arange(nmax)
        self.assertTrue(tools.idx_is_valid(np.where(a > 0)))
                
    def test_with_valid_2d(self):
        nmax = 5
        a = np.arange(nmax)
        self.assertTrue(tools.idx_is_valid(np.where(a > 0)))
        

class TestInterp1d(unittest.TestCase):
    """ Unit tests for <tools.interp_1d>"""
    
    def test_interp_1d(self):
        x = np.arange(6)*2
        xnew = np.arange(5)*2 + 1
        self.assertTrue(all(tools.interp_1d(xnew, x, x) == xnew))


class TestInterpFullDepth(unittest.TestCase):
    """ Unit tests for <tools.interp_fulldepth>" """
    
    def test_for_mdi(self):
        """ Test case for profile with missing data.""" 
        ob_z = np.arange(10)
        mdl_z = np.arange(15)
        mdl_dat = np.ma.MaskedArray(mdl_z, mask=True)
        interp_z, interp_dat = tools.interp_fulldepth(
            mdl_z, mdl_dat, ob_z)
        self.assertTrue(all(interp_dat.mask == True))
        self.assertTrue(len(interp_z) == len(ob_z))
        
    def test_using_valid_data(self):
        """ Test case for valid data with some missing values. """ 
        ob_z = np.arange(10)
        mdl_z = np.arange(15)
        mdl_dat = np.ma.MaskedArray(mdl_z, mask=mdl_z > 10)
        interp_z, interp_dat = tools.interp_fulldepth(
            mdl_z, mdl_dat, ob_z)
        self.assertTrue(mdl_dat.min() == interp_dat.min())
        self.assertTrue(mdl_dat.max() == interp_dat.max())
        self.assertTrue(len(ob_z) == len(interp_z))


class TestInterpObsDepth(unittest.TestCase):
    """ Unit tests for <tools.interp_obsdepth>"""
    
    def test_for_missing_mdl(self):
        """ Test case for model profile with missing data.""" 
        ob_z = np.arange(10)
        ob_dat = np.ma.MaskedArray(ob_z, mask=False)
        mdl_z = np.arange(15)
        mdl_dat = np.ma.MaskedArray(mdl_z, mask=True)
        interp_z, interp_dat = tools.interp_obsdepth(
            mdl_z, mdl_dat, ob_z, ob_dat)
        self.assertTrue(all(interp_dat.mask == True))
        self.assertTrue(len(interp_z) == len(ob_z))
        
    def test_for_missing_obs(self):
        """ Test case for obs profile with missing data """ 
        ob_z = np.arange(10)
        ob_dat = np.ma.MaskedArray(ob_z, mask=True)
        mdl_z = np.arange(15)
        mdl_dat = np.ma.MaskedArray(mdl_z, mask=False)        
        interp_z, interp_dat = tools.interp_obsdepth(
            mdl_z, mdl_dat, ob_z, ob_dat)
        self.assertTrue(all(interp_dat.mask == True))
        self.assertTrue(len(interp_z) == len(ob_z))
        
    def test_for_non_overlapping(self):
        """ Test case for profiles without overlapping depth ranges """ 
        ob_z = np.linspace(0,1000,100)
        ob_dat = np.ma.MaskedArray(ob_z, mask=ob_z < 500)
        mdl_z = np.linspace(0,1000,150)
        mdl_dat = np.ma.MaskedArray(mdl_z, mask=mdl_z > 500)        
        interp_z, interp_dat = tools.interp_obsdepth(
            mdl_z, mdl_dat, ob_z, ob_dat)
        self.assertTrue(all(interp_dat.mask == True))
        self.assertTrue(len(interp_z) == len(ob_z))
        
    def test_for_masks(self):
        """ Test masks are applied correctly for both model and obs profiles """ 
        ob_z = np.linspace(0,1000,100)
        ob_dat = np.ma.MaskedArray(ob_z, mask=ob_z < 200)
        mdl_z = np.linspace(0,1000,150)
        mdl_dat = np.ma.MaskedArray(mdl_z, mask=mdl_z > 700)        
        interp_z, interp_dat = tools.interp_obsdepth(
            mdl_z, mdl_dat, ob_z, ob_dat)
        ind1 = np.where(interp_z < 200)
        ind2 = np.where(interp_z > 700)
        self.assertTrue(all(interp_dat[ind1].mask == True))
        self.assertTrue(all(interp_dat[ind2].mask == True))
        
        
class TestResampleDepths(unittest.TestCase):
    """ Unit tests for <tools.resample_depths>""" 

    def test_for_negative(self):
        """ Test for negative depth values"""
        nz = 10
        z = np.arange(5) * -1.
        with self.assertRaises(TypeError) as context:
            tools.resample_depths(z, nz)
            
        self.assertTrue('All depths must be positive values.',
                        context.exception)
        
    def test_for_monotonic(self):
        """ Test for monotonic increase in depths"""
        nz = 10
        z = np.ones(5)
        with self.assertRaises(TypeError) as context:
            tools.resample_depths(z, nz)
            
        self.assertTrue('Depths must increase monotonically',
                        context.exception)
        
    def test_upsampling(self):
        """ Test upsampling depths"""
        nz = 20
        z = np.arange(10)
        newz = tools.resample_depths(z, nz)
        self.assertTrue(newz.min() == z.min())
        self.assertTrue(newz.max() == z.max())
        self.assertTrue(len(newz) == nz)
        
    def test_for_downsample(self):
        """ Test downsampling depths"""
        nz = 10
        z = np.arange(20)
        newz = tools.resample_depths(z, nz)
        self.assertTrue(newz.min() == z.min())
        self.assertTrue(newz.max() == z.max())
        self.assertTrue(len(newz) == nz)


class TestFindNearest(unittest.TestCase):
    """ Unit tests for <tools.find_nearest_neighbour """
    
    def test_nearest(self):
        """
        Test using 2d lat/lon fields
        
        """
        lats = np.arange(90).reshape(9,10)/10
        lons = (np.arange(90)).reshape(10,9).T/9
        
        iind, jind, d = tools.find_nearest_neigbour(0, 0, lats, lons)
        self.assertEqual((iind, jind), (0, 0))
        iind, jind, d = tools.find_nearest_neigbour(8, 9, lats, lons)
        self.assertEqual((iind, jind), (8, 9))
        iind, jind, d = tools.find_nearest_neigbour(20, 20, lats, lons)
        self.assertEqual((iind, jind), (None, None))
        
if __name__ == '__main__':
    unittest.main()
