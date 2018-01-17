#!/usr/bin/env python2.7

"""
Script to interpolate synthetic profiles to target format

"""

import argparse
from netCDF4 import Dataset
import numpy as np
import shutil
import copy


def get_args():
    """ Return arguments from command line """
    parser = argparse.ArgumentParser(
        description='Interpolate synthetic profiles to target format')
    parser.add_argument('sourcef', type=str, 
                        help='netcdf source file containing synthetic profiles')
    parser.add_argument('targetf', type=str, 
                        help='netcdf file containing original profiles in target format')
    parser.add_argument('outputf', type=str, 
                        help='output file name for synthetic profiles in target format')
    parser.add_argument('--source_latvar', type=str, default='en4_lat',
                        help='Latitude variable name in source file')
    parser.add_argument('--source_lonvar', type=str, default='en4_lon',
                        help='Longitude variable name in source file')
    parser.add_argument('--source_zvar', type=str, default='ts_lev',
                        help='Depth variable name in source file')
    parser.add_argument('--source_tvar', type=str, default='temp',
                        help='Temperature variable name in source file')
    parser.add_argument('--source_svar', type=str, default='salt',
                        help='Salinity variable name in source file')
    parser.add_argument('--source_mdi', type=float, default=1.e20,
                        help='Missing data indicator in source data')
    parser.add_argument('--target_latvar', type=str, default='LATITUDE',
                        help='Latitude variable name in target file')
    parser.add_argument('--target_lonvar', type=str, default='LONGITUDE',
                        help='Longitude variable name in target file')
    parser.add_argument('--target_zvar', type=str, default='DEPH_CORRECTED',
                        help='Depth variable name in target file')
    parser.add_argument('--target_tvar', type=str, default='POTM_CORRECTED',
                        help='Temperature variable name in target file')
    parser.add_argument('--target_svar', type=str, default='PSAL_CORRECTED',
                        help='Salinity variable name in target file')
    parser.add_argument('--target_mdi', type=float, default=1.e20,
                        help='Missing data indicator in target data')
    parser.add_argument('--latlon_tolerance', type=float, default=0.001,
                        help='Tolerance used to test equivalence of lat/lon coordinates')
    args = parser.parse_args()
    return args


class ShapeError(Exception):
    pass


class DimensionError(Exception):
    pass


class ProfileDataError(Exception):
    pass


