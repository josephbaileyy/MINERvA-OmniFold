import ROOT
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
import pickle
import os
from array import array

class OmniFold_helper_functions:
    def TH1_to_numpy(hist):
        num_bins = hist.GetNbinsX()
        hist_counts = np.empty(num_bins)
        bin_centers = np.empty(num_bins)
        bin_widths = np.empty(num_bins)
        for i in range(num_bins):
            hist_counts[i] = hist.GetBinContent(i+1)
            bin_centers[i] = hist.GetBinCenter(i+1)
            bin_widths[i] = hist.GetBinWidth(i+1)
        return hist_counts, bin_centers, bin_widths

    def TH2_to_numpy(hist):
        num_X_bins = hist.GetNbinsX()
        num_Y_bins = hist.GetNbinsY()
        hist_counts = np.empty(shape=(num_X_bins, num_Y_bins))
        bin_centers = np.empty(shape=(num_X_bins, num_Y_bins), dtype=object)
        bin_widths = np.empty(shape=(num_X_bins, num_Y_bins), dtype=object)
        for i in range(num_X_bins):
            for j in range(num_Y_bins):
                hist_counts[i, j] = hist.GetBinContent(i+1, j+1)
                bin_center_tuple = (hist.GetXaxis().GetBinCenter(i+1), hist.GetYaxis().GetBinCenter(j+1))
                bin_centers[i, j] = bin_center_tuple
                bin_width_tuple = (hist.GetXaxis().GetBinWidth(i+1), hist.GetYaxis().GetBinWidth(j+1))
                bin_widths[i, j] = bin_width_tuple
        return hist_counts, bin_centers, bin_widths

    def prepare_hist_data(counts, bin_centers, bin_widths):
        out_array = np.empty(shape=(int(np.sum(counts)), 1))
        out_weights = np.empty(shape=(int(np.sum(counts)), 1))
        entry_tracker = 0
        for (count, bin_center, bin_width) in zip(counts, bin_centers, bin_widths):
            out_array[entry_tracker:int(entry_tracker+count)] = bin_center
            out_weights[entry_tracker:int(entry_tracker+count)] = bin_width
            entry_tracker += int(count)
        return out_array, out_weights

    def prepare_response_data(counts, bin_centers, bin_widths):
        MCgen_array = np.empty(shape=(int(np.sum(counts)), 1))
        MCreco_array = np.empty(shape=(int(np.sum(counts)), 1))
        MCgen_weights = np.empty(shape=(int(np.sum(counts)), 1))
        MCreco_weights = np.empty(shape=(int(np.sum(counts)), 1))
        entry_tracker = 0
        for (count, bin_center, bin_width) in zip(counts, bin_centers, bin_widths):
            MCreco_array[entry_tracker:int(entry_tracker+count)] = bin_center[0]
            MCgen_array[entry_tracker:int(entry_tracker+count)] = bin_center[1]
            MCreco_weights[entry_tracker:int(entry_tracker+count)] = bin_width[0]
            MCgen_weights[entry_tracker:int(entry_tracker+count)] = bin_width[1]
            entry_tracker += int(count)
        return MCgen_array, MCreco_array, MCgen_weights, MCreco_weights

    def convert_to_TVectorD(array):
        vector = ROOT.TVectorD(len(array))
        for i, entry in enumerate(array):
            vector[i] = entry
        return vector

    def get_vectors(array):
        vector_list = []
        for entry in array:
            vector = OmniFold_helper_functions.convert_to_TVectorD(entry)
            vector_list.append(vector)
        return vector_list

    def reweight(events, classifier):
        class_probabilities = classifier.predict_proba(events)
        data_probability = class_probabilities[:,1]
        # divide by 0 symmetrical fix
        #weights = data_probability / (1. - data_probability)
        p_safe = np.clip(data_probability, 1e-6, 1-1e-6)
        weights = p_safe / (1. - p_safe)
        return np.squeeze(np.nan_to_num(weights))

    def omnifold(
            MCgen_entries,
            MCreco_entries,
            measured_entries,
            MC_pass_reco_mask,
            MC_pass_truth_mask,
            measured_pass_reco_mask,
            num_iterations,
            MCgen_weights = None,
            MCreco_weights = None,
            measured_weights = None,
            model_save_dict = None,
            classifier1_params = None,
            classifier2_params = None,
            regressor_params = None,
            parameter_format = "TMap",
            estimator = "exact",
            device = "cpu",
        ):
        # Removing events that don't pass generation level cuts
        MCreco_entries = MCreco_entries[MC_pass_truth_mask]
        MCgen_entries = MCgen_entries[MC_pass_truth_mask]
        MC_pass_reco_mask = MC_pass_reco_mask[MC_pass_truth_mask]
        if MCgen_weights is not None:
            MCgen_weights = MCgen_weights[MC_pass_truth_mask]
        else:
            MCgen_weights = np.ones(len(MCgen_entries))
        if MCreco_weights is not None:
            MCreco_weights = MCreco_weights[MC_pass_truth_mask]
        else:
            MCreco_weights = np.ones(len(MCreco_entries))
        if measured_weights is None:
            measured_weights = np.ones(len(measured_entries))
        
        measured_labels = np.ones(len(measured_entries[measured_pass_reco_mask]))
        MC_labels = np.zeros(len(MCgen_entries))

        weights_pull = np.ones(len(MCgen_entries))
        weights_push = np.ones(len(MCgen_entries))

        # Converting the TMap strings to the proper types
        def convert_to_dict(dict):
            params = {}
            for key, value in dict.items():
                if any(char.isdigit() for char in value):
                    number = float(value)
                    if number.is_integer():
                        number = int(number)
                    params[key] = number
                elif value == "True" or value == "False":
                    params[key] = bool(value)
                elif value == "None":
                    params[key] = None
                else:
                    params[key] = value
            return params
        if classifier1_params is not None:
            if parameter_format == "TMap":
                classifier1_params = convert_to_dict(classifier1_params)
        else:
            classifier1_params = {}

        if classifier2_params is not None:
            if parameter_format == "TMap":
                classifier2_params = convert_to_dict(classifier2_params)
        else:
            classifier2_params = {}

        if regressor_params is not None:
            if parameter_format == "TMap":
                regressor_params = convert_to_dict(regressor_params)
        else:
            regressor_params = {}
        # estimator="exact": original sklearn GradientBoosting{Classifier,Regressor}
        #   — exact-split CART, single-threaded, O(events) per split.
        # estimator="hist":  HistGradientBoosting{Classifier,Regressor}
        #   — histogram-binned (256 bins/feature), OpenMP-parallel, O(bins)
        #   per split. Typically 10-30x faster on >1M-row tabular data with
        #   the same gradient-boosting semantics. Default param mapping
        #   below preserves parity with the exact path (100 trees, depth 3
        #   ≈ 8 leaves, learning_rate=0.1). Any caller-supplied param dict
        #   takes precedence over these defaults.
        if estimator == "exact":
            step1_classifier = GradientBoostingClassifier(**classifier1_params)
            step2_classifier = GradientBoostingClassifier(**classifier2_params)
            use_regressor =  any(~MC_pass_reco_mask)
            if use_regressor:
                step1_regressor = GradientBoostingRegressor(**regressor_params)
        elif estimator == "hist":
            hist_defaults = dict(max_iter=100, max_leaf_nodes=8,
                                 learning_rate=0.1)
            c1 = {**hist_defaults, **classifier1_params}
            c2 = {**hist_defaults, **classifier2_params}
            rg = {**hist_defaults, **regressor_params}
            step1_classifier = HistGradientBoostingClassifier(**c1)
            step2_classifier = HistGradientBoostingClassifier(**c2)
            use_regressor =  any(~MC_pass_reco_mask)
            if use_regressor:
                step1_regressor = HistGradientBoostingRegressor(**rg)
        elif estimator == "xgb":
            # XGBoost histogram trees (tree_method="hist"). On CPU: typically
            # 1.5-3x faster than sklearn HistGBT thanks to better thread
            # scheduling. On GPU: pass device="cuda"; the per-tree work moves
            # to the device, host-device transfer is the bottleneck for d<=2,
            # so GPU only wins at higher feature dimensions.
            from xgboost import XGBClassifier, XGBRegressor
            xgb_defaults = dict(n_estimators=100, max_depth=3,
                                learning_rate=0.1, tree_method="hist",
                                device=device)
            c1 = {**xgb_defaults, **classifier1_params}
            c2 = {**xgb_defaults, **classifier2_params}
            rg = {**xgb_defaults, **regressor_params}
            step1_classifier = XGBClassifier(**c1)
            step2_classifier = XGBClassifier(**c2)
            use_regressor =  any(~MC_pass_reco_mask)
            if use_regressor:
                step1_regressor = XGBRegressor(**rg)
        elif estimator == "lgbm":
            # LightGBM leaf-wise growth — usually fastest CPU GBDT at this
            # data shape. GPU build requires lightgbm compiled with OpenCL
            # or CUDA support; default conda wheels are CPU-only. We pass
            # device="gpu" only when the caller requests cuda/gpu.
            from lightgbm import LGBMClassifier, LGBMRegressor
            lgbm_defaults = dict(n_estimators=100, num_leaves=8,
                                 learning_rate=0.1, verbose=-1)
            if device != "cpu":
                lgbm_defaults["device"] = "gpu"
            c1 = {**lgbm_defaults, **classifier1_params}
            c2 = {**lgbm_defaults, **classifier2_params}
            rg = {**lgbm_defaults, **regressor_params}
            step1_classifier = LGBMClassifier(**c1)
            step2_classifier = LGBMClassifier(**c2)
            use_regressor =  any(~MC_pass_reco_mask)
            if use_regressor:
                step1_regressor = LGBMRegressor(**rg)
        else:
            raise ValueError(
                f"Unknown estimator='{estimator}'. "
                "Expected one of: 'exact', 'hist', 'xgb', 'lgbm'.")
        
        for i in range(num_iterations):
            print(f"Starting iteration {i}") 
            step1_data = np.concatenate((MCreco_entries[MC_pass_reco_mask], measured_entries[measured_pass_reco_mask]))
            step1_labels = np.concatenate((np.zeros(len(MCreco_entries[MC_pass_reco_mask])), measured_labels))
            step1_weights = np.concatenate(
                (weights_push[MC_pass_reco_mask]*MCreco_weights[MC_pass_reco_mask], 
                np.ones(len(measured_entries[measured_pass_reco_mask]))*measured_weights[measured_pass_reco_mask])
            )
            
            # Training step 1 classifier and getting weights
            step1_classifier.fit(step1_data, step1_labels, sample_weight = step1_weights)
            new_weights = np.ones_like(weights_pull)
            new_weights[MC_pass_reco_mask] = OmniFold_helper_functions.reweight(MCreco_entries[MC_pass_reco_mask], step1_classifier)
            
            # Training a regression model to predict the weights of the events that don't pass reconstruction
            if use_regressor:
                step1_regressor.fit(MCgen_entries[MC_pass_reco_mask], new_weights[MC_pass_reco_mask])
                new_weights[~MC_pass_reco_mask] = step1_regressor.predict(MCgen_entries[~MC_pass_reco_mask])
            weights_pull = np.multiply(weights_push, new_weights)
                
            # Training step 2 classifier
            step2_data = np.concatenate((MCgen_entries, MCgen_entries))
            step2_labels = np.concatenate((MC_labels, np.ones(len(MCgen_entries))))
            step2_weights = np.concatenate((np.ones(len(MCgen_entries))*MCgen_weights, weights_pull*MCgen_weights))
            step2_classifier.fit(step2_data, step2_labels, sample_weight = step2_weights)

            # Getting step 2 weights and storing iteration weights
            weights_push = OmniFold_helper_functions.reweight(MCgen_entries, step2_classifier)

            if model_save_dict is not None and model_save_dict['save_models']:
                base_path = model_save_dict['save_dir']
                if not os.path.exists(base_path):
                    print(f"Path {base_path} not found. Creating it.")
                    os.makedirs(base_path, exist_ok=True)

                model_name = f"{model_save_dict['model_save_name']}_iteration_{i}.pkl"
                file_path = os.path.join(base_path, model_name)

                models_to_save = {
                    "step1_classifier": step1_classifier,
                    "step2_classifier": step2_classifier
                }
                if use_regressor:
                    models_to_save["step1_regressor"] = step1_regressor

                with open(file_path, "wb") as outfile:
                    pickle.dump(models_to_save, outfile)
                print(f"Saved models for iteration {i} to {file_path}")

        return weights_pull, weights_push


    def binned_omnifold(response_hist, measured_hist, num_iterations, use_density):
        measured_counts, measured_bin_centers, measured_bin_widths = OmniFold_helper_functions.TH1_to_numpy(measured_hist)
        response_counts, response_bin_centers, response_bin_widths = OmniFold_helper_functions.TH2_to_numpy(response_hist)
        MCgen_entries, MCreco_entries, MCgen_weights, MCreco_weights = OmniFold_helper_functions.prepare_response_data(response_counts.flatten(), response_bin_centers.flatten(), response_bin_widths.flatten())
        measured_entries, measured_weights = OmniFold_helper_functions.prepare_hist_data(measured_counts, measured_bin_centers, measured_bin_widths)
        if not use_density:
            MCgen_weights = np.ones_like(MCgen_weights)
            MCreco_weights = np.ones_like(MCreco_weights)
            measured_weights = np.ones_like(measured_weights)
        MC_pass_reco_mask = np.full(MCgen_entries.shape[0], True)
        MC_pass_truth_mask = np.full(MCreco_entries.shape[0], True)
        measured_pass_reco_mask = np.full(measured_entries.shape[0], True)
        _, step2_weights = OmniFold_helper_functions.omnifold(MCgen_entries,
                                    MCreco_entries,
                                    measured_entries,
                                    MC_pass_reco_mask,
                                    MC_pass_truth_mask,
                                    measured_pass_reco_mask,
                                    num_iterations,
                                    MCgen_weights = MCgen_weights.flatten(),
                                    MCreco_weights = MCreco_weights.flatten(),
                                    measured_weights = measured_weights.flatten())
        truth_axis = response_hist.GetYaxis()
        truth_edges = [truth_axis.GetBinLowEdge(1)]
        for i in range(1, response_hist.GetNbinsY() + 1):
            truth_edges.append(truth_axis.GetBinUpEdge(i))
        unfolded_hist = ROOT.TH1D(
                                "unfolded_hist",
                                "unfolded_hist",
                                response_hist.GetNbinsY(),
                                array("d", truth_edges)
                                )
        unfolded_hist.Sumw2()
        unfolded_hist.SetDirectory(0)
        for (weight, MC) in zip(step2_weights, MCgen_entries.flatten()):
            unfolded_hist.Fill(MC, weight)


        return unfolded_hist
    def unbinned_omnifold(
            MCgen_entries,
            MCreco_entries,
            measured_entries,
            num_iterations,
            MC_pass_reco_mask = None,
            MC_pass_truth_mask = None,
            measured_pass_reco_mask = None,
            MCgen_weights = None,
            MCreco_weights = None,
            measured_weights = None,
            model_save_dict = None,
            classifier1_params=None,
            classifier2_params=None,
            regressor_params=None,
            parameter_format = "TMap",
            estimator = "exact",
            device = "cpu",
        ):
        if MCgen_entries.ndim == 1:
            MCgen_entries = np.expand_dims(MCgen_entries, axis = 1)
        if MCreco_entries.ndim == 1:
            MCreco_entries = np.expand_dims(MCreco_entries, axis = 1)
        if measured_entries.ndim == 1:
            measured_entries = np.expand_dims(measured_entries, axis = 1)
        if MC_pass_reco_mask is None:
            MC_pass_reco_mask = np.full(MCgen_entries.shape[0], True, dtype=bool)
        if MC_pass_truth_mask is None:
            MC_pass_truth_mask = np.full(MCgen_entries.shape[0], True, dtype=bool)
        if measured_pass_reco_mask is None:
            measured_pass_reco_mask = np.full(measured_entries.shape[0], True, dtype=bool)
        return OmniFold_helper_functions.omnifold(
            MCgen_entries,
            MCreco_entries,
            measured_entries,
            MC_pass_reco_mask,
            MC_pass_truth_mask,
            measured_pass_reco_mask,
            num_iterations,
            MCgen_weights,
            MCreco_weights,
            measured_weights,
            model_save_dict,
            classifier1_params,
            classifier2_params,
            regressor_params,
            parameter_format,
            estimator,
            device,
        )

    def get_step1_predictions(MCgen_data, MCreco_data, path_to_model, pass_reco = None):
        file = path_to_model
        if os.path.isfile(file):
            print(f"Opening {file} for step 1 predictions.")
        else:
            raise ValueError(f"{file} does not exist! Please input a valid model .pkl path through SetLoadModelPath().")
        with open(file, "rb") as infile:
            loaded_models = pickle.load(infile)

        if MCgen_data.ndim == 1:
            MCgen_data = np.expand_dims(MCgen_data, axis = 1)
        if MCreco_data.ndim == 1:
            MCreco_data = np.expand_dims(MCreco_data, axis = 1)
        
        step1_test_weights = np.ones(len(MCreco_data))
        if pass_reco is None or len(pass_reco)==0:
            pass_reco = np.full_like(step1_test_weights, True, dtype=bool)
        step1_test_weights[pass_reco] = OmniFold_helper_functions.reweight(MCreco_data[pass_reco], loaded_models['step1_classifier'])
        if any(~pass_reco):
            step1_test_weights[~pass_reco] = loaded_models['step1_regressor'].predict(MCgen_data[~pass_reco])
        return step1_test_weights

    def get_step2_predictions(MCgen_data, path_to_model):
        file = path_to_model
        if os.path.isfile(file):
            print(f"Opening {file} for step 2 predictions.")
        else:
            raise ValueError(f"{file} does not exist! Please input a valid model .pkl path through SetLoadModelPath().")
        with open(file, "rb") as infile:
            loaded_models = pickle.load(infile)
        
        if MCgen_data.ndim == 1:
            MCgen_data = np.expand_dims(MCgen_data, axis = 1)
            
        step2_test_weights = OmniFold_helper_functions.reweight(MCgen_data, loaded_models['step2_classifier'])
        return step2_test_weights
