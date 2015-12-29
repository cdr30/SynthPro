#!/usr/local/sci/bin/python2.7
"""
Script to visualize synthetic profile data generated
from EN4 observational profiles.

"""

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset


def load_profile_data(f, var, qcvar=None, reject='4'):
    """
    Return profile data following application of QC.
    
    """
    ncf = Dataset(f)
    dat = ncf.variables[var][:]
    
    if qcvar is not None:
        pos_qc = np.array(ncf.variables['POSITION_QC'][:])
        dat_qc = np.array(ncf.variables[qcvar][:])

        pos_qc = pos_qc != reject
        dat_qc = return_1d_qc(dat_qc, reject=reject)
        qc_ind = np.where(pos_qc & dat_qc)
        dat = dat[qc_ind]
        
    return dat


def return_1d_qc(dat_qc, reject='4'):
    """
    For each profile, return values of True (accept)
    or False (reject).
    
    """
    nqs = np.arange(dat_qc.shape[0])
    qc_out = []
    
    for nq in nqs:
        if any(dat_qc[nq] == reject):
            qc_out.append(False)
        else:
            qc_out.append(True)
    
    return np.array(qc_out)
    

### Define variable names
tvar = 'POTM_CORRECTED'
svar = 'PSAL_CORRECTED'
zvar = 'DEPH_CORRECTED'
qcvar_t = 'POTM_CORRECTED_QC'
qcvar_s = 'PSAL_CORRECTED_QC'
yr, mon = 2010, 1


### File locations
obsf = '/tmp/EN.4.1.1.f.profiles.g10.%4i%02i.nc' % (yr, mon)
synf = '/tmp/EN.4.1.1.f.profiles.synthetic.%4i%02i.nc' % (yr, mon)
synf_fd = '/tmp/EN.4.1.1.f.profiles.synthetic_full_depth.%4i%02i.nc' % (yr, mon)


### Load data
tobs = load_profile_data(obsf, tvar, qcvar=qcvar_t)
tsyn = load_profile_data(synf, tvar, qcvar=qcvar_t)
tsyn_fd = load_profile_data(synf_fd, tvar, qcvar=qcvar_t)

sobs = load_profile_data(obsf, svar, qcvar=qcvar_s)
ssyn = load_profile_data(synf, svar, qcvar=qcvar_s)
ssyn_fd = load_profile_data(synf_fd, svar, qcvar=qcvar_s)

zobs = load_profile_data(obsf, zvar, qcvar=qcvar_t)
zsyn = load_profile_data(synf, zvar, qcvar=qcvar_t)
zsyn_fd = load_profile_data(synf_fd, zvar, qcvar=qcvar_t)

zobs_s = load_profile_data(obsf, zvar, qcvar=qcvar_s)
zsyn_s = load_profile_data(synf, zvar, qcvar=qcvar_s)
zsyn_s_fd = load_profile_data(synf_fd, zvar, qcvar=qcvar_s)


### Plot observations vs synthetic temperature data
plt.figure()
plt.plot(tobs.reshape(tobs.size), tsyn.reshape(tsyn.size), 'xr')
plt.xlabel('Observed T')
plt.ylabel('Synthetic T')
plt.show()
### Plot observed temperatures against depth
plt.figure()
plt.plot(tobs.reshape(zobs.size), -zobs.reshape(zobs.size), 'xr')
plt.xlabel('Observed T')
plt.ylabel('Depth')
plt.show()

### Plot synthetic temperatures against depth
plt.figure()
plt.plot(tsyn.reshape(tsyn.size), -zsyn.reshape(zsyn.size), 'xr')
plt.xlabel('Synthetic T')
plt.ylabel('Depth')
plt.show()

### Plot observed salinity against depth
plt.plot(sobs.reshape(sobs.size), -zobs_s.reshape(zobs_s.size), 'xr')
plt.xlabel('Observed S')
plt.ylabel('Depth')
plt.show()

### Plot synthetic salinity against depth
plt.plot(ssyn.reshape(ssyn.size), -zsyn_s.reshape(zsyn_s.size), 'xr')
plt.xlabel('Synthetic S')
plt.ylabel('Depth')
plt.show()


