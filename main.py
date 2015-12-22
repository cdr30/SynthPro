"""
Module containing high-level routines to execute synthpro.

"""

import parse_args
import namelist
import profiles
import model
import extract
import tools


def loadingbar(n, nmax=4):
    """ Print progress bar for loading data"""
    tools.print_progress('Loading data', nmax, n)


def print_start(args, config):
    """ Print start message."""
    msg = '\nRunning SynthPro for ${YYYY}${MM}${DD}'
    print tools.insert_date(args, config, msg) 


def print_inputs(config):
    """ Print input files."""
    print '\nInput profile data: ' + config.get('obs_profiles', 'file_name')
    print 'Input model T data: ' + config.get('model_temp', 'file_name') 
    print 'Input model S data: ' + config.get('model_sal', 'file_name') + '\n'


def print_outputs(config):
    """ Print outputs """
    print '\nCreating output file: ' + config.get('synth_profiles', 'file_name') + '\n'


def main():
    """ Execute synthetic profile extraction code """
        
    # Parse arguments and configuration files
    args = parse_args.get_args()
    config = namelist.get_namelist(args)
    print_start(args, config)
    
    # Build paths to data files
    tools.build_file_name(args, config, 'obs_profiles')
    tools.build_file_name(args, config, 'synth_profiles')
    tools.build_file_name(args, config, 'model_temp')
    tools.build_file_name(args, config, 'model_sal')
    print_inputs(config)
    
    # Create file to store synthetic profiles
    profiles.create_synth_file(config)
    print_outputs(config)
        
    # Load data objects 
    loadingbar(0)
    obsDat = profiles.assoc_profiles(config, 'obs_profiles', preload_data=True); loadingbar(1)
    synthDat = profiles.assoc_profiles(config, 'synth_profiles', preload_data=True); loadingbar(2)
    modelTemp = model.assoc_model(config, 'model_temp', preload_data=True); loadingbar(3)
    modelSal = model.assoc_model(config, 'model_sal', preload_data=True); loadingbar(4)
        
    # Extract profiles
    extract.extract_profiles(config, obsDat, synthDat, modelTemp, modelSal)
    
    # Finished
    print '\nFinished!\n'
 
