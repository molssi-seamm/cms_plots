# -*- coding: utf-8 -*-

"""Methods for creating plots for electronic structure calculations"""

import logging

try:
    import importlib.metadata as implib
except Exception:
    import importlib_metadata as implib
import jinja2

from .plotting import Figure

logger = logging.getLogger(__name__)


def band_structure(
    Band_Structure,
    DOS=None,
    layout="3-panels",
    template="band_structure.html_template",
):
    """Prepare the graph for the bandstructure

    Parameters
    ----------
    Band_Structure : pandas.DataFrame
        The band structure data in a standard Pandas dataframe.
    DOS : pandas.DataFrame
        The DOS data in a standard Pandas dataframe.
    layout : str
        For spin polarized calculations, use 3 (3-panels) or 2 panels.
    template : str
        The template for the figure. Defaults to "line.html_template"

    Returns
    -------
    plotting.Figure
        A figure with the band structure plot.
    """
    figure = create_figure(
        module_path=("cms_plots",),
        template=template,
        title="Band Structure",
    )

    # Create a graph of the DOS
    plot = figure.add_plot("Band_Structure")
    band_structure_plot(plot, Band_Structure)
    figure.grid_plots("Band_Structure")

    # Add the DOS plots if given
    if DOS is None:
        figure.grid_plots("Band_Structure")
    else:
        # Find the y axis
        for y_axis in plot.axes:
            if y_axis.direction == "y":
                break

        three_panels = layout == "3-panels" and any(
            ("↑" in name for name in DOS.columns)
        )
        if three_panels:
            plot = figure.add_plot("DOS-UP")
            dos_plot(
                plot,
                DOS,
                y_axis=y_axis,
                orientation="vertical",
                flipped="x",
                spin="↑",
            )

            plot = figure.add_plot("DOS-DOWN")
            dos_plot(plot, DOS, y_axis=y_axis, orientation="vertical", spin="↓")

            figure.grid_plots("DOS-UP Band_Structure - - DOS-DOWN", padx=0)
        else:
            plot = figure.add_plot("DOS")
            dos_plot(plot, DOS, y_axis=y_axis, orientation="vertical")

            figure.grid_plots("Band_Structure - - DOS", padx=0)

    return figure


def band_structure_plot(plot, Band_Structure):
    """Prepare the graph for the band structure.

    Parameters
    ----------
    plot : plotting.Plot
        Plot object for the graphs
    Band_Structure : pandas.DataFrame
        Standard dataframe containing the band structure
    """
    logger.debug("Preparing the band structure")

    xs = list(Band_Structure.index)

    # Have the full arrays, but want only the labeled points
    labels = Band_Structure["labels"].fillna("")
    labels = labels.loc[labels != ""]

    x_axis = plot.add_axis(
        "x",
        label="",
        tickmode="array",
        tickvals=list(labels.index),
        ticktext=list(labels),
    )
    y_axis = plot.add_axis("y", label="Energy (eV)", anchor=x_axis)
    x_axis.anchor = y_axis

    for label, values in Band_Structure.items():
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
            y=[f"{y:.3f}" for y in values],
            ylabel="Energy",
            yunits="eV",
            color=color,
        )


def create_figure(
    jinja_env=None, title="", template="line.graph_template", module_path=None
):
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

    if jinja_env is None:
        # The order of the loaders is important! They are searched
        # in order, so the first has precedence. This searches the
        # current package first, then looks in the main SEAMM
        # templates.
        if module_path is None:
            logger.debug("Reading graph templates from 'seamm'")
            loaders = [jinja2.PackageLoader("cms_plots")]
        else:
            logger.debug("Reading graph templates from the following modules, in order")
            loaders = []
            for module in module_path:
                paths = []
                for p in implib.files(module):
                    if p.parent.name == "templates":
                        paths.append(p)
                        break

                if len(paths) == 0:
                    logger.debug(f"\t{module} -- found no templates directory")
                else:
                    path = paths[0].locate().parent
                    logger.debug(f"\t{module} --> {path}")
                    loaders.append(jinja2.FileSystemLoader(path))

        jinja_env = jinja2.Environment(loader=jinja2.ChoiceLoader(loaders))

    figure = Figure(jinja_env=jinja_env, template=template, title=title)
    return figure


def dos(DOS, template="line.html_template"):
    """Prepare the graph for the density of states.

    Parameters
    ----------
    DOS : pandas.DataFrame
        The DOS data in a standard Pandas dataframe.
    template : str
        The template for the figure. Defaults to "line.html_template"

    Returns
    -------
    plotting.Figure
        A figure with the DOS plot.
    """
    figure = create_figure(
        module_path=("cms_plots",),
        template=template,
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
    xs = [f"{x:.3f}" for x in DOS.index]

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
                y=[f"{y:.3f}" for y in DOS[column]],
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
                x=[f"{y:.3f}" for y in DOS[column]],
                xlabel=column,
                xunits="",
                y=xs,
                ylabel="E",
                yunits="eV",
                color=color,
                dash=dash,
            )
