"""
Module containing routines to print messages to standard output.

"""

import tools
import sys

def message(config, message):
    """ Print message """
    if config.getboolean('options', 'print_stdout'): 
        print '\n %s \n' % (message)

def finished(config):
    """ Print finished message """
    if config.getboolean('options', 'print_stdout'): 
        print '\nFinished!\n'
    
def extracting(config, n, nmax):
    """ Print progress bar for extraction of data"""
    if config.getboolean('options', 'print_stdout'):
        tools.print_progress('Extracting synthetic data', nmax, n)
    
def combining(config, n, nmax):
    """ Print progress bar for combining synthetic profiles"""
    if config.getboolean('options', 'print_stdout'):
        tools.print_progress('Combining synthetic data', nmax, n)
    
def writing(config):
    """ Print progress bar for extraction of data"""
    if config.getboolean('options', 'print_stdout'): 
        print '\nSaving synthetic profiles: ' + config.get('synth_profiles', 'file_name') + '\n'
            
def loading(config):
    """ Print progress bar for loading data"""
    if config.getboolean('options', 'print_stdout'): 
        print '\nLoading data...\n'

def start(args, config):
    """ Print start message."""
    if config.getboolean('options', 'print_stdout'):
        msg = '\nRunning SynthPro for ${YYYY}${MM}${DD}'
        print tools.insert_date(args, config, msg) 

def inputs(config):
    """ Print input files."""
    if config.getboolean('options', 'print_stdout'):            
        print '\nInput profile data: ' + config.get('obs_profiles', 'file_name')
        print 'Input model T data: ' + config.get('model_temp', 'file_name') 
        print 'Input model S data: ' + config.get('model_sal', 'file_name')
        print 'Synthetic profile data: ' + config.get('synth_profiles', 'file_name')+ '\n'

def outputs(config):
    """ Print outputs """
    if config.getboolean('options', 'print_stdout'):        
        print '\nCreating output file: ' + config.get('synth_profiles', 'file_name') + '\n'
        
        
        
        
        
        
        
        