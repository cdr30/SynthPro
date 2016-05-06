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
        self.imin = config.getint(data_type, 'imin')
        self.imax = config.getint(data_type, 'imax')
        self.jmin = config.getint(data_type, 'jmin')
        self.jmax = config.getint(data_type, 'jmax')
        self.test_ij_range()
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
        
        dat = ncf.variables[ncvar]
        
        if len(dat.shape) == 1:
            dat = dat[:]
        elif len(dat.shape) == 2:
            dat = dat[self.jmin:self.jmax+1, self.imin:self.imax+1]
        elif len(dat.shape) == 3:
            dat = dat[:, self.jmin:self.jmax+1, self.imin:self.imax+1]
        elif (len(dat.shape) == 4) & (dat.shape[0] == 1):
            dat = dat[0, :, self.jmin:self.jmax+1, self.imin:self.imax+1]
        else:
            raise ShapeError('%s has invalid shape: &s', ncvar,
                             repr(dat.shape))
        
        ncf.close()
        
        return dat

    def load_data(self):
        """ Load data as <np.array> with dimensions [z, x, y] """
        self.data = self.read_var(self.data_var)
        self.test_shape(self.data_var, self.data.shape, 3)
        self.test_ij_index(self.data_var, self.data[0])
        self.load_mask()
        self.data = tools.mask_data(self.data, self.mask, self.mask_mdi)
        
    def load_depths(self):
        """ Load depths as <np.array> with dimensions [z] """
        self.depths = self.read_var(self.depth_var)
        self.test_shape(self.depth_var, self.depths.shape, 1)
        
    def load_lats(self):
        """ Load latitudes as <np.array> with dimensions [y, x]
            and fill value of +1e20 """
        self.lats = self.read_var(self.lat_var)
        self.test_shape(self.lat_var, self.lats.shape, 2)
        self.test_ij_index(self.lat_var, self.lats)
        self.lats = tools.mask_data(
            self.lats, self.mask[0], self.mask_mdi, fill_value=1e20)
        self.lats = self.lats.filled()
        
    def load_lons(self):
        """ Load longitudes as <np.array> with dimensions [y, x] 
            and fill value of +1e20 """
        self.lons = self.read_var(self.lon_var)
        self.test_shape(self.lon_var, self.lons.shape, 2)
        self.test_ij_index(self.lon_var, self.lons)
        self.lons = tools.mask_data(
            self.lons, self.mask[0], self.mask_mdi, fill_value=1e20)
        self.lons = self.lons.filled()

    def load_mask(self):
        """ Load longitudes as <np.array> with dimensions [z, y, x] """
        if not self.mask_loaded:
            self.mask = self.read_var(self.mask_var, altf=self.maskf)
            self.test_shape(self.mask_var, self.mask.shape, 3)
            self.test_ij_index(self.mask_var, self.mask[0])
            self.mask_loaded = True

    def find_nearest(self, lat, lon):
        """ Extract model profile for the specified i, j coord."""
        j, i, dist = tools.find_nearest_neigbour(lat, lon, self.lats, self.lons)

        return j, i, dist
    
    def extract_profile(self, lat, lon):
        """ Return model profile for the specified lat/lon 
        and distance to observed location"""
        j, i, dist = self.find_nearest(lat, lon)
        
        if (j is not None) and (i is not None):
            dat = self.data[:, j, i]
            i += self.imin 
            j += self.jmin
            return dat, dist, j, i
        else:
            return np.ma.MaskedArray(self.data[:, 0, 0], mask=True), dist, j, i
        
    def test_shape(self, varname, varshape, ndim):
        if len(varshape) != ndim:
            raise ShapeError('Shape=%s. Expected %i-D array for %s' %
                              (repr(varshape), ndim, varname))
        
    def test_ij_index(self, varname, dat_2d):
        nj, ni = dat_2d.shape
        
        if (self.imax < 0) or (self.imax - self.imin > ni - 1):
            raise IndexError('imax=%i is invalid. %s has valid range %i-%i.'
                              % (self.imax, varname, 0, ni - 1))
            
        if (self.imin < 0) or (self.imin > ni - 1):
            raise IndexError('imin=%i is invalid. %s has valid range %i-%i.'
                              % (self.imax, varname, 0, ni - 1))
            
        if (self.jmax < 0) or (self.jmax - self.jmin > nj - 1):
            raise IndexError('jmax=%i is invalid. %s has valid range %i-%i.'
                              % (self.jmax, varname, 0, nj - 1))
            
        if (self.jmin < 0) or (self.jmin > nj - 1):
            raise IndexError('jmin=%i is invalid. %s has valid range %i-%i.'
                              % (self.jmax, varname, 0, nj - 1))               

    def test_ij_range(self):
        if (self.imin >= self.imax) or (self.jmin >= self.jmax):
            raise IndexError('Invalid min/max indices: imin=%i,imax=%i, jmin=%i,jmax=%i'
                              % (self.imin, self.imax, self.jmin, self.jmax))

def assoc_model(config, data_type, **kwargs):
    """
    Return model class object of appropriate type
    associated with file on disk. 
    
    """
    model_type = config.get(data_type, 'model_type')
          
    if model_type == 'NEMO':
        modelDat = ModelData(config, data_type, **kwargs)
    else:
        print 'WARNING: Model type %s not recognized' % model_type
        print 'WARNING: attempting to load model data assuming default NEMO data structure'
        modelDat = ModelData(config, data_type, **kwargs)
    
    return modelDat

 