class Profiles(object):
    """ Class to read and write profile data """
    def __init__(self,
                 ncf='profiles.nc', 
                 tvar='temperature',
                 svar='salinity', 
                 zvar='depth', 
                 latvar='latitude', 
                 lonvar='longitude',
                 mdi = 1e20,
                 latlon_tolerance=0.001):
        """ Create instance holding profile data """
        self.ncf = ncf
        self.latvar = latvar
        self.lonvar = lonvar
        self.tvar = tvar
        self.svar = svar
        self.zvar = zvar
        self.latlon_tolerance = latlon_tolerance
        self.mdi = mdi
        self._read_data()

    def _read_data(self):
        """ Read profile data from netcdf file """
        self._load_temps()
        self._load_sals()
        self._load_depths()
        self._load_lats()
        self._load_lons()

    def save_profiles(self):
        """ Write temperature and salinity profiles to netcdf """
        ds = Dataset(self.ncf, 'r+')
        ds.variables[self.tvar][:] = self.temps
        ds.variables[self.svar][:] = self.sals
        ds.close()
        print 'SAVING: %s' % self.ncf

    def _read_var(self, ncvar):
        """ Read data from specified variable """
        ds = Dataset(self.ncf)
        dat = ds.variables[ncvar][:]
        ds.close()
        return dat   

    def _mask_data(self, dat):
        """ Test for mdi and NaN values and ensure data is masked """
        mask_ind = ( (dat == self.mdi) | np.isnan(dat) )
        dat = np.ma.MaskedArray(dat, mask=mask_ind)
        return dat

    def _load_temps(self):
        """ Load temperatures as <np.array> with dimensions [n, z] """
        self.temps = self._mask_data(self._read_var(self.tvar))
        self._test_ndims(self.tvar, self.temps.shape, 2)
        
    def _load_sals(self):
        """ Load salinities as <np.array> with dimensions [n, z] """
        self.sals = self._mask_data(self._read_var(self.svar))
        self._test_ndims(self.svar, self.sals.shape, 2)
        
    def _load_depths(self):
        """ Load depths as <np.array> with dimensions [n, z] """
        self.depths = np.abs(self._read_var(self.zvar))
        if self.depths.ndim == 1:
            print('WARNING: %s has shape=%s. Broadcasting array to shape=%s'%
                  (self.zvar, repr(self.depths.shape), repr(self.temps.shape)))
            self.depths = np.ones_like(self.temps) * self.depths[np.newaxis]
        self._test_ndims(self.zvar, self.depths.shape, 2)
        
    def _load_lats(self):
        """ Load latitudes as <np.array> with dimensions [n] """
        self.lats = self._read_var(self.latvar)
        self._test_ndims(self.latvar, self.lats.shape, 1)
        
    def _load_lons(self):
        """ Load longitudes as <np.array> with dimensions [n] """
        self.lons = self._read_var(self.lonvar)
        if any(self.lons < 0):
            self.lons[self.lons < 0] += 360
        self._test_ndims(self.lonvar, self.lons.shape, 1)
        
    def _test_ndims(self, varname, varshape, ndim):
        if len(varshape) != ndim:
            raise DimensionError('Shape=%s. Expected %i-D array for %s' %
                              (repr(varshape), ndim, varname))
        
    def _assert_equal(self, array1, array2, tolerance):
        """ Assert that shape and values of two arrays are equal """ 
        if array1.shape != array2.shape:
            raise ShapeError(
                'Different number of profiles in each data set')
        if not np.all(np.abs(array1 - array2) <= tolerance):
            raise ProfileDataError(
                'Profile lat/lon values do not match within +/- %f' % tolerance)
            
    def vinterp_profile(self, source_dat, source_z, target_dat, target_z):
        """ Linearly interpolate single profile onto target depths """
        interp_dat = np.ma.MaskedArray(copy.deepcopy(target_dat), mask=True)
        
        if np.all(target_dat.mask == True):    # Case 1
            interp_dat = np.ma.MaskedArray(copy.deepcopy(target_dat), mask=True)
        elif np.all(source_dat.mask == True): # Case 2
            interp_dat = np.ma.MaskedArray(copy.deepcopy(target_dat), mask=True)
        else:
            source_minz = source_z[source_dat.mask == False].min()
            source_maxz = source_z[source_dat.mask == False].max()
            target_minz = target_z[target_dat.mask == False].min()
            target_maxz = target_z[target_dat.mask == False].max()
            zind_source = (source_z >= source_minz) & (source_z <= source_maxz)
            zind_target = ((target_z >= target_minz) & (target_z <= target_maxz) & 
                           (target_z < source_maxz) & (target_z > source_minz))
            if np.any(zind_target) and np.any(zind_source):
                interp_dat[zind_target] = np.interp(
                    target_z[zind_target],source_z[zind_source],source_dat[zind_source])
        return interp_dat

    def vinterp_profiles(self, source_profiles, source_depths, target_profiles, target_depths):
        """ Linearly interpolate profiles onto target depths """
        interp_profiles = np.ones_like(target_profiles) * 1e20
        nprofiles = source_profiles.shape[0]
        for nprofile in range(nprofiles):
            interp_profiles[nprofile] = self.vinterp_profile(
                source_profiles[nprofile], source_depths[nprofile], 
                target_profiles[nprofile], target_depths[nprofile])
        return interp_profiles

    def update_profiles(self, SourceProfiles):
        """ 
        Update temperature and salinity data with values from 
        another Profiles instance. Data from SourceProfiles are 
        vertically interpolated onto the existing depth coordinate. 
        
        """
        self._assert_equal(self.lats, SourceProfiles.lats, self.latlon_tolerance)
        self._assert_equal(self.lons, SourceProfiles.lons, self.latlon_tolerance)
        self.temps = self.vinterp_profiles(
            SourceProfiles.temps, SourceProfiles.depths,self.temps, self.depths)
        self.sals = self.vinterp_profiles(
            SourceProfiles.sals, SourceProfiles.depths,self.sals, self.depths)


def main():
    """ Interpolate synthetic profiles to target format """
    args = get_args()
    shutil.copy(args.targetf, args.outputf)    
    target_profiles = Profiles(ncf=args.outputf,
                               tvar=args.target_tvar,
                               svar=args.target_svar,
                               zvar=args.target_zvar,
                               latvar=args.target_latvar,
                               lonvar=args.target_lonvar,
                               mdi=args.target_mdi,
                               latlon_tolerance=args.latlon_tolerance)
    source_profiles = Profiles(ncf=args.sourcef,
                               tvar=args.source_tvar,
                               svar=args.source_svar,
                               zvar=args.source_zvar,
                               latvar=args.source_latvar,
                               lonvar=args.source_lonvar,
                               mdi=args.source_mdi,
                               latlon_tolerance=args.latlon_tolerance)  
    target_profiles.update_profiles(source_profiles)
    target_profiles.save_profiles()

if __name__ == '__main__':
    main()
    
  
