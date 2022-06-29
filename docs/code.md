# Volume Image alignment Code documentation

## Infrastructure/Installation

The Basic installation requires the following software:

- the [Render web services](https://github.com/saalfeldlab/render) including the underlying [MongoDB](https://www.mongodb.com/) database. For full functionality, it is necessary to use the current `geometric-descriptor` branch.

- render client scripts from the compiled (mvn) [main repo](https://github.com/saalfeldlab/render): These need to be accessible for all machines that run clients.  For full functionality, it is necessary to use the current `geometric-descriptor` branch.

- render-python `renderapi` forked from [Allen Institute](https://github.com/martinschorb/render-python). This is consistent with the original `develop` branch.

- Asap modules `asap-modules` from [Allen Institute](https://github.com/AllenInstitute/asap-modules). This includes the `BigFeta` global solver.

- the EMBL custom Render-Python module (based on `asap-modules` development at the Allen Institute)
Repo: [`rendermodules-addons`](https://git.embl.de/schorb/rendermodules-addons)

- This includes the importers and scripts create proper BDV-N5 metadata context (last step  `finalize`) using [PyBDV](https://github.com/constantinpape/pybdv) and an exporter to MoBIE using [`mobie-utils-python`](https://github.com/mobie/mobie-utils-python).

## Frontend

The frontend for users to interact with the services is a [WebUI](dash.md) written in [Potly.dash](https://dash.plotly.com/). It provides visual interaction with some of Render's WebInterfaces, prepares the necessary parameters and launches and controls the client script application.

Most of the parameters are transparently provided to `asap-modules` and `rendermodules-addons` through `JSON` files in the underlying [`argschema`](https://github.com/AllenInstitute/argschema) specification.
