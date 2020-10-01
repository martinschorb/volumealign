
# Render basic requirements:


- render server up and running [EMBL test server](http://pc-emcf-16.embl.de)
- render client scripts from the compiled (mvn) [main repo](https://github.com/saalfeldlab/render): `/g/emcf/software/render/render-ws-java-client/src/main/scripts`
- render-python from [Allen Institute](https://github.com/AllenInstitute/render-python)
- render-python-apps `renderapi` from [Allen Institute](https://github.com/AllenInstitute/render-python-apps)


# EMBL custom Render-Python module:

Repo: [https://github.com/martinschorb/render-modules](https://github.com/martinschorb/render-modules)



# SBEMImage to Render:

## Status:
1. metadata and conversion to Render tilespecs and stack: [`generate_EM_tilespecs_from_SBEMImage.py`](https://github.com/martinschorb/render-modules/blob/master/rendermodules/dataimport/generate_EM_tilespecs_from_SBEMImage.py)

This script does:
- convert the metadata from SBEMImage to Render format
- connect to the EMBL render server
- create a new stack if defined stack not yet present

2. Mipmap generation: working on a wrapper to include project location on group share to store mipmaps. [`EMBL_mipmaps.py`](https://github.com/martinschorb/render-modules/blob/master/rendermodules/dataimport/EMBL_mipmaps.py)

Will then feed into [`EMBL_mipmaps.py`](https://github.com/martinschorb/render-modules/blob/master/rendermodules/dataimport/EMBL_mipmaps.py) that generates the parameters (local mimap directory in the data root) for [`generate_mipmaps.py`](https://github.com/martinschorb/render-modules/blob/master/rendermodules/dataimport/generate_mipmaps.py) to compute the mipmaps.

Then [`apply_mipmaps_to_render.py`](https://github.com/martinschorb/render-modules/blob/master/rendermodules/dataimport/apply_mipmaps_to_render.py) to build render stack based on mipmaplevels in render's format.

#


# Naming conventions:

I would suggest to user the `owner` field for project types (FIB-SEM, SBEM, ...) amd the `project` to describe the individual datasets. Check [this](https://github.com/saalfeldlab/render/issues/106) for how they do it at Janelia.

# Problems:

Mac: scripts:
- brew install coreutils (for greadlines)
- install JDK with install script
