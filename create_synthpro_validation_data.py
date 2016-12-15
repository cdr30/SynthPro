#!/usr/bin/env python2.7

"""
Script to calculate "model truth" quantities for use when
benchmarking different gridding/mapping methodologies. 

"""


import argparse
from netCDF4 import Dataset
import os

from synthpro.synthpro import *


class ArgError(Exception):
    pass

def get_args():
    """ Get arguments from command line. """
    parser = argparse.ArgumentParser(
        description='Generates "model truth" data sets for benchmarking of profile mapping methods')
    parser.add_argument(
        'month', type=int, help='Month used in file names.')
    parser.add_argument(
        'year', type=int, help='Year used in file names.')
    parser.add_argument(
        'namelist', type=str, help='Path to namelist.ini')
    parser.add_argument(
        'basins', type=str, help='Path to netcdf file containing basin masks') 
    parser.add_argument(
        'mesh', type=str, help='Path to netcdf file containing ocean mesh information')    
    parser.add_argument(
        '-d', '--day', type=int, help='Day used in file names [def=None].', default=None)
    parser.add_argument(
        '--outdir', type=str, help='Directory to save data [def=./].', default='./')
    parser.add_argument(
        '--bmdi', type=int, help='Missing data indicator for basin masks [def=0]', default=0)
    parser.add_argument(
        '--basinvars', type=str, help=('Space-delimited string of variable names for basin masks '+
        '[def="global n_hemisphere s_hemisphere arctic atlantic indian pacific southern"]'),
        default='global n_hemisphere s_hemisphere arctic atlantic indian pacific southern')
    parser.add_argument(
        '--meshvars', type=str, help='Space-delimited string of variable names for cell dimensions [def="e1t e2t e3t"]',
        default='e1t e2t e3t')
    parser.add_argument(
        '--rhocp', type=float, help='Rho*Cp, constant used for calculation of ocean heat content [def=4091688.0].',
        default=4091688.0)
    parser.add_argument('--layer_thickness', type=float, help='Layer thickness, m, for ocean heat content calculations [def=100].',
        default=100.)
    parser.add_argument('--time_dim', type=str, help='Name of time dimension in input netcdf files[def=time_counter].',
        default='time_counter')
    parser.add_argument('--time_var', type=str, help='Name of time variable in input netcdf files [def=time_counter].',
        default='time_counter')
    parser.add_argument('--depth_dim', type=str, help='Name of depth dimension in input netcdf files [def=deptht].',
        default='deptht')
    parser.add_argument('--depth_var', type=str, help='Name of depth variable in input netcdf files [def=deptht].',
        default='deptht')

    args = parser.parse_args()

    return args


def get_meshvars(args):
    """ Return list of mesh variable names """
    mvars = args.meshvars.split()
    nvars = len(mvars) 
    
    if nvars != 3:
        raise ArgError('"%s" is an invalid argument to meshvars. Try --meshvars "[dxvar] [dyvar] [dzvar]"' 
                       % args.meshvars)
        
    return mvars


def get_basinvars(args):
    """ Return list of basin variable names """
    bvars = args.basinvars.split()
    nvars = len(bvars) 
    if nvars == 0:
        raise ArgError('"%s" is an invalid argument to basinvars. Try --meshvars "basin1 basin2 ..."' 
                       % args.basinvars)
        
    return bvars


def load_var(fname, readFunc, varname):
    """ Load mesh data """
    dat = readFunc(varname, fname)
    
    return np.squeeze(dat)


def load_basinmask(args, modelDat, basinvar):
    """ Load basin mask """
    mask = load_var(args.basins, modelDat.read_var, basinvar)
    mask = mask == args.bmdi
    
    return mask
    

def calc_area_avgs(args, modelDat, dx, dy, bmask):
    """ Calculate area averages on each model level """
    nz = modelDat.data.shape[0]
    avgs = []
    
    for k in range(nz):
        dat = modelDat.data[k]
        dat = np.ma.MaskedArray(dat, mask=(bmask | dat.mask ))
        areas = np.ma.MaskedArray(dx * dy, mask=(bmask | dat.mask))
        avgs.append((dat * areas).sum() / areas.sum()) 
          
    avgs = np.array(avgs)
    avgs = np.ma.MaskedArray(avgs, mask=np.isnan(avgs))
    
    return avgs
    
    
