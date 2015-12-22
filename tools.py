"""
Useful functions.

"""

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline


def interp_1d(xnew, x, y):
    """ Evaluate y at xnew using linear interpolation """

    return np.interp(xnew, x, y)


def resample_depths(z, nz):
    """
    Resample depths while maintaining variable resolution
    using linear interpolation of first-differences.
    
    """
    # Check depths are given as positive values
    if not all(z >= 0):
        raise TypeError('All depths must be positive values.')
    
    # Check data is monotonic
    diffs = np.diff(z)
    if not all(diffs >= 0):
        raise TypeError('Depths must increase monotonically')
    
    # Linearly interpolate first differences
    z_guess = np.linspace(z.min(), z.max(), nz)
    diffs_new = interp_1d(z_guess[0:-1], z[0:-1], diffs)
    scale = np.sum(diffs)/np.sum(diffs_new)
    
    # Sum differences and scale range
    znew = np.cumsum(diffs_new) * scale
    
    # Add initial value
    znew = np.hstack((z[0], znew + z[0]))
    
    return znew


def find_nearest_neigbour(obs_lat, obs_lon, model_lats, model_lons):
    """ Return coordinate for nearest-neighbor model grid-point """ 
    
    tol = 0.25
    init_idx = ([], [])
    
    while len(init_idx[0]) == 0:
        init_idx = np.where((model_lats <= obs_lat + tol) & 
                            (model_lats >= obs_lat - tol) & 
                            (model_lons <= obs_lon + tol) & 
                            (model_lons >= obs_lon - tol))
        tol = tol * 2.
    
    init_lats = model_lats[init_idx]
    init_lons = model_lons[init_idx]
    
    d = equirect_distance(obs_lat, obs_lon, init_lats, init_lons)    
    final_idx = np.unravel_index(d.argmin(), d.shape)
    j, i  = init_idx[0][final_idx], init_idx[1][final_idx]
        
    return j, i 


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Return great circle distance between two points
    using Haversine formula:
    
    a = sin^2((lat1-lat2)/2) + cos(lat1) * cos(lat2) * sin^2((lon1-lon2)/2)
    c = 2 * arctan2(sqrt(a), sqrt(1-a))
    d = R * c
    
    where R is earth's radius
    
    """
    
    R = 6371000. 
    rad_lat1 = np.radians(lat1)
    rad_lat2 = np.radians(lat2)
    rad_lon1 = np.radians(lon1)
    rad_lon2 = np.radians(lon2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = (np.sin(delta_lat/2.)**2 + (np.cos(rad_lat1) * np.cos(rad_lat2) * np.sin(delta_lon/2.)**2))
    c = 2. * np.arctan2(np.sqrt(a), np.sqrt(1.-a))
    
    return R * c
    

def equirect_distance(lat1, lon1, lat2, lon2):
    """
    Return great circle distance between two points
    using equirectangular approximation
    
    """
    R = 6371000.
    dy = np.radians(lat2 - lat1)
    dx = np.radians(lon2 - lon1) * np.cos(np.radians((lat1 + lat2)/2))
    
    d = R  * np.sqrt(dx*dx + dy*dy)
        
    return d
        

def mask_data(dat, mask, mask_mdi, fill_value=None):
    """ Return data as np.ma.MaskedArray with applied mask. """
    
    if fill_value is not None:
        dat = np.ma.MaskedArray(dat, mask=(mask == mask_mdi), fill_value=fill_value)
    else:
        dat = np.ma.MaskedArray(dat, mask=(mask == mask_mdi))

    return dat


def print_progress(task_name, nmax, n, nbar=20):
    """ Print progress to standard out. """
    done = nbar * '|'
    todo = nbar * '.'
    flt_pct = 100. * np.float(n)/nmax
    progind = np.int(flt_pct)/(100/nbar)
    progbar = done[:progind] + todo[progind:]
    
    print ('\r%25s: %s %6.2f%%' %
          (task_name, progbar, flt_pct)),
    
    if np.int(flt_pct) == 100:
        print ''


def insert_date(args, config, f):
    """ Return string with date inserted """
            
    f = f.replace('${YYYY}', '%4i' % args.year)
    f = f.replace('${MM}', '%02i' % args.month)
    
    if config.getboolean('options', 'use_daily_data'):
        if args.day is None:
            raise TypeError(' [-d DAY] must be specified to read daily data.')
        else:
            f = f.replace('${DD}', '%02i' % args.day)          
            
    else:
        f = f.replace('${DD}', '')
    
    return f
    

def build_file_name(args, config, section):
    """
    Create name of file containing profile data
    
    """
    f = config.get(section, 'dir') + config.get(section, 'fpattern')
    f = insert_date(args, config, f)
    config.set(section, 'file_name', value=f)
    