#!/usr/bin/env python2.7
"""
Script to compare model data and extracted synthetic profiles.

"""

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import argparse


def get_args():
    """
    Get arguments from command line.
    
    """
    parser = argparse.ArgumentParser(
        description='Plot model data and extracted synthetic profiles.')
    parser.add_argument(
        'mdlf', help='Path to netcdf file containing model data.')
    parser.add_argument(
        'synf', help='Path to netcdf file containing synthetic profiles')
    parser.add_argument(
        'nprof', help='Number of profiles to plot')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()

    ### Load model data
    mnc = Dataset(args.mdlf)
    mt = mnc.variables['votemper'][:]
    ms = mnc.variables['vosaline'][:]
    mz = mnc.variables['deptht'][:]
    
    ### Load synth profiles 
    snc = Dataset(args.synf)
    st = snc.variables['POTM_CORRECTED'][:]
    ss = snc.variables['PSAL_CORRECTED'][:]
    sz = snc.variables['DEPH_CORRECTED'][:]
    i = snc.variables['i_index'][:]
    j = snc.variables['j_index'][:]
    
    # Plot temperature profiles
    nplotted = 0
    ind = 0
    while nplotted < np.int(args.nprof):
    
        if np.isnan(i[ind]) or np.isnan(j[ind]):
            pass
        else:
            plt.plot(mt[0,:,j[ind], i[ind]], -mz, 'k')
            plt.plot(st[ind], -sz[ind], 'or')
            nplotted += 1
        
        ind += 1
        
    plt.show()

    # Plot salinity profiles
    nplotted = 0
    ind = 0
    while nplotted < np.int(args.nprof):
    
        if np.isnan(i[ind]) or np.isnan(j[ind]):
            pass
        else:
            plt.plot(ms[0,:,j[ind], i[ind]], -mz, 'k')
            plt.plot(ss[ind], -sz[ind], 'or')
            nplotted += 1
        
        ind += 1
        
    plt.show()