# VolumeAlign WebUI development and customization


## General design

The frontend for users is written in [Potly.dash](https://dash.plotly.com/)(`>1.16`, version `2.0` is supported and will be necessary soon) based on Python (`> 3.6`).

The design of the workflow is inspired and borrowed from [IMOD's](https://bio3d.colorado.edu/imod/) [`etomo`](https://bio3d.colorado.edu/imod/doc/etomoTutorial.html) main window showing the sequential main steps of the procedure in the menu column on the left and all important parameter settings belonging to the current active steps in the main page.

## customization

All sub-pages can be arranged individually. Some commonly used functionality is made available through generic functions with the page elements provided in [`index.py`]({{ dirs.code }}dash/index.py).



::: solve
    rendering:
        show_root_heading: true
