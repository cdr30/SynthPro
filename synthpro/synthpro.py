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
    printmsg.start(args, config)
    
    # Build paths to data files
    tools.build_file_name(args, config, 'obs_profiles')
    tools.build_file_name(args, config, 'synth_profiles')
    tools.build_file_name(args, config, 'model_temp')
    tools.build_file_name(args, config, 'model_sal')
    printmsg.inputs(config)
    
    # Create file to store synthetic profiles
    profiles.create_synth_file(config)
    printmsg.outputs(config)
        
    # Load data objects 
    obsDat = profiles.assoc_profiles(config, 'obs_profiles'); printmsg.loading(1)
    synthDat = profiles.assoc_profiles(config, 'synth_profiles'); printmsg.loading(2)
    modelTemp = model.assoc_model(config, 'model_temp'); printmsg.loading(3)
    modelSal = model.assoc_model(config, 'model_sal'); printmsg.loading(4)
        
    # Extract profiles
    extract.extract_profiles(config, obsDat, synthDat, modelTemp, modelSal)
    
    # Finished
    print '\nFinished!\n'
 
