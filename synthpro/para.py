"""
Housekeeping routines for running synthpro in parallel using openMPI.

"""

import numpy as np

import tools
import profiles
import printmsg

def combine_profiles(args, config, size):
    """
    Combine synthetic profiles returned by each process and 
    choose between any  duplicates using the minimum distance between 
    ob and model location.
    
    """
    synthDatFinal = profiles.assoc_profiles(config, 'synth_profiles')
    
    for nf in np.arange(size)[1:]:
        printmsg.combining(nf+1, size)
        oldsuffix = '_core%i.nc' % (nf - 1)
        newsuffix = '_core%i.nc' % (nf)
        
        config = update_fpattern(config, 'synth_profiles',
                  oldsuffix=oldsuffix, newsuffix=newsuffix)
        config = tools.build_file_name(args, config, 'synth_profiles')
        synthDat = profiles.assoc_profiles(config, 'synth_profiles')
        
        ind = np.where(synthDat.dists < synthDatFinal.dists)
        if tools.idx_is_valid(ind):
            synthDatFinal.dists[ind] = synthDat.dists[ind]
            synthDatFinal.temps[ind] = synthDat.temps[ind]
            synthDatFinal.sals[ind] = synthDat.sals[ind]
            synthDatFinal.depths[ind] = synthDat.depths[ind]
        
        tools.rmfile(config.get('synth_profiles', 'file_name'))
            
    
        
    synthDatFinal.write_sals(synthDatFinal.sals)
    synthDatFinal.write_temps(synthDatFinal.temps)
    synthDatFinal.write_depths(synthDatFinal.depths)
    synthDatFinal.write_dist(synthDatFinal.dists)


def update_fpattern(config, section, oldsuffix='.nc', newsuffix='_suffix.nc'):
    """
    Update file path used to create synthetic profiles
    to include rank of process.
    
    """
    fpattern = config.get(section, 'fpattern')
    fpattern = fpattern.replace(oldsuffix, newsuffix)
    config.set(section, 'fpattern', value=fpattern)
    
    return config
    

def check_ncores(config, size):
    """
    Check that number of cores in MPI matches
    nx/ny in namelist configuration file.
    
    """
    nxcores = config.getint('parallel', 'nxcores')
    nycores = config.getint('parallel', 'nycores')
    
    if size != nxcores*nycores:
        raise ValueError('Number of MPI cores != nxcores * nycores')
    

def update_ij_range(config, rank):
    """ Update model imin/imax and jmin/jmax for the specified core"""

    nxcores= config.getint('parallel', 'nxcores')
    nycores= config.getint('parallel', 'nycores')

    for data_type in ['model_temp', 'model_sal']:
        imin = config.getint(data_type, 'imin')
        imax = config.getint(data_type, 'imax')
        jmin = config.getint(data_type, 'jmin')
        jmax = config.getint(data_type, 'jmax')
        
        ni = imax - imin + 1
        nj = jmax - jmin + 1
        imins, imaxs, jmins, jmaxs = tools.mapcores(ni, nj, nxcores, nycores)
        config.set(data_type, 'imin', value='%i' % imins[rank])
        config.set(data_type, 'imax', value='%i' % imaxs[rank])
        config.set(data_type, 'jmin', value='%i' % jmins[rank])
        config.set(data_type, 'jmax', value='%i' % jmaxs[rank])
        
    return
