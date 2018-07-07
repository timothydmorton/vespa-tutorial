This tutorial cracks open the black box of vespa.

If a directory is [completely prepared](#preparing-a-vespa-directory), running `vespa` consists of executing the following commands from a terminal:

    starfit --all <directory name>
    calcfpp <directory name>

The `starfit --all` command [estimates the stellar properties of the host star](#fitting-stellar-models), and `calcfpp` [computes the false positive probability](#calculating-fpp).

# Preparing a `vespa` directory

Running a `vespa` calculation requires creating `star.ini` and `fpp.ini` config files, as described below.

## Host star

Create a `star.ini` file containing the RA/Dec coordinates of the transit candidate host star, and any available observed properties, such as broadband photometric magnitudes, spectroscopic properties, or parallax.
One of the magnitudes provided must be the band in which the transit was observed.
Here is an example `star.ini` file:

    ra = 289.217499
    dec = 47.88446
    J = 10.523, 0.02
    H = 10.211, 0.02
    K = 10.152, 0.02
    g = 12.0428791, 0.05
    r = 11.5968652, 0.05
    i = 11.4300704, 0.05
    z = 11.393061, 0.05
    Kepler = 11.664
    Teff = 5642, 50.0
    feh = -0.27, 0.08
    logg = 4.443, 0.028

## Planet candidate

Create a text file containing the photometry of the detected candidate, detrended and phase-folded.
This file should have the following three columns in order:

  * Time from mid-transit, in units of days
  * Relative flux, normalized to unity; e.g., `flux / median(flux)`.
  * Relative flux uncertainty (also normalized)

The photometry should be limited to only those points within just a few transit durations of the transit, not the entire orbital phase.
This file may have any name, but for current purposes, let's call it `transit.txt`.

The results of three other analyses (calculations that `vespa` does not do) must also be provided:

  - A best-fit estimate of the planet/star radius ratio.

  - An observational upper limit on the depth of a potential secondary eclipse in the light curve.
    This may be calculated by, e.g., running a transit search in the light curve at other phases but keeping the period fixed.

  - A limit on the furthest angular separation from the target star that a potential blending star might reside.
    This limit should come from pixel-level analysis of the target star photometry, establishing that the signal does not originate from a different star.
    While the tightest constraint will come from some kind of centroid or pixel-modeling effort (e.g. [Bryson et al, 2013](https://arxiv.org/pdf/1303.0052.pdf)), it should also be sufficient to test the depth of the signal as a function of aperture size, to see whether the measured depth is aperture-dependent (that is, if the signal is caused by a small amount of flux from a bright eclipsing binary many pixels away from the target, then the signal will be deeper with larger apertures.)
    A good example of what can happen if this analysis is not done carefully is with EPIC210400868 from [Cabrera et al., 2017](https://arxiv.org/pdf/1707.08007.pdf).

All of this information gets summarized in another config file: `fpp.ini`, as follows:

    name = K00087.01
    ra = 289.217499
    dec = 47.88446
    period = 289.864456     # Orbital period of candidate
    rprs = 0.021777742485   # Planet/star radius ratio
    photfile = transit.txt  # File containing transit photometry

    [constraints]
    maxrad = 1.05           # Maximum potential blending radius, in arcsec
    secthresh = 9.593e-05   # Maximum allowed secondary eclipse depth


# Fitting stellar models

The first step of a `vespa` calculation is to fit the stellar parameters to the observed properties of the star.
Before this step, the directory should look like this:

    $ ls TestCase1
    fpp.ini
    star.ini
    transit.txt

Fitting the stellar properties consists of running the `starfit` script, which is part of the `isochrones` package:

    starfit --all TestCase1

This script performs three different fits: single-, binary- and triple-star models.
It should take approximately 25 minutes to run: about 3, 7, and 15 minutes for the single, binary, and triple models, respectively.
After the script finishes, your directory should look like:

    $ls TestCase1
    ....<contents of directory post-starfit>....

The `mist_starmodel_*.h5` files contain the samples from the posterior probability distribution of the model parameters, as well as samples of derived parameters.
You can load the stellar model as follows:

    from isochrones import StarModel
    mod_single = StarModel.load_hdf('TestCase1/mist_starmodel_single.h5')

and you can investigate the posterior samples via the `.samples` attribute:

    mod_single.samples.head()

The `*.png` files in the directory contain diagnostic plots.
There are two kinds of "corner" plots that show the joint distributions of various parameters: `*_physical.png` and `*_observed.png`.
The "physical" plots show the distribution of the physical parameters of the star(s) resulting from the model fits: mass, radius, age, [Fe/H], distance, and extinction.  (Radius is the only of these that is a derived parameter, rather than a directly fitted parameter.)

    from IPython.display import Image
    Image("TestCase1/mist_corner_binary_physical.png")

The "observed" plots show the distribution of the derived parameters of the model that correspond to the quantities used to constrain the models; in this case, seven photometric bands and three spectroscopic parameters.
These figures also show the provided constraint values (blue lines), which can be indicative of a poor stellar model fit if they do not lie comfortably within the distribution of the modeled parameters.

    Image("TestCase1/mist_corner_binary_observed.png")


# Calculating FPP

When the stellar model fits are complete, you can now calculate the false positive probability by executing the following in a terminal:

    `calcfpp TestCase1`

If you want to do a quicker test run, you can run `calcfpp -n 1000` (for example), to make smaller populations (the default `n` is 20000, which takes about 10 minutes).

If you follow along with the output of `calcfpp`, you will notice it first fits the trapezoid model to the observed transit signal.
It then proceeds to generate populations for lots of different models, and subsequently to fit a trapezoidal model to each instance.
By default, `calcfpp` will use the following models:

  * BEB (background(/foreground) eclipsing binary---physically unassociated with target star)
  * HEB (hierarchcial eclipsing binary)
  * EB (eclipsing binary---the target star is an EB, no additional blending)
  * Pl (planet: the true transiting planet model)

There are also `_Px2` versions of the EB models, in which the false positive scenario has a period exactly twice the candidate's period, which could happen if the primary and secondary EB eclipse depths are very similar.

After running `calcfpp`, you now have the following files in your directory:

    $ ls TestCase1
    < full contents of directory >

`popset.h5` contains the simulated populations, and can be loaded as follows:

    from vespa import PopulationSet
    popset = PopulationSet.load_hdf('TestCase1/popset.h5')

Individual populations can be accessed from this object as follows:

    bebs = popset['beb']
    hebs = popset['heb']

As before, `*.png` files are diagnostic figures.  `FPPsummary.png` displays the summary of the results, and the others are informative visualizations of the various models, showing the distribution of simulated trapezoidal model parameters compared to the trapezoidal fit to the true transit candidate signal.

You can also directly load the `FPPCalculation` object from this directory:

    from vespa import FPPCalculation
    fpp = FPPCalculation.load('TestCase1')

At this point, you should be able to quickly get the false positive probability result:

    fpp.FPP()

The calculation is quick this time because the populations are already generated, and the likelihood computations have been cached.
