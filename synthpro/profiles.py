"""
Data classes for profile data.

"""

from netCDF4 import Dataset
import shutil
import numpy as np


class ShapeError(Exception):
    pass

class ProfileTypeError(Exception):
    pass

class Profiles(object):
    """
    Class containing methods to read from/write to
    netcdf files containing observed profile data
    
    """
    def __init__(self, config, profile_type='obs_profiles', preload_data=True):
        """
        Initialize Profile class using configuration options
        
        """
        self.f = config.get(profile_type, 'file_name')        
        self.temp_var = config.get(profile_type, 'temp_var')
        self.sal_var = config.get(profile_type, 'sal_var')
        self.depth_var = config.get(profile_type, 'depth_var')
        self.lat_var = config.get(profile_type, 'lat_var')
        self.lon_var = config.get(profile_type, 'lon_var')
              
        if preload_data:
            self.load_temps()
            self.load_sals()
            self.load_depths()
            self.load_lats()
            self.load_lons()
            
    def read_var(self, ncvar):
        """ Read data from specified variable """
        ncf = Dataset(self.f)
        dat = ncf.variables[ncvar][:]
        ncf.close()
        return dat   
                       
    def load_temps(self):
        """ Load temperatures as <np.array> with dimensions [n, z] """
        self.temps = self.read_var(self.temp_var)
        self.test_shape(self.temp_var, self.temps.shape, 2)
        
    def load_sals(self):
        """ Load salinities as <np.array> with dimensions [n, z] """
        self.sals = self.read_var(self.sal_var)
        self.test_shape(self.sal_var, self.sals.shape, 2)
        
    def load_depths(self):
        """ Load depths as <np.array> with dimensions [n, z] """
        self.depths = self.read_var(self.depth_var)
        self.test_shape(self.depth_var, self.depths.shape, 2)
        
    def load_lats(self):
        """ Load latitudes as <np.array> with dimensions [n] """
        self.lats = self.read_var(self.lat_var)
        self.test_shape(self.lat_var, self.lats.shape, 1)
        
    def load_lons(self):
        """ Load longitudes as <np.array> with dimensions [n] """
        self.lons = self.read_var(self.lon_var)
        self.test_shape(self.lon_var, self.lons.shape, 1)
        
    def test_shape(self, varname, varshape, ndim):
        if len(varshape) != ndim:
            raise ShapeError('Shape=%s. Expected %i-D array for %s' %
                              (repr(varshape), ndim, varname))
        

class SynthProfiles(Profiles):
    """
    Profile class containing additional methods to write 
    synthetic data to file.
    
    """
    def __init__(self, config, profile_type='synth_profiles', preload_data=True, read_only=False):
        """ Extend __init__ method for SynthProfile class. """
        
        Profiles.__init__(self, config, profile_type=profile_type, preload_data=preload_data)
        self.dist_var = 'distance_to_ob'
        self.i_var = 'i_index'
        self.j_var = 'j_index'

        if not read_only:
            for synthvar in [self.dist_var, self.i_var, self.j_var]:
                self.duplicate_var(self.lat_var, synthvar)

    def load_dists(self):
        """ Load distances as <np.array> with dimensions [n] """
        self.dists = self.read_var(self.dist_var)
        self.test_shape(self.dist_var, self.dists.shape, 1)
        
    def load_i(self):
        """ Load i indices as <np.array> with dimensions [n] """
        self.i = self.read_var(self.i_var)
        self.test_shape(self.i_var, self.i.shape, 1)

    def load_j(self):
        """ Load j indices as <np.array> with dimensions [n] """
        self.j = self.read_var(self.j_var)
        self.test_shape(self.j_var, self.j.shape, 1)

    def write_var(self, ncvar, dat):
        """ Write data to specified variable """#
        ncf = Dataset(self.f, 'r+')
        var = ncf.variables[ncvar]
        var[:] = dat
        ncf.close()
        
    def write_dist(self, dat):
        """ Write distance data to file. """
        self.write_var(self.dist_var, dat)
        
    def write_i(self, dat):
        """ Write i index to file. """
        self.write_var(self.i_var, dat)
        
    def write_j(self, dat):
        """ Write j index to file. """
        self.write_var(self.j_var, dat)    
        
    def write_depths(self, dat):
        """ Write depth data to file. """
        self.write_var(self.depth_var, dat)
                
    def write_temps(self, dat):
        """ Write depth data to file. """
        self.write_var(self.temp_var, dat)
    
    def write_sals(self, dat):
        """ Write depth data to file. """
        self.write_var(self.sal_var, dat)

    def duplicate_var(self, ncvar1, ncvar2):
        """ Create new variable based on existing variable """
        ncf = Dataset(self.f, 'r+')
        var1 = ncf.variables[ncvar1]
        ncf.createVariable(ncvar2, var1.dtype, dimensions=var1.dimensions,
                           fill_value=1e20)
        ncf.close()
      


def assoc_profiles(config, profile_type, **kwargs):
    """
    Return profile class object of appropriate type
    associated with file on disk. 
    
    """
    data_type = config.get('obs_profiles', 'data_type')   
    
    if data_type == 'EN4':
        if profile_type == 'obs_profiles':
            proDat = Profiles(config, **kwargs)
        elif profile_type == 'synth_profiles':
            proDat = SynthProfiles(config, **kwargs)
            
    else:
        print 'Profile type %s not recognized' % data_type
        print 'Attempting to load profile data assuming default EN4 data structure'
        try:
            if profile_type == 'obs_profiles':
                proDat = Profiles(config, **kwargs)
            elif profile_type == 'synth_profiles':
                proDat = SynthProfiles(config, **kwargs)
        except:
            raise ProfileTypeError('Failed to load profile data of type: %s' % data_type)
    
    return proDat

 
def create_synth_file(config):
    """
    Create a copy of netcdf containing observed profiles
    to hold synthetic profiles.
    
    """
    obsf = config.get('obs_profiles', 'file_name')
    synthf = config.get('synth_profiles', 'file_name')
    shutil.copy(obsf, synthf)

