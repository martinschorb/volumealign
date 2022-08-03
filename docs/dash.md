# VolumeAlign WebUI development and customization


## General design

The frontend for users is written in [Potly.dash](https://dash.plotly.com/)(`>= 2.0`) based on Python (`> 3.6`).

The design of the workflow is inspired and borrowed from [IMOD's](https://bio3d.colorado.edu/imod/) [`etomo`](https://bio3d.colorado.edu/imod/doc/etomoTutorial.html) main window showing the sequential main steps of the procedure in the menu column on the left and all important parameter settings belonging to the current active steps in the main page.

## customization

All sub-pages can be arranged individually. Some commonly used functionality is made available through generic functions with the page elements provided in [`index.py`]({{ dirs.code }}dash/index.py).

## HTTPS encryption

The web interface can be reached using HTTPS if a certificate (`cert.pem`) and key (`key.pem`) file is provided in the root directory. These can be created using 
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```