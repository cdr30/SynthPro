"""
Data classes for profile data.

"""

from netCDF4 import Dataset
import shutil
import datetime
import numpy as np


class ShapeError(Exception):
    pass


class Profiles(object):
    """
    Class containing methods to read from/write to
    netcdf files containing observed profile data
    
    """
    def __init__(self, config, profile_type, preload_data=True):
        """
        Initialize Profile class using configuration options
        
        """
        self.f = config.get(profile_type, 'file_name')        
        self.temp_var = config.get(profile_type, 'temp_var')
        self.sal_var = config.get(profile_type, 'sal_var')
        self.depth_var = config.get(profile_type, 'depth_var')
        self.lat_var = config.get(profile_type, 'lat_var')
        self.lon_var = config.get(profile_type, 'lon_var')
        self.dt_var = config.get(profile_type, 'dt_var')
      
        if preload_data:
            self.load_temps()
            self.load_sals()
            self.load_depths()
            self.load_lats()
            self.load_lons()
            self.load_dts()
      
    def read_var(self, ncvar):
        """ Read data from specified variable """
        ncf = Dataset(self.f)
        dat = ncf.variables[ncvar][:]
        ncf.close()
        return dat   
        
    def write_var(self, ncvar, dat):
        """ Write data to specified variable """#
        #print 'Writing %s to %s' % (ncvar, self.f)
        ncf = Dataset(self.f, 'r+')
        var = ncf.variables[ncvar]
        var[:] = dat
        ncf.close()
        
    def write_depths(self, dat):
        """ Write depth data to file. """
        self.write_var(self.depth_var, dat)
                
    def write_temps(self, dat):
        """ Write depth data to file. """
        self.write_var(self.temp_var, dat)
    
    def write_sals(self, dat):
        """ Write depth data to file. """
        self.write_var(self.sal_var, dat)
                
    def load_dts(self):
        """ Load dates as <np.array> of <datetime.datetime> values """
        jdays = self.read_var(self.dt_var)
        dt0 = datetime.datetime(1950, 01, 01, 0, 0, 0)
        self.dts = np.array([dt0 + datetime.timedelta(jday) for jday in jdays])
        self.test_shape(self.dt_var, self.dts.shape, 1)
        
    def load_temps(self):
        """ Load temperatures as <np.array> with dimensions [t, z] """
        self.temps = self.read_var(self.temp_var)
        self.test_shape(self.temp_var, self.temps.shape, 2)
        
    def load_sals(self):
        """ Load salinities as <np.array> with dimensions [t, z] """
        self.sals = self.read_var(self.sal_var)
        self.test_shape(self.sal_var, self.sals.shape, 2)
        
    def load_depths(self):
        """ Load depths as <np.array> with dimensions [t, z] """
        self.depths = self.read_var(self.depth_var)
        self.test_shape(self.depth_var, self.depths.shape, 2)
        
    def load_lats(self):
        """ Load latitudes as <np.array> with dimensions [t] """
        self.lats = self.read_var(self.lat_var)
        self.test_shape(self.lat_var, self.lats.shape, 1)
        
    def load_lons(self):
        """ Load longitudes as <np.array> with dimensions [t] """
        self.lons = self.read_var(self.lon_var)
        self.test_shape(self.lon_var, self.lons.shape, 1)
        
    def test_shape(self, varname, varshape, ndim):
        if len(varshape) != ndim:
            raise ShapeError('Shape=%s. Expected %i-D array for %s' %
                              (repr(varshape), ndim, varname))
        

def assoc_profiles(config, profile_type, **kwargs):
    """
    Return profile class object of appropriate type
    associated with file on disk. 
    
    """
    data_type = config.get(profile_type, 'data_type')   
    
    if data_type == 'EN4':
        proDat = Profiles(config, profile_type, **kwargs)
    else:
        print 'Profile type %s not recognized' % data_type
        print 'Attempting to load profile data assuming default EN4 data structure'
        proDat = Profiles(config, profile_type, **kwargs)
    
    return proDat

 
def create_synth_file(config):
    """
    Create a copy of netcdf containing observed profiles
    to hold synthetic profiles.
    
    """
    obsf = config.get('obs_profiles', 'file_name')
    synthf = config.get('synth_profiles', 'file_name')
    shutil.copy(obsf, synthf)

