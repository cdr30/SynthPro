"""
Main profile extraction routines. 

"""

import tools
import numpy as np


def extractingbar(n, nmax):
    """ Print progress bar for extraction of data"""
    tools.print_progress('Extracting synthetic data', nmax, n)
    
    
def writingbar(n, nmax):
    """ Print progress bar for extraction of data"""
    tools.print_progress('Saving synthetic data', nmax, n)


def extract_profile(config, modelDat, ob_z, ob_lat, ob_lon, ob_dat):
    """ Extract profile at an observed location """

    # Add check if obs_dat all masked and skip extraction.
    
    dat = modelDat.extract_profile(ob_lat, ob_lon)
    z = modelDat.depths
        
    if config.getboolean('options', 'extract_full_depth'):
        zind = np.where(dat.mask != True)
        znew = tools.resample_depths(z[zind], len(ob_z))
        datnew = tools.interp_1d(znew, z, dat)
    
    else:
        if all(ob_dat.mask == True):
            datnew = ob_dat
        else:
            zind = np.where(dat.mask != True)
            datnew = tools.interp_1d(ob_z, z[zind], dat[zind])
            new_mask = (ob_dat.mask) | (ob_z > z.max())
            datnew = tools.mask_data(datnew, new_mask, True)
        znew = ob_z 
            
    return znew, datnew


def extract_profiles(config, obsDat, synthDat, modelTemp, modelSal):
    """ Extract synthetic profiles from model data for each observed location """
    
    nobs = np.arange(len(obsDat.dts))
    nmax = nobs.max() + 1
    syn_depths = synthDat.depths
    syn_temps = synthDat.temps
    syn_sals = synthDat.sals
    
    extractingbar(0, nmax)
    for nob in nobs:        
        ob_lat = obsDat.lats[nob]
        ob_lon = obsDat.lons[nob]
        ob_t = obsDat.temps[nob]
        ob_s = obsDat.sals[nob]
        ob_z = obsDat.depths[nob]
                
        syn_z, syn_t = extract_profile(config, modelTemp, ob_z, ob_lat, ob_lon, ob_t)
        syn_z, syn_s = extract_profile(config, modelSal, ob_z, ob_lat, ob_lon, ob_s)
        
        syn_depths[nob] = syn_z
        syn_temps[nob] = syn_t
        syn_sals[nob] = syn_s
        
        extractingbar(nob + 1, nmax)
    
    writingbar(0, 3)
    synthDat.write_sals(syn_sals); writingbar(1, 3)
    synthDat.write_temps(syn_temps); writingbar(2, 3)
    synthDat.write_depths(syn_depths); writingbar(3, 3)

