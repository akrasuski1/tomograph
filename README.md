
To run:
```
./run.sh img/shepp.png
```

You can change delta alpha (step size) by changing `n_samples` variable. Setting it to
180 makes 180 samples, giving a 1 degree step size. Changing resolution of a single
scan (number of emitters and detectors) is done by setting `n_emitters` variable.
Setting the detector spread is done by setting `l_spread` variable. It is ratio of the 
spread to the whole image width (i.e. values higher than 1 are nonsense).
Changing boolean variable `use_filter` decides whether the tomograph will use convolution
filtering to improve resulting image quality.

Directory structure:
- out/scan - will show where the detectors are at each point in time
- out/sino - will show how the sinogram looks
- out/reco - will show how the reconstructed image looks like
