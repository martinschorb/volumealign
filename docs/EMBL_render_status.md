
# Render basic requirements:


- render server up and running [EMBL Render server](http://render.embl.de)
- render client scripts (`geometric-descriptor`) from the compiled (mvn) [main repo](https://github.com/saalfeldlab/render): `/g/emcf/software/render/render-ws-java-client/src/main/scripts`
- render-python `renderapi` (`develop`) from [Allen Institute](https://github.com/AllenInstitute/render-python-apps)


# EMBL custom Render-Python module:

Repo: [https://github.com/martinschorb/render-modules](https://github.com/martinschorb/render-modules)



# SBEMImage to Render:
[Pipeline schema](https://schorb.embl-community.io/volumealign/SBEM_scheme.html)

## Status:
1. metadata and conversion to Render tilespecs and stack: [`generate_EM_tilespecs_from_SBEMImage.py`](https://github.com/martinschorb/render-modules/blob/master/rendermodules/dataimport/generate_EM_tilespecs_from_SBEMImage.py)

This script does:
- convert the metadata from SBEMImage to Render format
- connect to the EMBL render server
- create a new stack if defined stack not yet present

2. Tilepair generation: `create_tilepairs.py`](https://github.com/martinschorb/render-modules/blob/master/rendermodules/pointmatch/create_tilepairs.py)

3. SIFT-Alignment: Option 1) [openCV](https://github.com/martinschorb/render-modules/blob/master/rendermodules/pointmatch/generate_point_matches_opencv.py)
  Option 2) [spark](https://github.com/martinschorb/render-modules/blob/master/rendermodules/pointmatch/generate_point_matches_spark.py)->[SIFTPointMatchClient](https://github.com/saalfeldlab/render/blob/geometric_descriptor/render-ws-spark-client/src/main/java/org/janelia/render/client/spark/SIFTPointMatchClient.java"). Right now call the Client Script from [submission bash script](https://git.embl.de/schorb/volumealign/-/blob/master/spark_slurm.sh) directly.

4. Solve (Allen's `bigfeta` [solver](https://github.com/martinschorb/render-modules/blob/master/rendermodules/solver/solve.py)) - Need to activate MogoDB's network access (in `/etc/mongod.conf`, add local IP). Alternatively: set `db_interface` to `render`.

5. 2D montage and 3D cross-layer matching can be iterated.

# Render to BDV:

Established [N5 export](https://github.com/saalfeldlab/render/blob/geometric_descriptor/render-ws-spark-client/src/main/java/org/janelia/render/client/spark/n5/N5Client.java).

Need an additional step to create proper BDV-N5 metadata context using [PyBDV](https://github.com/constantinpape/pybdv).


# Naming conventions:

I would suggest to user the `owner` field for project types (FIB-SEM, SBEM, ...) and the `project` to describe the individual datasets. Check [this](https://github.com/saalfeldlab/render/issues/106) for how they do it at Janelia.
