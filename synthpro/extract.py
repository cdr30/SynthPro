"""
Profile extraction routines. 

"""

import numpy as np

import tools
import printmsg


def extract_profile(config, modelDat, ob_z, ob_lat, ob_lon, ob_dat):
    """ Extract profile at an observed location """

    mdl_dat, dist = modelDat.extract_profile(ob_lat, ob_lon)
    mdl_z = modelDat.depths
        
    if config.getboolean('options', 'extract_full_depth'):
        extr_z, extr_dat = tools.interp_fulldepth(mdl_z, mdl_dat, ob_z)
    else:
        extr_z, extr_dat = tools.interp_obsdepth(mdl_z, mdl_dat, ob_z, ob_dat)

    return extr_z, extr_dat, dist


def extract_profiles(config, obsDat, synthDat, modelTemp, modelSal):
    """ Extract synthetic profiles from model data for each observed location """
    
    nobs = np.arange(len(obsDat.lats))
    nmax = nobs.max() + 1
    syn_depths = synthDat.depths
    syn_temps = synthDat.temps
    syn_sals = synthDat.sals
    syn_dist = np.ma.MaskedArray(synthDat.lats, mask=False)
    
    for nob in nobs:        
        ob_lat = obsDat.lats[nob]
        ob_lon = obsDat.lons[nob]
        ob_t = obsDat.temps[nob]
        ob_s = obsDat.sals[nob]
        ob_z = obsDat.depths[nob]
                
        syn_z, syn_t, dist = extract_profile(config, modelTemp, ob_z, ob_lat, ob_lon, ob_t)
        syn_z, syn_s, dist = extract_profile(config, modelSal, ob_z, ob_lat, ob_lon, ob_s)
        
        syn_depths[nob] = syn_z
        syn_temps[nob] = syn_t
        syn_sals[nob] = syn_s
        syn_dist[nob] = dist
        
        if config.getboolean('options', 'print_stdout'):
            printmsg.extracting(nob + 1, nmax)
    
    synthDat.write_sals(syn_sals)
    synthDat.write_temps(syn_temps)
    synthDat.write_depths(syn_depths)
    synthDat.write_dist(syn_dist)
    
    if config.getboolean('options', 'print_stdout'):
        printmsg.writing(1, 1)
        
