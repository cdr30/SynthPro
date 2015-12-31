"""
Data classes for gridded model data.

"""

from netCDF4 import Dataset
import numpy as np


import tools


class ShapeError(Exception):
    pass


class ModelData(object):
    """
    Class containing methods to read data from
    a NEMO-type netcdf file.
    
    """
    def __init__(self, config, data_type, preload_data=True):
        """
        Initialize <ModelData> object using configuration options
        
        """        
        self.f = config.get(data_type, 'file_name')
        self.maskf = config.get(data_type, 'maskf')
        self.mask_var = config.get(data_type, 'mask_var')
        self.mask_mdi = config.getfloat(data_type, 'mask_mdi')
        self.data_var = config.get(data_type, 'data_var')
        self.depth_var = config.get(data_type, 'depth_var')
        self.lat_var = config.get(data_type, 'lat_var')
        self.lon_var = config.get(data_type, 'lon_var')
        self.mask_loaded = False 
      
        if preload_data:
            self.load_data()
            self.load_depths()
            self.load_lats()
            self.load_lons()
            
    def read_var(self, ncvar, altf=None):
        """ Read data from specified variable """
        if altf is None:
            ncf = Dataset(self.f)
        else:
            ncf = Dataset(altf)
        
        dat = ncf.variables[ncvar][:]
        ncf.close()
        
        return dat

    def load_data(self):
        """ Load data as <np.array> with dimensions [z, x, y] """
        self.data = np.squeeze(self.read_var(self.data_var))
        self.test_shape(self.data_var, self.data.shape, 3)
        self.load_mask()
        self.data = tools.mask_data(self.data, self.mask, self.mask_mdi)

        
    def load_depths(self):
        """ Load depths as <np.array> with dimensions [z] """
        self.depths = np.squeeze(self.read_var(self.depth_var))
        self.test_shape(self.depth_var, self.depths.shape, 1)
        
    def load_lats(self):
        """ Load latitudes as <np.array> with dimensions [y, x]
            and fill value of +1e20 """
        self.lats = np.squeeze(self.read_var(self.lat_var))
        self.test_shape(self.lat_var, self.lats.shape, 2)
        self.lats = tools.mask_data(
            self.lats, self.mask[0], self.mask_mdi, fill_value=1e20)
        self.lats = self.lats.filled()
        
    def load_lons(self):
        """ Load longitudes as <np.array> with dimensions [y, x] 
            and fill value of +1e20 """
        self.lons = np.squeeze(self.read_var(self.lon_var))
        self.test_shape(self.lon_var, self.lons.shape, 2)
        self.lons = tools.mask_data(
            self.lons, self.mask[0], self.mask_mdi, fill_value=1e20)
        self.lons = self.lons.filled()

    def load_mask(self):
        """ Load longitudes as <np.array> with dimensions [z, y, x] """
        if not self.mask_loaded:
            self.mask = np.squeeze(self.read_var(self.mask_var, altf=self.maskf))
            self.test_shape(self.mask_var, self.mask.shape, 3)
            self.mask_loaded = True

    def find_nearest(self, lat, lon):
        """ Extract model profile for the specified i, j coord."""
        j, i = tools.find_nearest_neigbour(lat, lon, self.lats, self.lons)

        return j, i
    
    def extract_profile(self, lat, lon):
        """ Extract model profile for the specified lat/lon """
        j, i = self.find_nearest(lat, lon)
        
        return self.data[:, j, i]
        
    def test_shape(self, varname, varshape, ndim):
        if len(varshape) != ndim:
            raise ShapeError('Shape=%s. Expected %i-D array for %s' %
                              (repr(varshape), ndim, varname))

    
def assoc_model(config, data_type, **kwargs):
    """
    Return model class object of appropriate type
    associated with file on disk. 
    
    """
    model_type = config.get(data_type, 'model_type')
          
    if model_type == 'NEMO':
        modelDat = ModelData(config, data_type, **kwargs)
    else:
        print 'Model type %s not recognized' % model_type
        print 'Attempting to load model data assuming default NEMO data structure'
        modelDat = ModelData(config, data_type, **kwargs)
    
    return modelDat

 