def calc_vol_integrals(args, modelDat, dx, dy, dz, bmask):
    """ Calculate volume integrals on each model level """
    nz = modelDat.data.shape[0]
    vints = []
    
    for k in range(nz):
        dat = modelDat.data[k]
        dat = np.ma.MaskedArray(dat, mask=(bmask | dat.mask ))
        vols = np.ma.MaskedArray(dx * dy * dz[k], mask=(bmask | dat.mask))
        vints.append((dat * vols).sum())
        
    vints = np.array(vints)
    vints = np.ma.MaskedArray(vints, mask=np.isnan(vints))
    
    return vints


def calc_depth_bounds(zthick):
    """ Return depth coordinate bounds calculated from layer thicknesses """
    bounds = []
    
    for k in range(len(zthick)):
        
        if k == 0:
            bounds.append([0, zthick[k]])
            
        else:
            upper = bounds[k-1][1]
            bounds.append([upper, upper + zthick[k]])
            
    return bounds

    
def create_layers(model_dz, layer_dz):
    """ Return layers for ocean heat content calculations """
    zupper = np.arange(np.int(model_dz.sum()/layer_dz) + 1) * layer_dz
    zlower = zupper + layer_dz
    layers = [[zu, zl] for zu,zl in zip(zupper, zlower)]
    
    return layers


def calc_overlap(a, b):
    """ Return range of overlap between two arrays. """
    max_of_mins = max(min(a), min(b))
    min_of_maxs = min(max(a), max(b))     
        
    if max_of_mins >= min_of_maxs:
        overlap_range = None
    else:
        overlap_range = [max_of_mins, min_of_maxs]
        
    return overlap_range


def calc_zfrac(zthick, minz, maxz):
    """
    Return fraction of each vertical level that
    falls within minz and maxz.        
    
    """
    bounds = calc_depth_bounds(zthick)
    zfrac = []
    
    for bound in bounds:
        overlap = calc_overlap(bound, [minz, maxz])
        
        if overlap is not None:
            wt = ( (max(overlap) - min(overlap)) / 
                   (max(bound) - min(bound)) )
        else:
            wt = 0
            
        zfrac.append(wt)
        
    return np.array(zfrac)


def calc_layer_ohc(args, tint, dz):
    """ 
    Calculate ocean heat content within specific layers from 
    volume integrated temperature on each model level. 
    
    """
    zthick = np.apply_over_axes(np.median, dz, [1,2]).squeeze()
    layers = create_layers(zthick, args.layer_thickness)
    layer_ohc = []
    
    for layer in layers:
        wts = calc_zfrac(zthick, layer[0], layer[1])
        layer_ohc.append(np.sum(wts * tint) * args.rhocp)    

    return layers, np.array(layer_ohc)
        

def copy_ncdim(ncin, ncout, dim_name):
    """ Copy dimension from ncin to ncout """
    
    dimin = ncin.dimensions[dim_name]
    dimout = ncout.createDimension(
        dim_name, len(dimin) if not dimin.isunlimited() else None)


def copy_ncvar(ncin, ncout, var_name):
    """ Copy variables from ncin to ncout """
    
    varin = ncin.variables[var_name]
    varout = ncout.createVariable(var_name, varin.dtype, varin.dimensions)
    varout.setncatts( { k: varin.getncattr(k) for k in varin.ncattrs() } )
    varout[:] = varin[:]
    

def create_savename(args, fin, basin, varname):
    """ Create filename for output netcdf """
    outname = fin.split('/')[-1].replace('.nc', '.%s_%s.nc' % (basin, varname))
    outdir = '%s%s/' % (args.outdir, basin)
    fout = outdir + outname
    
    try: 
        os.makedirs(outdir)
    except OSError:
        if not os.path.isdir(outdir):
            raise IOError

    return fout


