"""Estimate multivarate spectral TE.

Note:
    Written for Python 3.4+

@author: edoardo
"""
import numpy as np
from . import stats
from .network_analysis import Network_analysis
from .set_estimator import Estimator_cmi
from .data import Data
from . import modwt
import copy as cp

VERBOSE = True


class Multivariate_spectral_te(Network_analysis):
    """Set up a network analysis using multivariate spectral transfer entropy.

    Set parameters necessary for inference of spectral components of
    multivariate transfer entropy (TE). To perform network inference call
    analyse_network() on an instance of the data class.

    Args:
        options : dict
            parameters for estimator use and statistics:

            - 'cmi_calc_name' - estimator to be used for CMI calculation
              (For estimator options see the respective documentation.)
            - 'n_perm_spec' - number of permutations (default=200)
            - 'alpha_spec' - critical alpha level for statistical significance
              (default=0.05)
            - 'cmi_calc_name' - estimator to be used for CMI calculation
              (For estimator options see the respective documentation.)
            - 'permute_in_time' - force surrogate creation by shuffling
              realisations in time instead of shuffling replications; see
              documentation of Data.permute_samples() for further options
              (default=False)

    """

    # TODO right now 'options' holds all optional params (stats AND estimator).
    # We could split this up by adding the stats options to the analyse_*
    # methods?
    def __init__(self, options):
        # Set estimator in the child class for network inference because the
        # estimated quantity may be different from CMI in other inference
        # algorithms. (Everything else can be done in the parent class.)
        try:
            self.calculator_name = options['cmi_calc_name']
        except KeyError:
            raise KeyError('Calculator name was not specified!')
        self._cmi_calculator = Estimator_cmi(self.calculator_name)
        self.n_permutations = options.get('n_perm_spec', 200)
        self.perm_type = options.get('perm_type', 'random')
        self.alpha = options.get('alpha_spec', 0.05)
        self.tail = options.get('tail', 'two')
        super().__init__(options)

    def analyse_network(self, res_network, data, targets='all', sources='all'):
        """Find multivariate spectral transfer entropy between all nodes.

        Estimate multivariate transfer entropy (TE) between all nodes in the
        network or between selected sources and targets.

        Example:

            >>> dat = Data()
            >>> dat.generate_mute_data(100, 5)
            >>> max_lag = 5
            >>> min_lag = 4
            >>> analysis_opts = {
            >>>     'cmi_calc_name': 'jidt_kraskov',
            >>>     'n_perm_max_stat': 200,
            >>>     'n_perm_min_stat': 200,
            >>>     'n_perm_omnibus': 500,
            >>>     'n_perm_max_seq': 500,
            >>>     }
            >>> network_analysis = Multivariate_te(max_lag, min_lag,
            >>>                                    analysis_opts)
            >>> res = network_analysis.analyse_network(dat)
            >>>
            >>> spectral_opts = {
            >>>     'cmi_calc_name': 'jidt_kraskov',
            >>>     'n_perm_spec': 200,
            >>>     'alpha_spec': 0.05
            >>>     }
            >>> spectral_analysis = Multivariate_spectral_te(spectral_opts)
            >>> res_spec = spectral_analysis.analyse_network(res)

        Note:
            For more details on the estimation of multivariate transfer entropy
            see documentation of class method 'analyse_single_target'.

        Args:
            res_network: dict
                results from multivariate network inference, e.g., using TE
            data : Data instance
                raw data from which the network was inferred
            targets : list of int | 'all' [optinal]
                index of target processes (default='all')
            sources : list of int | list of list | 'all' [optional]
                indices of source processes for each target (default='all');
                if 'all', all identified sources in the network are tested for
                spectral TE;
                if list of int, sources specified in the list are tested for
                each target;
                if list of list, sources specified in each inner list are
                tested for the corresponding target

        Returns:
            dict
                results consisting of

                - TODO to be specified ...

                for each target
        """
        # TODO see Multivariate_te.analyse_network()
        return 1

    def analyse_single_target(self, res_target, data, scale, sources='all'):
        """Find multivariate spectral transfer entropy into a target.

        Test multivariate spectral transfer entropy (TE) between all source
        identified using multivariate TE and a target:

        (1) take one relevant variable s
        (2) perform a maximal overlap discrete wavelet transform (MODWT)
        (3) destroy information carried by a single frequency band by
            scrambling the coefficients in the respective scale
        (4) perform the inverse of the MODWT, iMODWT, to get back the time-
            domain representation of the variable
        (5) calculate multivariate TE between s and the target, conditional on
            all other relevant sources
        (6) repeat (3) to (5) n_perm number of times to build a test
            distribution
        (7) test original multivariate TE against the test distribution

        Example:

            >>> dat = Data()
            >>> dat.generate_mute_data(100, 5)
            >>> max_lag = 5
            >>> min_lag = 4
            >>> analysis_opts = {
            >>>     'cmi_calc_name': 'jidt_kraskov',
            >>>     'n_perm_max_stat': 200,
            >>>     'n_perm_min_stat': 200,
            >>>     'n_perm_omnibus': 500,
            >>>     'n_perm_max_seq': 500,
            >>>     }
            >>> target = 0
            >>> sources = [1, 2, 3]
            >>> network_analysis = Multivariate_te(max_lag, min_lag,
            >>>                                    analysis_opts)
            >>> res = network_analysis.analyse_single_target(dat, target,
            >>>                                              sources)
            >>>
            >>> spectral_opts = {
            >>>     'cmi_calc_name': 'jidt_kraskov',
            >>>     'n_perm_spec': 200,
            >>>     'alpha_spec': 0.05
            >>>     }
            >>> spectral_analysis = Multivariate_spectral_te(spectral_opts)
            >>> res_spec = spectral_analysis.analyse_single_target(res, dat)

            Note:
            For more details on the estimation of multivariate transfer entropy
            see documentation of class method 'analyse_single_target'.

            Args:
            res_target: dict
                results from multivariate network inference, e.g., using TE
            data : Data instance
                raw data from which the network was inferred
            scale : int
                scale to be tested (1-indexed)
            sources : list of int | 'all' [optional]
                list of source indices to be tested for the target, if 'all'
                all identified sources in res_target will be tested 
                (default='all')

        Returns:
            dict
                results consisting of sets of selected variables as (full, from
                sources only, from target only), pvalues and TE for each
                significant source variable, the current value for this
                analysis, results for omnibus test (joint influence of all
                selected source variables on the target, omnibus TE, p-value,
                and significance); NOTE that all variables are listed as tuples
                (process, lag wrt. current value)
        """
        n_samples = data.n_samples
        n_repl = data.n_replications
        current_value = res_target['current_value']  # use current value from previous multivar. TE analysis

        max_scale = int(np.round(np.log2(n_samples)))
        assert (scale <= max_scale), (
            'scale ({0}) must be smaller or equal to max_scale'
            ' ({1}).'.format(scale, max_scale))
        if VERBOSE:
            print('Max. scale is {0}'.format(max_scale))

        # wavelet used for modwt
        mother_wavelet = 'db16'

        # Convert lags in the results structure to absolute indices
        idx_list_sources = self._lag_to_idx(
                    lag_list=res_target['selected_vars_sources'],
                    current_value_sample=current_value[1])

        conditioning_set = self._lag_to_idx(
            lag_list=res_target['selected_vars_full'],
            current_value_sample=current_value[1])

        # idx_list_sources[(0,1),(0,2),(1,1),(1,2),(1,3)]
        # unique_sources=np.unique([x[0] for x in idx_list_sources])

        pvalue = []
        significance = []
        te_surrogate = [[] for i in range(len(idx_list_sources))]
        surrogate = [[] for i in range(len(idx_list_sources))]
        cur_val_realisations = data.get_realisations(current_value,
                                                     [current_value])[0]
        # Main algorithm.
        count = 0
        for source in idx_list_sources:
            process = source[0]            
            print('testing {0} from source set {1}'.format(
                    self._idx_to_lag([source], current_value[1])[0],
                    self._idx_to_lag(idx_list_sources, current_value[1])[0]), 
                  end='')
            """
            Modwt coefficients at level j are associated to the same nominal
            frequency band |f|=[1/2.^j+1,1/2.^j]
            A.Walden "Wavelet Analysis of Discrete Time Series"

            i.e 1000 Hz signal
            at scale 4
             ([1/2.^5,1/2.^4])*1000= [31.25 Hz 62.5 Hz]  #gamma band
            at scale 5
            ([1/2.^6,1/2.^5])*1000= [15.62 Hz 31.25 Hz]  #beta band
            at scale 6
            ([1/2.^7,1/2.^6])*1000= [7.81 Hz 15.62 Hz]   # alpha band
            at scale 7
             ([1/2.^7,1/2.^6])*1000= [3.9 Hz 7.81 Hz]   # theta band
            """
            # w_storage_d = []
            storage1_d = np.asarray(np.zeros((max_scale + 1, 
                                              n_samples, 
                                              n_repl)))
            data_slice = data._get_data_slice(process)[0]

            for rep in range(0, n_repl):
                """
                w_transform contains  wavelet coefficients.
                """

                w_transform = modwt.Modwt(data_slice[:, rep],
                                          mother_wavelet,
                                          max_scale)
                # w_storage_d.append(w_transform)
                storage1_d[:, :, rep] = w_transform

            
            '''
            from 1 to max_scale = detailed wavelet coefficient (the ones we
            shuffle) last index contain average coefficient, we keep this only
            for later reconstruction example= for max_scale=10 we have 10
            detailed coeff + one average

            '''
            # for i in range(0, n_repl):
            #     storage1_d[:, :, i] = np.asarray(w_storage_d[i][:, :])

            # plt.figure()

            # for i in range(1,n_level+1):

            #   plt.subplot(n_level,1,i)
            #   plt.plot(storage1_d[i-1,:])

            #   plt.xlabel('n_samples')
            # plt.show()
            # plt.suptitle('wavelet coefficients at each scale $w_{j}$ '
            #              'produced by the MODWT')

            # Store wavelet coeff as 3d object for all replication of a given 
            # source: processes represent scales, samples represent coeffs.
            wav_stored = Data(storage1_d, dim_order='psr', normalise=False)
            # Create surrogates by shuffling coefficients in given scale.
            spectral_surr = stats._get_spectral_surrogates(
                                                       wav_stored,
                                                       scale - 1,
                                                       self.n_permutations,
                                                       perm_opts=self.options)
            # number replication*n_samples*n_permutation
            
            # Get the conditioning set for current source to be tested and its
            # realisations (can be reused over permutations).
            cur_cond_set = cp.copy(conditioning_set)
            cur_cond_set.pop(cur_cond_set.index(source))
            cur_cond_set_realisations = data.get_realisations(
                                                        current_value,
                                                        cur_cond_set)[0]
            #conditioning_set_list = conditioning_set.pop(
            #                                conditioning_set.index(source))  # this is outside loop because at each permutation it tries to remove the same source            
            # Get distribution of surrogate TE values.            
            te_surr = np.zeros(self.n_permutations)
            surrog = []
            for perm in range(0, self.n_permutations):
                if VERBOSE:
                    print('permutation: {0} of {1}.'.format(
                                                        perm, 
                                                        self.n_permutations))
                # Replace coefficients of scale to be tested by shuffled 
                # coefficients to destroy influence of this freq. band.
                wav_stored._data[scale - 1, :, :] = spectral_surr[:, :, perm]
                reconstructed = np.empty((n_repl, n_samples))                
                # original = np.empty((n_repl, n_samples))
                
                # Reconstruct the signal from all scales, with shuffled 
                # coefficients for the scale to be tested.
                for inv in range(0, n_repl):
                    merged_coeff = wav_stored._data[:, :, inv]
                    # apply inverse modwt transform to reconstruct it
                    reconstructed[inv, :] = modwt.Imodwt(merged_coeff,
                                                         mother_wavelet)
                    # original[inv, :] = pywt.iswt(w_transform, mother_wavelet)
                surrog.append(reconstructed)  # for debugging
                
                # Create surrogate data object and add the reconstructed
                # shuffled time series.
                # Check error of reconstruction with original coeff with
                # L-infinty norm.                
                d_temp = cp.copy(data.data)
                # transp = reconstructed.T
                # transp = original.T
                # resp_const = np.reshape(transp, (1, n_samples, n_repl))
                # d_temp[series, :, :] = resp_const
                d_temp[process, :, :] = reconstructed.T
                data_surr = Data(d_temp, 'psr', normalise=False)  # TODO make the data output optional      
                #self.current_value = res_target['current_value']
                # Get the realisations of the current source from the surrogate
                # data (with the shuffled coefficient)
