# Volume Image alignment with Render

This is the documentation for the Render webUI.

## Overview

The render infrastructure consists of web servers that take care of handling the image metadata. The processing is done on so-called clients that communicate with the web service and update the metadata.

To increase performance, some of these client processing procedures are run on the cluster.

In order to enable the users to interact with both the metadata web service and the individual clients, there is a web interface. This interface runs on top of the system that manages the client calls.

At EMBL, this is the graphical cluster node. This means, you can access it through a graphical login and launch the web interface from there.

[Here](x2go.md) you can find details on how to set up this procedure.


## How to use it

Find out how to use it [here](usage.md).

