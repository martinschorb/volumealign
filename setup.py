import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
  name = "volumealign",
  version = "0.0.1",
  author = "Martin Schorb",
  author_email = "schorb@embl.de",
  description = "Volume alignment with Render",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url = "https://git.embl.de/schorb/volumealign",
  project_urls = {"Bug Tracker" : "https://git.embl.de/schorb/volumealign/issues",
  },
  classifiers = ["Programming Language :: Python :: 3",
      "License :: OSI Approved :: GPLv3 License",
      "Operating System :: OS Independent"],
#  package_dir = {"" : "dash"},
  python_requires = ">=3.6",
  packages=setuptools.find_packages()
)
