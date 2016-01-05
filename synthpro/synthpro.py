"""
Module containing main routines to execute synthpro.

"""

import parse_args
import namelist
import numpy as np

import profiles
import model
import extract
import tools
import printmsg
import para

try:
    from mpi4py import MPI
except ImportError:
    print 'WARNING: mpi4py not available. Parallel jobs will fail.'
    

def main_singlenode(args, config):
    """ Run a single instance of synthpro """
    
    if config.getboolean('options', 'print_stdout'): 
        printmsg.start(args, config)
    
    # Build paths to data files
    config = tools.build_file_name(args, config, 'obs_profiles')
    config = tools.build_file_name(args, config, 'synth_profiles')
    config = tools.build_file_name(args, config, 'model_temp')
    config = tools.build_file_name(args, config, 'model_sal') 
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


def main_parallel(args, config):
    """ Run synthpro in parallel using openMPI """
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    if rank == 0:
        para.check_ncores(config, size)
    else:
        config.set('options', 'print_stdout', value='False')
    
    para.update_ij_range(config, rank)
    config = para.update_fpattern(config, 'synth_profiles',
                  newsuffix=('_core%i.nc' % rank))

    main_singlenode(args, config)
    comm.Barrier()
    
    if rank == 0:
        para.combine_profiles(args, config, size)


def main():
    """
    Parse command line arguments and options and run synthpro.
    
    """

    args = parse_args.get_args()
    config = namelist.get_namelist(args)
    
    if config.getboolean('parallel', 'submit_parallel'):
        main_parallel(args, config)
    else:
        main_singlenode(args, config)
        
    # Finished
    if config.getboolean('options', 'print_stdout'): 
        printmsg.finished()
 
    