def write_data_modelz(args, config, varname, basin, dat, units=None):
    """ Write data on model depth levels to netcdf """
    
    # Associate data
    fin = config.get('model_temp', 'file_name')
    ncin = Dataset(fin)
    fout = create_savename(args, fin, basin, varname)
    ncout = Dataset(fout, 'w')
    printmsg.message(config, 'Writing: %s' % fout)
    
    # Copy time and depth variables
    copy_ncdim(ncin, ncout, args.time_dim)
    copy_ncdim(ncin, ncout, args.depth_dim)
    copy_ncvar(ncin, ncout, args.time_var)
    copy_ncvar(ncin, ncout, args.depth_var)
        
    # Add data variable    
    varout = ncout.createVariable(varname, 'float64', (args.time_dim, args.depth_dim))
    varout[:] = dat.reshape((1,len(dat)))
    if units is not None:
        varout.setncatts({'units': units})
    
    # Close files
    ncout.close()
    ncin.close()


def write_data_layers(args, config, varname, basin, layers, dat, units=None):
    """ Write data on specified layers to netcdf """
    
    # Associate data
    fin = config.get('model_temp', 'file_name')
    ncin = Dataset(fin)
    fout = create_savename(args, fin, basin, varname)
    ncout = Dataset(fout, 'w')
    printmsg.message(config, 'Writing: %s' % fout)
    
    # Extract bounds information
    ubounds = np.array([bound[0] for bound in layers])
    lbounds = np.array([bound[1] for bound in layers])
    
    # Copy time and depth variables
    copy_ncdim(ncin, ncout, args.time_dim)
    copy_ncvar(ncin, ncout, args.time_var)
    zDim = ncout.createDimension('layers', len(ubounds))
    
    uzvar = ncout.createVariable('upper_boundary', 'float64', ('layers',))
    uzvar[:] = ubounds
    uzvar.setncatts({'units': 'm'})
    
    lzvar = ncout.createVariable('lower_boundary', 'float64', ('layers',))
    lzvar[:] = lbounds
    lzvar.setncatts({'units': 'm'})
    
    # Add data variable    
    varout = ncout.createVariable(varname, 'float64', (args.time_dim, 'layers'))
    varout[:] = dat.reshape((1,len(dat)))
    if units is not None:
        varout.setncatts({'units': units})
    
    # Close files
    ncout.close()
    ncin.close()                  


if __name__ == '__main__':
    
    # Load arguments
    args = get_args()   
    dxvar, dyvar, dzvar = get_meshvars(args)
    basinvars = get_basinvars(args)
        
    # Build paths to input data files
    config = namelist.get_namelist(args)    
    config = tools.build_file_name(args, config, 'model_temp')
    config = tools.build_file_name(args, config, 'model_sal')
    
    # Load model data
    printmsg.message(config, 'Loading input data...')
    modelTemp = model.assoc_model(config, 'model_temp')
    modelSal = model.assoc_model(config, 'model_sal')

    # Load mesh data
    dx = load_var(args.mesh, modelTemp.read_var, dxvar)
    dy = load_var(args.mesh, modelTemp.read_var, dyvar)
    dz = load_var(args.mesh, modelTemp.read_var, dzvar)
    
    # Calculate metrics for each basin
    for basinvar in basinvars:

        printmsg.message(config, 'Calculating %s metrics...' % basinvar)
        bmask = load_basinmask(args, modelTemp, basinvar)
        tavg = calc_area_avgs(args, modelTemp, dx, dy, bmask)
        savg = calc_area_avgs(args, modelSal, dx, dy, bmask)
        tint = calc_vol_integrals(args, modelTemp, dx, dy, dz, bmask)
        sint = calc_vol_integrals(args, modelSal, dx, dy, dz, bmask)
        layers, ohc = calc_layer_ohc(args, tint, dz)
        
        printmsg.message(config, 'Saving %s metrics...' % basinvar)
        write_data_modelz(args, config, 'area_avg_temperature', basinvar, tavg, units='C')
        write_data_modelz(args, config, 'area_avg_salinity', basinvar, savg, units='psu')
        write_data_modelz(args, config, 'vol_integrated_temperature', basinvar, tint, units='C*m3')
        write_data_modelz(args, config, 'vol_integrated_salinity', basinvar, sint, units='psu*m3')
        write_data_layers(args, config, 'ocean_heat_content', basinvar, layers, ohc, units='J')



        