from __future__ import division, print_function

import iotbx.phil

help_message = '''
Redesign script for merging xfel data
'''

from xfel.merging.database.merging_database import mysql_master_phil
master_phil="""
data {
  type = *glob dir file
    .type = choice
    .help = How is the data identified, either by glob, directory name, or file name?
  path = None
    .type = str
    .multiple = True
    .help = paths is validated as a glob, directory or file, respectively.
    .help = however, validation is delayed until data are assigned to parallel ranks?
    .help = integrated_experiments (.json) and reflection tables (.pickle) must both be
    .help = present as matching files.  Only one need be explicitly specified.
}

filter
  .help = The FILTER section defines criteria to accept or reject whole experiments
  .help = or to modify the entire experiment by a reindexing operator
  .help = refer to the select section for filtering of individual reflections
  {
  algorithm = n_obs a_list reindex resolution unit_cell report
    .type = choice
    .multiple = True
  n_obs {
    min = 15
      .help = Minimum number of observations for subsequent processing
  }
  a_list
    .help = a_list is a text file containing a list of acceptable experiments
    .help = for example, those not misindexed, wrong type, or otherwise rejected as determined separately
    .help = suggested use, string matching, can include timestamp matching, directory name, etc
    {
    file = None
      .type = path
      .multiple = True
    operation = *select deselect
      .type = choice
      .multiple = True
      .help = supposedly have same number of files and operations. Different lists can be provided for select and deselect
  }
  reindex {
    data_reindex_op = h,k,l
      .type = str
      .help = Reindex, e.g. to change C-axis of an orthorhombic cell to align Bravais lattice from indexing with actual space group
    reverse_lookup = None
      .type = str
      .help = filename, pickle format, generated by the cxi.brehm_diederichs program.  Contains a
      .help = (key,value) dictionary where key is the filename of the integrated data pickle file (supplied
      .help = with the data phil parameter and value is the h,k,l reindexing operator that resolves the
      .help = indexing ambiguity.
  }
  resolution {
    d_min = None
      .type = float
      .help = Reject the experiment unless some reflections extend beyond this resolution limit
    model_or_image = model image
      .type = choice
  }
  unit_cell
    .help = Various algorithms to restrict unit cell and space group
    {
    algorithm = range value cluster
      .type = choice
    value
      .help = Discard lattices that are not close to the given target.
      .help = If the target is left as Auto, use the scaling model
      .help = (derived from either PDB file cryst1 record or MTZ header)
      {
      target_unit_cell = Auto
        .type = unit_cell
      target_space_group = Auto
        .type = space_group
      unit_cell_length_tolerance = 0.1
        .type = float
        .help = Fractional change in unit cell dimensions allowed (versus target cell).
      unit_cell_angle_tolerance = 2.
        .type = float
      }
    cluster
      .help = CLUSTER implies an implementation (standalone program or fork?) where all the
      .help = unit cells are brought together prior to any postrefinement or merging,
      .help = and analyzed in a global sense to identify the isoforms.
      .help = the output of this program could potentially form the a_list for a subsequent
      .help = run where the pre-selected events are postrefined and merged. {
      algorithm = rodgriguez_laio dbscan
        .type = choice
      isoform = None
        .type=str
        .help = unknown at present. if there is more than one cluster, such as in PSII,
        .help = perhaps the program should write separate a_lists.
        .help = Alternatively identify a particular isoform to carry forward for merging.
    }
  }
}

modify
  .help = The MODIFY section defines operations on the integrated intensities
  {
  algorithm = *polarization
    .type = choice
    .multiple = True
}

select
  .help = The SELECT section accepts or rejects specified reflections
  {
  algorithm = panel cspad_sensor significance_filter outlier
    .type = choice
    .multiple = True
  cspad_sensor {
    number = None
      .type = int(value_min=0, value_max=31)
      .multiple = True
      .help = Index in the range(32) specifying sensor on the CSPAD to deselect from merging, for the purpose
      .help = of testing whether an individual sensor is poorly calibrated.
    operation = *deselect select
      .type = choice
      .multiple = True
  }
  significance_filter
    .help = If listed as an algorithm, apply a sigma cutoff (on unmerged data) to limit
    .help = the resolution from each diffraction pattern.
    .help = Implement an alternative filter for fuller-kapton geometry
    {
    n_bins = 12
      .type = int (value_min=2)
      .help = Initial target number of resolution bins for sigma cutoff calculation
    min_ct = 10
      .type = int
      .help = Decrease number of resolution bins to require mean bin population >= min_ct
    max_ct = 50
      .type = int
      .help = Increase number of resolution bins to require mean bin population <= max_ct
    sigma = 0.5
      .type = float
      .help = Remove highest resolution bins such that all accepted bins have <I/sigma> >= sigma
  }
  outlier {
    min_corr = 0.1
      .type = float
      .help = Correlation cutoff for rejecting individual frames.
      .help = This filter is not applied if model==None. No experiments are rejected with min_corr=-1.
      .help = This either keeps or rejects the whole experiment.
    assmann_diederichs {}
  }
}

scaling {
  model = None
    .type = str
    .help = PDB filename containing atomic coordinates & isomorphous cryst1 record
    .help = or MTZ filename from a previous cycle
  model_reindex_op = h,k,l
    .type = str
    .help = Kludge for cases with an indexing ambiguity, need to be able to adjust scaling model
  k_sol = 0.35
    .type = float
    .help = If model is taken from coordinates, use k_sol for the bulk solvent scale factor
    .help = default is approximate mean value in PDB (according to Pavel)
  b_sol = 46.00
    .type = float
    .help = If model is taken from coordinates, use b_sol for bulk solvent B-factor
    .help = default is approximate mean value in PDB (according to Pavel)
  algorithm = *mark0 mark1
    .type = choice
    .help = "mark0: original per-image scaling by reference to isomorphous PDB model"
    .help = "mark1: no scaling, just averaging (i.e. Monte Carlo
             algorithm).  Individual image scale factors are set to 1."
}

postrefinement {
  enable = False
    .type = bool
    .help = enable the preliminary postrefinement algorithm (monochromatic)
    .expert_level = 3
  algorithm = *rs rs2 rs_hybrid eta_deff
    .type = choice
    .help = rs only, eta_deff protocol 7
    .expert_level = 3
  rs2
    .help = Reimplement postrefinement with the following (Oct 2016):
    .help = Refinement engine now work on analytical derivatives instead of finite differences
    .help = Better convergence using "traditional convergence test"
    .help = Use a streamlined frame_db schema, currently only supported for FS (filesystem) backend
    {}
  rs_hybrid
    .help = More aggressive postrefinement with the following (Oct 2016):
    .help = One round of 'rs2' using LBFGS minimizer as above to refine G,B,rotx,roty
    .help = Gentle weighting rather than unit weighting for the postrefinement target
    .help = Second round of LevMar adding an Rs refinement parameter
    .help = Option of weighting the merged terms by partiality
    {
    partiality_threshold = 0.2
      .type = float ( value_min = 0.01 )
      .help = throw out observations below this value. Hard coded as 0.2 for rs2, allow value for hybrid
      .help = must enforce minimum positive value because partiality appears in the denominator
    }
  target_weighting = *unit variance gentle extreme
    .type = choice
    .help = weights for the residuals in the postrefinement target (for rs2 or rs_hybrid)
    .help = Unit: each residual weighted by 1.0
    .help = Variance: weighted by 1/sigma**2.  Doesn't seem right, constructive feedback invited
    .help = Gentle: weighted by |I|/sigma**2.  Seems like best option
    .help = Extreme: weighted by (I/sigma)**2.  Also seems right, but severely downweights weak refl
  merge_weighting = *variance
    .type = choice
    .help = assumed that individual reflections are weighted by the counting variance
  merge_partiality_exponent = 0
    .type = float
    .help = additionally weight each measurement by partiality**exp when merging
    .help = 0 is no weighting, 1 is partiality weighting, 2 is weighting by partiality-squared
  lineshape = *lorentzian gaussian
    .type = choice
    .help = Soft sphere RLP modeled with Lorentzian radial profile as in prime
    .help = or Gaussian radial profile. (for rs2 or rs_hybrid)
  show_trumpet_plot = False
    .type = bool
    .help = each-image trumpet plot showing before-after plot. Spot color warmth indicates I/sigma
    .help = Spot radius for lower plot reflects partiality. Only implemented for rs_hybrid
}

merging {
  minimum_multiplicity = None
    .type = int(value_min=2)
    .help = If defined, merged structure factors not produced for the Miller indices below this threshold.
  error {
    model = ha14 ev11 errors_from_sample_residuals
      .type = choice
      .multiple = False
      .help = ha14, formerly sdfac_auto, apply sdfac to each-image data assuming negative
      .help = intensities are normally distributed noise
    ev11
      .help = formerly sdfac_refine, correct merged sigmas refining sdfac, sdb and sdadd as Evans 2011.
      {
      random_seed = None
        .help = Random seed. May be int or None. Only used for the simplex minimizer
        .type = int
        .expert_level = 1
      minimizer = *lbfgs LevMar
        .type = choice
        .help = Which minimizer to use while refining the Sdfac terms
      refine_propagated_errors = False
        .type = bool
        .help = If True then during sdfac refinement, also \
                refine the estimated error used for error propagation.
      show_finite_differences = False
        .type = bool
        .help = If True and minimizer is lbfgs, show the finite vs. analytical differences
      plot_refinement_steps = False
        .type = bool
        .help = If True, plot refinement steps during refinement.
    }
  }
  plot_single_index_histograms = False
    .type = bool
  set_average_unit_cell = True
    .type = bool
    .help = Output file adopts the unit cell of the data rather than of the reference model.
    .help = How is it determined?  Not a simple average, use a cluster-driven method for
    .help = deriving the best unit cell value.
  d_min = None
    .type = float
    .help = limiting resolution for scaling and merging
  d_max = None
    .type = float
    .help = limiting resolution for scaling and merging.  Implementation currently affects only the CCiso cal
  merge_anomalous = False
    .type = bool
    .help = Merge anomalous contributors
}

output {
  prefix = iobs
    .type = str
    .help = Prefix for all output file names
  title = None
    .type = str
    .help = Title for run - will appear in MTZ file header
}

statistics {
  n_bins = 10
    .type = int(value_min=1)
    .help = Number of resolution bins in statistics table
  cc1_2 {
    hash_filenames = False
      .type = bool
      .help = For CC1/2, instead of using odd/even filenames to split images into two sets,
      .help = hash the filename using md5 and split the images using odd/even hashes.
  }
  cciso {
    mtz_file = None
      .type = str
     .help = for Riso/ CCiso, the reference structure factors, must have data type F
      .help = a fake file is written out to this file name if model is None
    mtz_column_F = fobs
      .type = str
      .help = for Riso/ CCiso, the column name containing reference structure factors
  }
  predictions_to_edge {
    apply = False
      .type = bool
      .help = If True and key 'indices_to_edge' not found in integration pickles, predictions
      .help = will be made to the edge of the detector based on current unit cell, orientation,
      .help = and mosaicity.
    image = None
      .type = path
      .help = Path to an example image from which to extract active areas and pixel size.
    detector_phil = None
      .type = path
      .help = Path to the detector version phil file used to generate the selected data.
  }
  report_ML = True
    .type = bool
    .help = Report statistics on per-frame attributes modeled by max-likelihood fit (expert only)
}

parallel {
  nproc = 1
    .help = 1, use no parallel execution.
    .type = int
}

""" + mysql_master_phil

class Script(object):
  '''A class for running the script.'''

  def __init__(self):
    # The script usage
    import libtbx.load_env
    self.usage = "usage: %s [options] [param.phil] " % libtbx.env.dispatcher_name
    self.parser = None

  def initialize(self):
    '''Initialise the script.'''
    from dials.util.options import OptionParser
    from iotbx.phil import parse
    phil_scope = parse(master_phil)
    # Create the parser
    self.parser = OptionParser(
      usage=self.usage,
      phil=phil_scope,
      epilog=help_message)
    self.parser.add_option(
        '--plots',
        action='store_true',
        default=False,
        dest='show_plots',
        help='Show some plots.')

    # Parse the command line. quick_parse is required for MPI compatibility
    params, options = self.parser.parse_args(show_diff_phil=True,quick_parse=True)
    self.params = params
    self.options = options

  def validate(self):
    from xfel.merging.application.validation.application import application
    application(self.params)

  def run(self):
    print('''Mock run, merge some data.''')
    self.initialize()
    self.validate()
    # do other stuff
    return

if __name__ == '__main__':
  script = Script()
  result = script.run()
  print ("OK")