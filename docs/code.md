# Volume Image alignment Code documentation

## Infrastructure/Installation

The Basic installation requires the following software:

- the [Render web services](https://github.com/saalfeldlab/render) including the underlying [MongoDB](https://www.mongodb.com/) database.

- render client scripts from the compiled (mvn) [main repo](https://github.com/saalfeldlab/render): These need to be accessible for all machines that run clients.

- render-python-apps `renderapi` from [Allen Institute](https://github.com/AllenInstitute/render-python-apps)

- the EMBL custom Render-Python module (based on `render-modules` development at the Allen Institute). This includes the `BigFeta` global solver.
Repo: [https://github.com/martinschorb/render-modules](https://github.com/martinschorb/render-modules)

- in addition, an additional step to create proper BDV-N5 metadata context (last step  finalize`) is necessary using [PyBDV](https://github.com/constantinpape/pybdv).

## Frontend

The frontend for users to interact with the services is a [WebUI](dash.md) written in [Potly.dash](https://dash.plotly.com/). It provides visual interaction with some of Render's WebInterfaces, prepares the necessary parameters and launches and controls the client script application.

Most of the parameters are transparently provided to [`render-modules`](https://github.com/martinschorb/render-modules) through `JSON` files in the underlying [`argschema`](https://github.com/AllenInstitute/argschema) specification.
