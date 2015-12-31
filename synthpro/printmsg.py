"""
Module containing routines to print messages to standard output.

"""

import tools


def extracting(n, nmax):
    """ Print progress bar for extraction of data"""
    tools.print_progress('Extracting synthetic data', nmax, n)
    
    
def writing(n, nmax):
    """ Print progress bar for extraction of data"""
    tools.print_progress('Saving synthetic data', nmax, n)
            

def loading(n, nmax=4):
    """ Print progress bar for loading data"""
    tools.print_progress('Loading data', nmax, n)


def start(args, config):
    """ Print start message."""
    msg = '\nRunning SynthPro for ${YYYY}${MM}${DD}'
    print tools.insert_date(args, config, msg) 


def inputs(config):
    """ Print input files."""
    print '\nInput profile data: ' + config.get('obs_profiles', 'file_name')
    print 'Input model T data: ' + config.get('model_temp', 'file_name') 
    print 'Input model S data: ' + config.get('model_sal', 'file_name') + '\n'


def outputs(config):
    """ Print outputs """
    print '\nCreating output file: ' + config.get('synth_profiles', 'file_name') + '\n'
    

if __name__ == '__main__':
    pass