#                cur_val_realisations = data_surr.get_realisations(
#                                                    self.current_value,
#                                                    [self.current_value])
#                cur_source_realisations = data_surr.get_realisations(
#                                                    self.current_value,
#                                                    [process])
#                conditioning_set_realisations = data_surr.get_realisations(
#                                                    self.current_value,
#                                                    [conditioning_set_list])
                
                # TODO the following can be parallelized
                # Compute TE between shuffled source and current_value 
                # conditional on the remaining set. Get the current source's
                # realisations from the surrogate data object, get realisations
                # of all other variables from the original data object.
                cur_source_realisations = data_surr.get_realisations(
                                                    current_value,
                                                    [source])[0]                
                te_surr[perm] = self._cmi_calculator.estimate(
                                        var1=cur_val_realisations,
                                        var2=cur_source_realisations,
                                        conditional=cur_cond_set_realisations,
                                        opts=self.options)

            # Calculate p-value for original TE against spectral surrogates.
            te_original = res_target['selected_sources_te'][count]
            [sign, pval] = stats._find_pvalue(statistic=te_original, 
                                              distribution=te_surr, 
                                              alpha=self.alpha,
                                              tail='one')

            te_surrogate[count].append(te_surr)
            surrogate[count].append(surrog)
            pvalue.append(pval)
            significance.append(sign)
            # new methods in class Data():
            # dat._get_data_slice
            # dat.slice_permute_samples
            # dat.slice_permute_replications
            # new method in module stats:
            # stats._generate_spectral_surrogates
            count += 1

        return pvalue, significance, te_surrogate, surrogate
