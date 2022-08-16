# -*- coding: utf-8 -*-

"""cms_plots
Plots for computational materials/molecular science
"""

# Bring up the classes so that they appear to be directly in
# the cms_plots

# Main classes
from .plotting import Figure  # noqa: F401
from .electronic import band_structure, band_structure_plot  # noqa: F401
from .electronic import create_figure, dos, dos_plot  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
