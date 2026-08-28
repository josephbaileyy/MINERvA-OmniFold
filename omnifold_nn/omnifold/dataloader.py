import numpy as np

class DataLoader():
    def __init__(
            self,
            reco,
            pass_reco = None,
            gen = None,
            pass_gen = None,
            weight = None,
            weight_reco = None,
            normalize=False,
            normalization_factor = 1_000_000,
            bootstrap = False,
            rank = 0,
            size = 1,
            reco_evt = None,
            gen_evt = None,
    ):
        """
        Initializes the DataLoader with the required datasets and parameters for handling 
        the training in OmniFold.

        Parameters:
        -----------
        reco : numpy.ndarray
            The detector-level (reconstructed) dataset.        
        pass_reco : numpy.ndarray, optional (default=None)
            A boolean array or mask that specifies a subset of the reconstructed data passing reco cuts.         
        gen : numpy.ndarray, optional (default=None)
            The truth-level (generated) dataset. This can be `None` for measured data.        
        pass_gen : numpy.ndarray, optional (default=None)
            A boolean array or mask for the truth-level data, specifying a subset of generated data to be used.        
        weight : numpy.ndarray, optional (default=None)
            An array of weights associated with the reconstructed or truth-level data. 
            These weights can be initial MC weights for the simulation
        weight_reco : numpy.ndarray, optional (default=None)
            OPTIONAL second MC weight array for the DETECTOR-level (step-1) leg -- audit finding
            B-4, decision D1 (2026-08-04). When supplied, `weight` is the TRUTH-leg weight (step 2
            and every truth-space quantity) and `weight_reco` is what step 1 consumes. The two are
            two views of ONE MC event, so they share the bootstrap draw and a single normalization
            constant. Leave as `None` for the historical single-weight contract, which is preserved
            byte-for-byte.
        normalize : bool, optional (default=False)
            If `True`, the dataset will be normalized according to the provided `normalization_factor`.
            Normalization ensures that the total sum of weights equals the normalization factor.        
        normalization_factor : float, optional (default=1_000_000)
            The factor by which to normalize the dataset if `normalize` is set to `True`. 
            This value is applied such that the total sum of weights matches this factor.        
        bootstrap : bool, optional (default=False)
            If `True`, bootstrapping will be applied to resample the data. Bootstrapping involves random sampling 
            with replacement using Poisson weights.
        """

        if gen is not None:
            assert reco.shape[0] == gen.shape[0], "ERROR: Reco and Gen Events have different number of entries"
        self.rank = rank
        self.size = size
        self.nmax = reco.shape[0]
        self.reco = reco
        self.weight = weight
        self.weight_reco = weight_reco
        self.gen = gen
        self.pass_reco = pass_reco
        self.pass_gen = pass_gen
        self.bootstrap=bootstrap
        # Optional per-event CONTINUOUS high-level features, paired row-for-row with the
        # reco/gen point clouds (KNOWN_ISSUES #19 full-event representation). reco_evt goes
        # with `reco` (a step-1 detector-level feature block; for data this is event_data,
        # for MC this is event_reco -- SAME observable schema), gen_evt with `gen` (event_truth,
        # its own truth schema/normalization). Left None => byte-for-byte the recoil-only path.
        self.reco_evt = reco_evt
        self.gen_evt = gen_evt

        self.reco = self.reco[rank::size]
        if self.gen is not None:
            self.gen = self.gen[rank::size]
        if self.reco_evt is not None:
            assert self.reco_evt.shape[0] == self.nmax, \
                "ERROR: reco_evt and reco have different number of entries"
            self.reco_evt = self.reco_evt[rank::size]
        if self.gen_evt is not None:
            assert self.gen is not None and self.gen_evt.shape[0] == gen.shape[0], \
                "ERROR: gen_evt requires gen and must match its entries"
            self.gen_evt = self.gen_evt[rank::size]

        if self.weight is None:
            if self.rank==0:print("INFO: Creating weights ...")
            self.weight = np.ones(self.reco.shape[0],dtype=np.float32)
        else:
            self.weight = self.weight[rank::size]
            
        # B-4 / D1: shard the reco leg exactly like the truth leg. Kept as `None` when absent so
        # every historical single-weight consumer is untouched.
        if self.weight_reco is not None:
            self.weight_reco = self.weight_reco[rank::size]
            assert self.weight_reco.shape[0] == self.weight.shape[0], \
                "ERROR: weight_reco and weight have different number of entries"

        if self.bootstrap:
            # ONE Poisson draw shared by both legs. Independent draws would decorrelate the reco
            # and truth views of the same MC event and smear the migration matrix
            # (2d-unfolding/2D_OMNIFOLD_REFERENCE.md, bootstrap invariant 2).
            _draw = np.random.poisson(1,self.weight.shape[0])
            self.weight = _draw*self.weight
            if self.weight_reco is not None:
                self.weight_reco = _draw*self.weight_reco
            
        if self.pass_reco is None:
            if self.rank==0:print("INFO: Creating pass reco flag ...")
            self.pass_reco = np.ones(self.reco.shape[0],dtype=bool)
        else:
            #Make a boolean mask
            self.pass_reco = np.array(self.pass_reco) == 1
            #Distribute across GPUs
            self.pass_reco = self.pass_reco[rank::size]

        self.is_mc =  self.gen is not None

        if self.is_mc:            
            if  self.pass_gen is None:
                if self.rank==0:print("INFO: Creating pass gen flag ...")
                self.pass_gen = np.ones(self.gen.shape[0],dtype=bool)
            else:
                #Make a boolean mask
                self.pass_gen = np.array(self.pass_gen) == 1
                #Distribute across GPUs
                self.pass_gen = self.pass_gen[rank::size]
                

        if normalize:
            if self.rank==0:print(f"INFO: Normalizing sum of weights to {normalization_factor} ...")
            # B-4 / D1, Option A (decided 2026-08-04). The step-1 class ratio is set by the weight
            # step 1 ACTUALLY consumes, so when a reco leg is supplied the constant is derived from
            # IT, and the SAME constant scales both legs. That preserves the per-event
            # weight_reco/weight ratio, which is a physical MINOS-efficiency factor measured in
            # [0.931, 0.998] on the production dump -- renormalizing the legs separately would
            # multiply it by sum(w_truth)/sum(w_reco) and destroy that meaning. Step 2 loses
            # nothing, because it weights BOTH of its classes by `weight` and is therefore
            # scale-invariant.
            #
            # CONSEQUENCE, stated because it is a trap: with a reco leg supplied,
            # sum(weight[pass_reco]) is NOT normalization_factor -- it is that times
            # sum(w_truth[pass_reco])/sum(w_reco[pass_reco]). Truth-space yields must therefore be
            # built from the RAW truth weights times pot_scale, never from this normalized copy.
            _pr = np.array(self.pass_reco)==1
            _src = self.weight if self.weight_reco is None else self.weight_reco
            sumw = np.sum(_src[_pr])
            _c = (normalization_factor/sumw).astype(np.float32)
            # In-place on purpose: `self.weight` is a view of the caller's array, and callers rely
            # on seeing the rescale (train_fullevent_nominal.py:74 documents that dependency). Do
            # not convert these to `x = x*_c` -- it would silently break that aliasing.
            self.weight *= _c
            if self.weight_reco is not None:
                self.weight_reco *= _c
