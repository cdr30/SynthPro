#!/usr/bin/env python2.7

"""
Script to generate directory structure and symbolic links for a SynthPro dataset. 

"""

import ConfigParser
import argparse
import os
import glob


def get_args():
    """ Return arguments from command line """
    parser = argparse.ArgumentParser(
        description='Prepare directory structure for generation of a SynthPro dataset')
    parser.add_argument('config', type=str, help='Path to config.ini file.')
    parser.add_argument('namelist', type=str, help='Path to namelist.ini file.')
    args = parser.parse_args()

    return args

def get_namelist(args):
    """ Return config  as a <ConfigParser> object """
    namelist = ConfigParser.ConfigParser()
    namelist.read(args.namelist)
    
    return namelist

def get_config(args):
    """ Return config  as a <ConfigParser> object """
    config = ConfigParser.ConfigParser()
    config.read(args.config)
    
    return config


def print_config(config):
    for section in config.sections():
        print '\n%s\n' % (section)
        for item1,item2 in config.items(section):
            print item1, item2

            
def create_dir(dirname):
    """ Create directory, else raise warning """

    try:
        os.makedirs(dirname)
    except OSError:
        if not os.path.isdir(dirname):
            raise IOError('Cannot create directory, file exists: %s' % dirname)


def next_mon(yr, mon):
    """ Increment year and month by one month """

    if mon + 1 > 12:
        yr += 1
        mon = 1
    else:
        mon += 1

    return yr, mon
    

def replace_yr_mon(string, yr, mon):
    """ Replace year and month in string """
    
    string = string.replace('${YYYY}', '%4i' % yr)
    string = string.replace('${MM}', '%02i' % mon)
    
    return string


def create_symlink(f, link):
    """ Create symlink to file"""

    try:
        os.symlink(f, link)
    except OSError:
        if not os.path.realpath(f) == os.path.realpath(link):
            raise IOError('Failed to create link. File exists: %s' % link)
        

def match_one_file(modelf):
    """ Return a single file matching modelf, else raise warning """
    files = glob.glob(modelf)

    if len(files) != 1:
        raise IOError('Path must match one file only: %s' % modelf)

    return files[0]


def create_dirs(config):
    """ Create directory structure for SynthPro dataset """

    rootdir = config.get('dataset', 'rootdir')
    name = config.get('dataset', 'name')
    topdir = '%s%s/' % (rootdir, name)
    print 'Setting up dataset: ' + topdir
    
    config.set('dataset', 'topdir', topdir)
    config.set('dataset', 'obsdir', topdir + 'obs_profiles/')      
    config.set('dataset', 'modeldir', topdir + 'model_data/')        
    config.set('dataset', 'synthdir', topdir + 'synth_profiles/')    
    config.set('dataset', 'plotsdir', topdir + 'plots/')             
    config.set('dataset', 'datadir', topdir + 'validation_data/')   
    config.set('dataset', 'tmpdir', topdir + 'tmp/')               
    
    create_dir(config.get('dataset', 'topdir'))
    create_dir(config.get('dataset', 'obsdir'))
    create_dir(config.get('dataset', 'modeldir'))
    create_dir(config.get('dataset', 'synthdir'))
    create_dir(config.get('dataset', 'plotsdir'))
    create_dir(config.get('dataset', 'datadir'))
    create_dir(config.get('dataset', 'tmpdir'))
 
    return config


def create_links_to_obs(config):
    """ Generate symbolic links to observational profiles """

    obsdir = config.get('obs', 'dir')
    linkdir = config.get('dataset', 'obsdir')
    fpattern = config.get('obs', 'fpattern')
    start_yr = config.getint('obs', 'start_yr')
    start_mon = config.getint('obs', 'start_mon')
    end_yr = config.getint('obs', 'end_yr')
    end_mon = config.getint('obs', 'end_mon')

    yr, mon = start_yr, start_mon

    while True:
        obsf = replace_yr_mon(fpattern, yr, mon)
        obspath = obsdir + obsf
        obslink = linkdir + obsf
        create_symlink(obspath, obslink)
        
        if (yr == end_yr) & (mon == end_mon):
            break

        yr, mon = next_mon(yr, mon)

       
def create_links_to_model(config):
    """ Generate symbolic links to model data """

    for model_dat in ['model_temp', 'model_sal']:

        # Read data locations
        modeldir = config.get(model_dat, 'dir')
        modelpat = config.get(model_dat, 'fpattern')
        linkdir = config.get('dataset', 'modeldir')

        # Read model date info
        model_start_yr = config.getint('model', 'start_yr')
        model_start_mon = config.getint('model', 'start_mon')
        model_end_yr = config.getint('model', 'end_yr')
        model_end_mon = config.getint('model', 'end_mon')

        # Read obs data info
        obs_start_yr = config.getint('obs', 'start_yr')
        obs_start_mon = config.getint('obs', 'start_mon')
        obs_end_yr = config.getint('obs', 'end_yr')
        obs_end_mon = config.getint('obs', 'end_mon')

        # Intialize counters
        model_yr, model_mon = model_start_yr, model_start_mon
        obs_yr, obs_mon = obs_start_yr, obs_start_mon    

        # Create links
        while True:
            modelf = modeldir + replace_yr_mon(modelpat, model_yr, model_mon)
            modelf = match_one_file(modelf)
            modellink = linkdir + '%s_%4i%02i.nc' % (model_dat, obs_yr, obs_mon)
            create_symlink(modelf, modellink)
        
            if (model_yr == model_end_yr) & (model_mon == model_end_mon):
                break

            obs_yr, obs_mon = next_mon(obs_yr, obs_mon)
            model_yr, model_mon = next_mon(model_yr, model_mon)
        

