This tutorial cracks open the black box of vespa.

If a directory is [completely prepared](#preparing-a-vespa-directory), running vespa consists of executing the following commands from a terminal:

    starfit --all <directory name>
    calcfpp <directory name>

The `starfit --all` command [estimates the stellar properties of the host star](#fitting-stellar-models), and `calcfpp` [computes the false positive probability](#calculating-fpp).

# Preparing a `vespa` directory

Running a `vespa` calculation requires creating `star.ini` and `fpp.ini` config files, as described below.

## Stellar property config file

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



  - Photometry of the detected candidate, detrended and phase-folded.
    This should be presented as a text file with the following three columns in order:

        * Time from mid-transit, in units of days
        * Flux, normalized to 1; e.g., `flux / median(flux)`.
        * Flux uncertainty (also normalized)

    The photometry should be limited to only those points within just a few transit durations of the transit.

The results of two other analyses must also be provided to `vespa`:

  - An observational upper limit on the depth of a potential secondary eclipse in the light curve.
    This may be calculated by, e.g., running a transit search in the light curve at other phases but keeping the period fixed.

  - A limit on the furthest angular separation from the target star that a potential blending star might reside.
    This limit should come from pixel-level analysis of the target star photometry, establishing that the signal does not originate from a different star.
    While the tightest constraint will come from some kind of centroid or pixel-modeling effort (e.g. [Bryson et al, 2013](https://arxiv.org/pdf/1303.0052.pdf)), it should also be sufficient to test the depth of the signal as a function of aperture size, to see whether the measured depth is aperture-dependent (that is, if the signal is caused by a small amount of flux from a bright eclipsing binary many pixels away from the target, then the signal will be deeper with larger apertures.)
    A good example of what can happen if this analysis is not done carefully is with EPIC210400868 from [Cabrera et al., 2017](https://arxiv.org/pdf/1707.08007.pdf).

All of this information gets summarized in two config files: `star.ini` and `fpp.ini`

# Fitting stellar models


# Calculating FPP


If you want to do a test run, you can run `calcfpp -n 100` (for example), to make smaller populations (the default `n` is 20000).
A typical `starfit --all` call takes will take about 25 minutes: about 3 minutes for the single star fit, 7 for the binary star fit, and 15 for the triple star fit.
If desired, you may get the same effect as `starfit --all` by executing three different jobs in parallel: `starfit <directory>`, `starfit --binary <directory>`, and `starfit --triple <directory>`.
`calcfpp` with default population size runs in about 10 minutes.
