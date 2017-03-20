"""Unit tests for IDTxl multivariate spectral TE module.

@author: edoardo, patricia
"""
import os
import h5py
import pickle
import numpy as np
# import scipy.fftpack
from idtxl.data import Data
from idtxl.multivariate_te import Multivariate_te
from idtxl.multivariate_spectral_te import Multivariate_spectral_te
import idtxl.idtxl_utils as utils

# from idtxl.stats import _generate_spectral_surrogates
# from idtxl.stats import _generate_surrogates
# from idtxl.bivariate_te import Bivariate_te
# from idtxl.network_analysis import Network_analysis
# from idtxl import visualise_graph
# from idtxl import ft2idtxl
# import idtxl.visualise_graph as vis

# Load test data: simple sine wave coupled with an AR process with a delay of
# 3 samples (source 0 drives  process 1)
f = h5py.File(os.path.join(os.path.dirname(__file__),
              'data/spect.mat'))
dataf = f.get('data_spectral')
data = np.array(dataf).T
d1 = Data(data, dim_order='psr')

# # Plot power spectrum
# N = 1000
# T = 1.0 / 1000
# x = np.linspace(0.0, N * T, N)
# yf = scipy.fftpack.fft(d1._data[0, :, 0])
# xf = np.linspace(0.0, 1.0 / (2.0 * T), N / 2)
# fig, ax = plt.subplots()
# plt.plot(xf, 2.0 / N * np.abs(yf[:N // 2]))
# plt.xlim(0, 20)
# plt.show()

# different simulations that are in data.py
# d_spectral=Data()
# d_spectral.generate_faes_data(1000,10)
# d_spectral.generate_spectral_data(1000,10)

analysis_opts = {'cmi_calc_name': 'jidt_kraskov',
                 'n_perm_max_stat': 30,
                 'n_perm_min_stat': 30,
                 'n_perm_omnibus': 30,
                 'n_perm_max_seq': 30
                 }
target = 1
sources = [0, 2]
network_analysis = Multivariate_te(max_lag_target=5, max_lag_sources=4,
                                   options=analysis_opts, min_lag_sources=1)
res = network_analysis.analyse_single_target(d1, target, sources)
utils.print_dict(res)


spectral_opts = {'cmi_calc_name': 'jidt_kraskov',
                 'n_perm_spec': 10,
                 'alpha_spec': 0.11,
                 'permute_in_time': True,
                 'perm_type': 'random'}
spectral_analysis = Multivariate_spectral_te(spectral_opts)

# [pvalue,
#  sign,
#  te_distr,
#  reconstructed] = spectral_analysis.analyse_single_target(res, d1, 7)
# from scipy import io
# io.savemat('C:/Users/pc/Documents/Uni_frankfurt/spectral_te/test_spectral/reconstructed',dict(x=reconstructed[0][0][100], y=d1._data))

# plt.hist(te_distr[0])
# plt.show()

max_scale = 11  # scale of finterest = 7
pvalue = []
sign = []
te_distr = []
reconstructed = []
for s in range(1, max_scale):
    # returns pvalue, significance, te_surrogate, surrogate
    [p, s, te_surr, r,
     te_surr_temp] = spectral_analysis.analyse_single_target(res, d1, s)
    pvalue.append(p)
    sign.append(s)
    te_distr.append(te_surr)
    reconstructed.append(r)

path = '/home/patriciaw/repos/IDTxl/dev/test_spectral_te/'
with open(path + 'pvalues.txt', 'wb') as fp:
    pickle.dump(pvalue, fp)
with open(path + 'sign.txt', 'wb') as fp:
    pickle.dump(sign, fp)
with open(path + 'te_distr.txt', 'wb') as fp:
    pickle.dump(te_distr, fp)
with open(path + 'reconstructed_surr.txt', 'wb') as fp:
    pickle.dump(reconstructed, fp)
with open(path + 'te_surr_temp.txt', 'wb') as fp:
    pickle.dump(te_surr_temp, fp)

te_orig = res['selected_sources_te']
with open(path + 'te_orig.txt', 'wb') as fp:
    pickle.dump(te_orig, fp)

# Unpickle with:
# with open("test.txt", "rb") as fp:
#     b = pickle.load(fp)

# plt.hist(te_distr[0][0])
# plt.show()
