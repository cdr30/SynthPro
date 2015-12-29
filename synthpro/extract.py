"""
Profile extraction routines. 

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

    mdl_dat = modelDat.extract_profile(ob_lat, ob_lon)
    mdl_z = modelDat.depths
        
    if config.getboolean('options', 'extract_full_depth'):
        extr_z, extr_dat = tools.interp_fulldepth(mdl_z, mdl_dat, ob_z)
    else:
        extr_z, extr_dat = tools.interp_obsdepth(mdl_z, mdl_dat, ob_z, ob_dat)

    return extr_z, extr_dat



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