def create_links_to_metadata(config):
    """ Generate symbolic links to model metadata """

    topdir = config.get('dataset', 'topdir')
    meshf = config.get('model', 'mesh')
    create_symlink(meshf, topdir + 'mesh.nc')
    basinf = config.get('model', 'basin')
    create_symlink(basinf, topdir + 'basin.nc')
    tmaskf = config.get('model_temp', 'maskf')
    create_symlink(tmaskf, topdir + 'tmask.nc')
    smaskf = config.get('model_sal', 'maskf')
    create_symlink(tmaskf, topdir + 'smask.nc')


def update_namelist(config, namelist):
    """ Update template namelist using config options """

    # Update directoies
    namelist.set('obs_profiles', 'dir', config.get('dataset', 'obsdir'))
    namelist.set('synth_profiles', 'dir', config.get('dataset', 'synthdir'))
    namelist.set('model_temp', 'dir', config.get('dataset', 'modeldir'))
    namelist.set('model_sal', 'dir', config.get('dataset', 'modeldir'))
    
    # Update fpatterns
    obspat = config.get('obs', 'fpattern')
    namelist.set('obs_profiles', 'fpattern', obspat)
    synthpat = obspat.replace('.nc', '.%s.nc' % config.get('dataset', 'name'))
    namelist.set('synth_profiles', 'fpattern', synthpat)
    namelist.set('model_temp', 'fpattern', 'model_temp_${YYYY}${MM}.nc' )
    namelist.set('model_sal', 'fpattern', 'model_sal_${YYYY}${MM}.nc')

    # Update mask files
    namelist.set('model_temp', 'maskf', config.get('dataset', 'topdir') + 'tmask.nc')
    namelist.set('model_sal', 'maskf', config.get('dataset', 'topdir') + 'smask.nc')

    return namelist


def write_namelist(config, namelist):
    """ Write namelist in present directory and in data directory """

    pwd = os.getcwd()
    fname_local = '%s/namelist.%s.ini' % (pwd, config.get('dataset', 'name'))
    fname_topdir = config.get('dataset', 'topdir') + 'namelist.ini'

    print 'Creating namelist: %s' % fname_local
    
    with open(fname_local, 'w') as configfile:
        namelist.write(configfile)
        
    with open(fname_topdir, 'w') as configfile:
        namelist.write(configfile)
    
    
def write_config(config):
    """ Write config to data directory """
    fname = '%sconfig.ini' % config.get('dataset', 'topdir')

    with open(fname, 'w') as configfile:
        config.write(configfile)

          
def create_readme(config):
    """ Generate readme file in data directory """
    readmef = config.get('dataset','topdir') + 'README.txt'
    print 'Writing readme: %s' % (readmef)
    
    with open(readmef, 'w') as f:
        f.write('SynthPro dataset %s\n\n' % config.get('dataset', 'name'))
        f.write('This directory contains synthetic versions of observed\n'
                'ocean temperature and salinity profiles extracted from\n'
                'the %s model.\n\n' % (config.get('model', 'model_name')))
        f.write('Profiles were generated using SynthPro:\n'
                '%s\n\n' % config.get('dataset','code_version'))
        f.write('Profile locations are from %s for the period'
                '%i/%i - %i/%i.\n\n' %
                (config.get('obs', 'obs_name'),
                 config.getint('obs','start_yr'),
                 config.getint('obs','start_mon'),
                 config.getint('obs','end_yr'),
                 config.getint('obs','end_mon')))        
        f.write('Profiles are generated from the following model data:\n'
                ' * Model name: %s\n * Experiment: %s\n * Experiment ID: %s\n'
                ' * Start year: %s\n * Start month: %s\n * End year: %s\n'
                ' * End month: %s\n\n' % (config.get('model', 'model_name'),
                                     config.get('model', 'exp_desc'),
                                     config.get('model', 'exp_id'),
                                     config.getint('model','start_yr'),
                                     config.getint('model','start_mon'),
                                     config.getint('model','end_yr'),
                                     config.getint('model','end_mon')))
        f.write('Symbolic links to observed profiles are located here:\n %s\n\n'
                % config.get('dataset', 'obsdir'))
        f.write('Symbolic links to model data are located here:\n %s\n\n'
                % config.get('dataset', 'modeldir'))
        f.write('Synthetic profile datasets are located here:\n %s\n\n'
                % config.get('dataset', 'synthdir'))
        f.write('Plots of synthetic vs observed profile data are located here:\n %s\n\n'
                % config.get('dataset', 'plotsdir'))
        f.write('"Model truth" validation data sets are located here:\n %s\n\n'
                % config.get('dataset', 'datadir'))
        f.write('Further SynthPro configuration details are containin within '
                'config.ini and namelist.ini\n\n') 
        f.write('This README.txt file was automatically generated by\n %s' % os.path.realpath(__file__))
        
        
if __name__ == '__main__':

    # Read config files
    args = get_args()
    config = get_config(args)
    namelist = get_namelist(args)
    
    # Write updated config files
    config = create_dirs(config)
    write_config(config)
    namelist = update_namelist(config, namelist)
    write_namelist(config, namelist)
    create_readme(config)
    
    print 'Creating links ...'
    create_links_to_obs(config)
    create_links_to_model(config)
    create_links_to_metadata(config)
