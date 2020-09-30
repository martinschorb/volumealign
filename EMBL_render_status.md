



# Render basic requirements:


- render server up and running [EMBL test server](http://pc-emcf-16.embl.de)
- render client scripts from the compiled (mvn) [main repo](https://github.com/saalfeldlab/render): `/g/emcf/software/render/render-ws-java-client/src/main/scripts`
- render-python from [Allen Institute](https://github.com/AllenInstitute/render-python)
- render-python-apps `renderapi` from [Allen Institute](https://github.com/AllenInstitute/render-python-apps)


# EMBL custom Render-Python module:

Repo: [https://github.com/martinschorb/render-modules](https://github.com/martinschorb/render-modules)


problems:

Mac: scripts:
- brew install coreutils (for greadlines)
- install JDK with install script


# steps

1) create tilespec metadata
  - SBEM: OK (`sbem2renderstack.py` in `render-python-apps/.../dataimport`)



2) generate mipmaps
  - SBEM: OK (`create_mipmaps` - need to check URLs to files, depends on where this runs)

3) create stacks
  - OK

4) populate render
