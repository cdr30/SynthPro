"""
Module containing main routines to execute synthpro.

"""

import parse_args
import namelist

import profiles
import model
import extract
import tools
import printmsg


def main():
    """ Execute synthetic profile extraction code """
        
    # Parse arguments and configuration files
    args = parse_args.get_args()
    config = namelist.get_namelist(args)
    if config.getboolean('options', 'print_stdout'): 
        printmsg.start(args, config)
    
    # Build paths to data files
    tools.build_file_name(args, config, 'obs_profiles')
    tools.build_file_name(args, config, 'synth_profiles')
    tools.build_file_name(args, config, 'model_temp')
    tools.build_file_name(args, config, 'model_sal') 
    if config.getboolean('options', 'print_stdout'): 
        printmsg.inputs(config)
    
    # Create file to store synthetic profiles
    profiles.create_synth_file(config)
    if config.getboolean('options', 'print_stdout'): 
        printmsg.outputs(config)
        
    # Load data objects 
    obsDat = profiles.assoc_profiles(config, 'obs_profiles')
    synthDat = profiles.assoc_profiles(config, 'synth_profiles')
    modelTemp = model.assoc_model(config, 'model_temp')
    modelSal = model.assoc_model(config, 'model_sal')
    if config.getboolean('options', 'print_stdout'): 
        printmsg.loading(1,1)
    
    # Extract profiles
    extract.extract_profiles(config, obsDat, synthDat, modelTemp, modelSal)
    
    # Finished
    if config.getboolean('options', 'print_stdout'): 
        printmsg.finished()
 
