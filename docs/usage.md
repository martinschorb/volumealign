# Volume image alignment with Render

The design of the main window, where you control and run the alignment workflow is inspired by [IMOD's](https://bio3d.colorado.edu/imod/) [`etomo`](https://bio3d.colorado.edu/imod/doc/etomoTutorial.html) main window showing the sequential main steps of the procedure in the menu column on the left and all important parameter settings belonging to the current active steps in the main page.

![startpage](img/webui_start.png "VolumeAlign WebUI startpage")

## Data import - convert

The initial step in the alignment of volume data is to import it into Render and convert the metadata and if necessary also the image data accordingly.

![convert](img/webui_convert.png "VolumeAlign WebUI convert")

This page contains the following elements:

- **Type selector:** choose the type of volume EM data to convert. The rest of the page will adapt accordingly.

- The type-dependent import content (see below)

- **select Render Project** and **select Render stack:** Provide a Render project and stack name into which the metadata will be imported. **Create new Project** and **Create new Stack** define the names of new instances.

### SBEMImage

- **dataset root directory:** the directory path of the SBEMImage root directory. This is the one that contains the `tiles`, `overviews`, `workspace` and `meta` subfolders.
- **browse:** use this dropdown to browse the directory. To move up (`..`) multiple times, you have to close the selector (`x` on the very right) for each additional step up.

## Generate Tile Pairs

This step will tell Render which of the tiles are neighbours in `x` and `y` and also in `z`. It will then have a collection of pairs that it can try to match with each other all in parallel.

It will be necessary to perform this step multiple times: once for the neighbours in **`2D`**, and once across slices (**`3D`**, here you can choose how many neighbouring sections should be considered). This is needed because the image analysis algorithms likely need different parameters to work well, especially with an anisotropic datasets. In case the data changes significantly within a stack, you can also split up your data further using **Substack selection**.

![tilepairs](img/webui_tilepair.png "VolumeAlign WebUI tilepairs")


## Generate/Update PointMatchCollection for Render stack

This is the most resource-demanding step of the procedure. Here we now like to find matching image areas in neighbouring tiles, the so-called **Point Matches**. This can be done using various image analysis methods like cross-correlation or [SIFT](https://en.wikipedia.org/wiki/Scale-invariant_feature_transform).

It will be necessary to perform this step multiple times: once for the neighbours in `x` and `y`, and once across slices. This is needed because the image analysis algorithms likely need different parameters to work well, especially with an anisotropic datasets. In case the data changes significantly within a stack, you can also split up your data further.

![pointmatch](img/webui_pointmatch.png "VolumeAlign WebUI Pointmatch")

This page contains the following elements:

- **Tilepair source directory selector:** here you select the tile pairs you want to process. These are the results of the previous step and will be shown based on the stack selection.

- **Type selector:** choose the type of image analysis algorithm to use for determining the point matches. The rest of the page will adapt accordingly.

At the moment, only the SIFT client developed in Janelia that makes use of [Spark](https://en.wikipedia.org/wiki/Apache_Spark) for resource parallelisation is implemented.

- **Select Match Collection:** The results of the analysis will be stored in a database (independent from the stack database). You can store as many runs into the same collection, even if they comprise the same pairs. If you want to add matches to an existing collection, select one. Otherwise create a new one. The `Owner` should describe the nature and project of your dataset while the collection name would specify the stack and potentially some hint about the method(s) and parameters used for determining the matches.


### SIFT point matches

Each SIFT run requires several sets of parameters that control the information features that are extracted from each image as well as the criteria to match them.

Render provides a web interface where these parameters can be set and the the quality of the matches as well as their compute time can be estimated for a single representative tile pair.

There is a small library of parameter templates available for several specimens. You can pick them from:

- **Organism Selector**

and

- **Match Trial Selector**

![pointmatch](img/webui_pointmatch_tile.png "VolumeAlign WebUI SIFT Pointmatch - Tiles")

There are also two **Tile Viewers** where you can browse the stack and identify two neighbouring tiles to be used for the match trial.

If you click **Explore MatchTrial**, you will get to the Match Trial web interface. It will show the results of the template trial (the images might not be available).

![matchtrial_template](img/match_trial_create.png "Render WebUI matchTrial")


Click **Create New Trial** at the top of the page. This will open the Parameter editor with the parameters defined in the template.

![matchtrial_params](img/match_trial_params.png "Render WebUI matchTrial Parameters")

To make the tiles from the current stack available to this interface, you need to copy and paste the link that is shown above each tile view in the main UI into the two big text boxes at the bottom of the parameter interface.

Make sure that their relative position (`2D`) is correct in the `Clip Parameters` section.

Click `Run Trial` at the bottom of the page to see if the parameters work for your stack.

On the next page, you will see the results. At the bottom, the two tiles are shown with coloured circles or lines indicating the matching features. Also, it provides statistics and the time it took to derive the matches.

![matchtrial_explore](img/match_trial_explore.png "MatchTrial Explorer, results")

You want to make sure that the Standard Deviation of the matches is within your expectations. This depends on the pixel size and section spacing. Something close to 1 pixel is acceptable.

If the combined time of deriving features and matches is significantly higher than a few hundred ms (`2D`) or 2 seconds (`3D`), it might be worth working with lower resolution images. This decreases the accuracy of the matching but makes it faster.

To change the scaling, modify the last part of the two image URLs in the large text boxes (`scale`) and run the trial again.

```
...&scale=0.4
```


If you are happy with the parameters, copy the long ID at the very end of the website address bar over to the Main UI.

```
...?matchTrialId=xxxxxxxxxxxxxxxxxxxx
```

There, paste it into the text box after **Use this Match Trial as compute parameters:**.

These parameters will then be used for the search of all the tiles.

With the known number of tile pairs and the estimated run time for each pair from the trial, the necessary compute resources for the stack are predicted and can be checked in **Compute settings**.

Launching the computation will request the selected resources on the cluster and then launch a Spark instance on the allocated compute nodes that distributes and manages the parallel computation of the point matches.
You will receive an email once the computation is done. It will tell you that the computation was `CANCELLED` but this only means that the resource allocation has been ended after successful computation of the matches. If you get a message referring to a `TIMEOUT`, you have to re-run the computation with more generous resource settings.

## Solve Positions

Now that we have collected matching features for the tiles, these connections need to be compiled into a global solution positioning all tiles in 3D space to result in the aligned volume.

![solve](img/webui_solve.png "VolumeAlign WebUI solve")


This page contains the following elements:

- **Select Match Collection:** select the match collection that you want to use to align your stack.

- **Explore Match Collection:** This link will lead you to Render's Web tool to visualize and browse match collections.

![match_explore](img/pointmatch_explorer.png "Render Explore Pointmatches")

You will see a 3D graph containing all the tiles and their interconnections. The colours of the links represent the quality and weight of each connection and how it contributes to the global solution. You can also access metadata for each tile and its neighbours.

- **Explore tile/slice:** you can browse individual tiles or slices to determine the **substack selection**.

- **Select Output Render Stack:** The procedure will write a new stack into the existing project. Here you select the target stack.

-**Select Transform type:** Select a transformation type to be used for the solving. `rigid` or `TranslationModel` should match for most volume EM data (except ssTEM).

-**Select solve type:** You can choose between `2D` (inside one section only) and `3D` considering the full volume for the solve.
