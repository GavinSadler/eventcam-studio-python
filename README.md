
# eventcam-studio-python

Things to install beforehand:

[Metavision Studio 5.2 or greater](https://files.prophesee.ai/share/dists/public/windows/baiTh5si/) \
[Pylon](https://www.baslerweb.com/en/software/pylon/) \
[Python 3.9](https://www.python.org/downloads/release/python-3913/) or [Python 3.8](https://www.python.org/downloads/release/python-3810/) SPECIFICALLY (This is a requirement of Metavision's Python API)

Install the following:

```bash
# Update pip
$ pip install pip --upgrade

# Pylon requirements
$ pip install pypylon

# Metavision requirements
$ pip install "opencv-python==4.5.5.64" "sk-video==1.1.10" "fire==0.4.0" "numpy==1.23.4" "h5py==3.7.0" pandas scipy
$ pip install matplotlib "ipywidgets==7.6.5"

# Our UI requirements
$ pip install dearpygui
```

[Pypylon is Basler's Python library](https://github.com/basler/pypylon) \
[Metavision's python instructions installation for their SDK on Windows](https://docs.prophesee.ai/stable/installation/windows.html#installing-dependencies)
