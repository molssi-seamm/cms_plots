# -*- coding: utf-8 -*-

"""Methods for creating plots for electronic structure calculations
"""

import logging

try:
    import importlib.metadata as implib
except Exception:
    import importlib_metadata as implib
import jinja2

from .plotting import Figure

logger = logging.getLogger(__name__)


def band_structure_plot(plot, BandStructure):
    """Prepare the graph for the band structure.

    Parameters
    ----------
    plot : plotting.Plot
        Plot object for the graphs
    BandStructure : pandas.DataFrame
        Standard dataframe containing the band structure
    """
    logger.info("Preparing the band structure")

    xs = list(BandStructure.index)

    # Have the full arrays, but want only the labeled points
    labels = BandStructure["labels"].loc[BandStructure["labels"] != ""]

    x_axis = plot.add_axis(
        "x",
        label="",
        tickmode="array",
        tickvals=list(labels.index),
        ticktext=list(labels),
    )
    y_axis = plot.add_axis("y", label="Energy (eV)", anchor=x_axis)
    x_axis.anchor = y_axis

    for label, values in BandStructure.items():
        if label in ("labels", "points"):
            continue

        if "↑" in label:
            color = "red"
        elif "↓" in label:
            color = "blue"
        else:
            color = "black"

        plot.add_trace(
            x_axis=x_axis,
            y_axis=y_axis,
            name=label,
            x=xs,
            xlabel="",
            xunits="",
            y=list(values),
            ylabel="Energy",
            yunits="eV",
            color=color,
        )


def create_figure(self, title="", template="line.graph_template", module_path=None):
    """Create a new figure.

    Parameters
    ----------
    title : str, optional
    template : str, optional
        The Jinja template for the desired graph. Defaults to
        'line.graph_template'

    Returns
    -------
    plotting.Figure
    """

    if self._jinja_env is None:
        # The order of the loaders is important! They are searched
        # in order, so the first has precedence. This searches the
        # current package first, then looks in the main SEAMM
        # templates.
        if module_path is None:
            self.logger.info("Reading graph templates from 'seamm'")
            loaders = [jinja2.PackageLoader("cms_plots")]
        else:
            self.logger.info(
                "Reading graph templates from the following modules, in order"
            )
            loaders = []
            for module in module_path:
                paths = []
                for p in implib.files(module):
                    if p.parent.name == "templates":
                        paths.append(p)
                        break

                if len(paths) == 0:
                    self.logger.info(f"\t{module} -- found no templates directory")
                else:
                    path = paths[0].locate().parent
                    self.logger.info(f"\t{ module} --> {path}")
                    loaders.append(jinja2.FileSystemLoader(path))

        self._jinja_env = jinja2.Environment(loader=jinja2.ChoiceLoader(loaders))

    figure = Figure(jinja_env=self._jinja_env, template=template, title=title)
    return figure


def dos(DOS):
    """Prepare the graph for the density of states.

    Parameters
    ----------
    """
    figure = create_figure(
        module_path=("cms_plots",),
        template="line.graph_template",
        title="Density of States (DOS)",
    )

    # Create a graph of the DOS
    plot = figure.add_plot("DOS")
    dos_plot(plot, DOS)
    figure.grid_plots("DOS")

    return figure


def dos_plot(
    plot,
    DOS,
    colors=(
        "purple",
        "green",
        "cyan",
        "gold",
        "deeppink",
        "turquoise",
        "magenta",
    ),
    dashes={
        "s": "dot",
        "p": "dash",
        "d": "dashdot",
        "f": "longdashdot",
    },
    y_axis=None,
    orientation="horizontal",
    flipped="",
    spin=None,
):
    """Prepare the plot of the density of states (DOS).

    Parameters
    ----------
    plot : plotting.Plot
        The Plot object for the graph.
    DOS : pandas.DataFrame
        The DOS data in a standard form as a Pandas DataFrame.
    colors : (str,)
        The colors to use for atom-projected DOS.
    dashes : (str,)
        The dashes used to denote the shells in projected DOS
    y_axis : plotting.Axis = None
        The y axis for shared plots, in e.g. the combo band structure - DOS plot.
    orientation : str = "horizontal"
        The orientation of the energy axis, horizontal or vertical.
    flipped : str
        If this string contains "x" the energy in a veritcal graph increases to left.
    spin : str = None
        If not None, only DOS with labels including this string are plotted. Intended
        to be e.g. "↑" or "↓" to pick out the spin-up or -down bands.
    """
    if orientation == "horizontal":
        x_axis = plot.add_axis("x", label="Energy (eV)")
        if y_axis is None:
            y_axis = plot.add_axis("y", label="DOS")
    else:
        if "x" in flipped:
            x_axis = plot.add_axis(
                "x",
                label="DOS",
                ticklabelposition="inside",
                autorange="reversed",
            )
        else:
            x_axis = plot.add_axis(
                "x",
                label="DOS",
                ticklabelposition="inside",
            )
        if y_axis is None:
            y_axis = plot.add_axis("y", label="Energy (eV)")

    x_axis.anchor = y_axis
    y_axis.anchor = x_axis

    # The common x coordinates (energy)
    xs = list(DOS.index)

    last_element = None
    count = -1
    for column in DOS.columns:
        if spin is not None and spin not in column:
            continue

        if "Total" in column:
            if "↑" in column:
                color = "red"
                dash = "solid"
            elif "↓" in column:
                color = "blue"
                dash = "solid"
            else:
                color = "black"
                dash = "solid"
        else:
            if "_" in column:
                element, shell = column.split("_")
                shell = shell[0]
                dash = dashes[shell]
            else:
                element = column.split(" ")[0]
                dash = "solid"
            if element != last_element:
                last_element = element
                count += 1
                if count >= len(colors):
                    count = 0
                color = colors[count]

        if orientation == "horizontal":
            plot.add_trace(
                x_axis=x_axis,
                y_axis=y_axis,
                name=column,
                x=xs,
                xlabel="E",
                xunits="eV",
                y=list(DOS[column]),
                ylabel=column,
                yunits="",
                color=color,
                dash=dash,
            )
        else:
            plot.add_trace(
                x_axis=x_axis,
                y_axis=y_axis,
                name=column,
                x=list(DOS[column]),
                xlabel=column,
                xunits="",
                y=xs,
                ylabel="E",
                yunits="eV",
                color=color,
                dash=dash,
            )
