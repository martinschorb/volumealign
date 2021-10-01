# Volume image alignment with Render

The design of the main window, where you control and run the alignment workflow is inspired by [IMOD's](https://bio3d.colorado.edu/imod/) [`etomo`](https://bio3d.colorado.edu/imod/doc/etomoTutorial.html) main window showing the sequential main steps of the procedure in the menu column on the left and all important parameter settings belonging to the current active steps in the main page.

![startpage](img/webui_start.png "VolumeAlign WebUI startpage")

## Data import - convert

The initial step in the alignment of volume data is to import it into Render and convert the metadata and if necessary also the image data accordingly.

![convert](img/webui_convert.png "VolumeAlign WebUI convert")

This page contains the following elements:

- **Type selector:** choose the type of volume EM data to convert. The rest of the page will adapt accordingly.

- The type-dependent import content (see below)

- **select Render Project** and **select Render stack:** Provide a Render project and stack name into which the metadata will be imported. **Create new Project** and **... Stack** define the names of new instances.

### SBEMImage

- **dataset root directory:** the directory path of the SBEMImage root directory. This is the one that contains the `tiles`, `overviews`, `workspace` and `meta` subfolders.
- **browse:** use this dropdown to browse the directory. To move up (`..`) multiple times, you have to close the selector (`x` on the very right) for each additional step up.

## Generate Tile Pairs

This step will tell Render which of the tiles are neighbours in `x` and `y` and also in `z`. It will then have a collection of pairs that it can try to match with each other all in parallel.

It will be necessary to perform this step multiple times: once for the neighbours in `2D`, and once across slices (`3D`, here you can choose how many neighbouring sections should be considered). This is needed because the image analysis algorithms likely need different parameters to work well, especially with an anisotropic datasets. In case the data changes significantly within a stack, you can also split up your data further.


![convert](img/webui_tilepair.png "VolumeAlign WebUI tilepairs")

## Generate/Update PointMatchCollection for Render stack

This is the most resource-demanding step of the procedure. Here we now like to find matching image areas in neighbouring tiles, the so-called **Point Matches**. This can be done using various image analysis methods like cross-correlation or [SIFT](https://en.wikipedia.org/wiki/Scale-invariant_feature_transform).

It will be necessary to perform this step multiple times: once for the neighbours in `x` and `y`, and once across slices. This is needed because the image analysis algorithms likely need different parameters to work well, especially with an anisotropic datasets. In case the data changes significantly within a stack, you can also split up your data further.

![convert](img/webui_tilepair.png "VolumeAlign WebUI tilepairs")

This page contains the following elements:

- **Tilepair source directory selector:** here you select the tile pairs you want to process. These are the results of the previous step and will be shown based on the stack selection.

- **Type selector:** choose the type of image analysis algorithm to use for determining the point matches. The rest of the page will adapt accordingly.

At the moment, only the SIFT client developed in Janelia that makes use of [Spark](https://en.wikipedia.org/wiki/Apache_Spark) for resource parallelisation is implemented.

- **Select Match Collection:** The results of the analysis will be stored in a database (independent from the stack database). You can store as many runs into the same collection, even if they comprise the same pairs. If you want to add matches to an existing collection, select one. Otherwise create a new one. The `Owner` should describe the nature and project of your dataset while the collection name would specify the stack and potentially some hint about the method(s) and parameters used for determining the matches.


### SIFT point matches
