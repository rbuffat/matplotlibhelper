'''
Created on Mar 27, 2018

@author: rene
'''

from enum import Enum
import pprint
import subprocess

import matplotlib
matplotlib.use("Agg")
from matplotlib.pyplot import tight_layout
from pint.registry import UnitRegistry

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


ureg = UnitRegistry()


class Journal(Enum):
    SPRINGER = "SPRINGER"
    ELSEVIER = "ELSEVIER"


class Columnes(Enum):
    ONE = "1"
    ONE_POINT_FIVE = "1.5"
    TWO = "2"


MAX_HEIGHT = "MAX_HEIGHT"
FONT = "FONT"
FONT_SIZE = "FONT_SIZE"

journal_config = {}
"""
Sizes from:
http://www.springer.com/computer/journal/450 > Artwork and Illustrations Guidelines > Figure Placement and Size
"""
journal_config[Journal.SPRINGER] = {Columnes.ONE: 84.0 * ureg.millimeter,
                                    Columnes.ONE_POINT_FIVE: 129.0 * ureg.millimeter,
                                    Columnes.TWO: 174.0 * ureg.millimeter,
                                    MAX_HEIGHT: 234.0 * ureg.millimeter,
                                    FONT: 'Helvetica',
                                    FONT_SIZE: 10}

"""Sizes from:
https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
"""
journal_config[Journal.ELSEVIER] = {Columnes.ONE: 90.0 * ureg.millimeter,
                                    Columnes.ONE_POINT_FIVE: 140.0 * ureg.millimeter,
                                    Columnes.TWO: 190.0 * ureg.millimeter,
                                    MAX_HEIGHT: 240.0 * ureg.millimeter,
                                    FONT: 'Helvetica',
                                    FONT_SIZE: 10}


def figsize(fig_height_mm=None,
            columnes=Columnes.TWO,
            height_scale=1.0,
            journal=Journal.SPRINGER):
    """
    Inspired from https://nipunbatra.github.io/blog/2014/latexify.html
    """

    fig_width_mm = journal_config[journal][columnes]

    if fig_height_mm is None:
        golden_mean = (np.sqrt(5.0) - 1.0) / 2.0    # Aesthetic ratio
        fig_height_mm = fig_width_mm * golden_mean

    fig_height_mm *= height_scale

    max_figh_height_mm = journal_config[journal][MAX_HEIGHT]
    if fig_height_mm > max_figh_height_mm:
        print("WARNING: fig_height too large:" + fig_height_mm +
              "so will reduce to" + fig_height_mm + "mm.")
        fig_height_mm = max_figh_height_mm

    fig_width = fig_width_mm.to(ureg.inch).magnitude
    fig_height = fig_height_mm.to(ureg.inch).magnitude

    return (fig_width, fig_height)


def init_figure(nrows=1,
                ncols=1,
                sharex=False,
                sharey=False,
                squeeze=True,
                fig_height_mm=None,
                height_scale=1.0,
                columnes=Columnes.TWO,
                journal=Journal.SPRINGER,
                disabled_spines=['top', 'right']):

    sns.set_style("whitegrid")
    sns.set_context("paper")

    """
    Credit to Paul Hobson-2
    http://matplotlib.1069221.n5.nabble.com/Problems-with-sans-serif-fonts-and-tick-labels-with-TeX-td40985.html
    """
    params = {
        'axes.labelsize': 7,
        'axes.titlesize': 7,
        'font.size': journal_config[journal][FONT_SIZE],
        'legend.fontsize': 7,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'grid.linewidth': 0.8,
        'text.usetex': True,
        'text.latex.preamble': [r'\usepackage{siunitx}'
                                r'\usepackage{helvet}',
                                r'\usepackage{sansmath}',
                                r'\sansmath',
                                r'\sisetup{detect-all}',
                                # https://tex.stackexchange.com/questions/207060/siunitx-celsius-font
                                r'\sisetup{math-celsius = {}^{\circ}\kern-\scriptspace C}'],
        'text.latex.unicode': True,
        'font.family': 'sans-serif',
        'font.sans-serif': journal_config[journal][FONT],
        'grid.linestyle': ':',
        'legend.frameon': True,
    }

    matplotlib.rcParams.update(params)

    f, axs = plt.subplots(nrows=nrows,
                          ncols=ncols,
                          sharex=sharex,
                          sharey=sharey,
                          squeeze=squeeze,
                          figsize=figsize(fig_height_mm=fig_height_mm,
                                          columnes=columnes,
                                          height_scale=height_scale,
                                          journal=journal))

    for ax in f.axes:
        for spine in disabled_spines:
            ax.spines[spine].set_visible(False)

    return f, axs


def save_figure(outpath, dpi=600, tight_layout=True):
    if tight_layout:
        plt.tight_layout()
    plt.savefig(outpath,
                dpi=dpi,
                transparent=False)

    plt.savefig(outpath.replace('.png', '-transparent.png'),
                dpi=dpi,
                transparent=True)

    plt.savefig(outpath.replace('.png', '.pdf'))

    subprocess.run(["pdfcrop",
                    outpath.replace('.png', '.pdf'),
                    outpath.replace('.png', '-crop.pdf')])
    plt.close()


if __name__ == '__main__':
    f, ax = init_figure(nrows=1,
                        ncols=1,
                        columnes=Columnes.TWO)

    xs = np.arange(1.0, 10.0)
    ys = xs**2

    ax.plot(xs, ys)
    ax.set_title("A title")
    ax.set_xlabel(r"X [$\si{\mega\tonne}$]")
    ax.set_ylabel(r"Y [$\si{\celsius}$]")

    save_figure(outpath=r"/tmp/test.png")
