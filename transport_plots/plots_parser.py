#!/usr/bin/env python3
# coding: utf-8

import argparse, os, sys

modules_path = os.path.dirname(os.path.realpath(__file__))
modules_path = os.path.dirname(modules_path)  # twice because this script is in a folder within /tools4physicell
modules_path = os.path.join(modules_path, 'modules')
sys.path.append(modules_path)

from multicellds import *



def create_parser_transport():
    """
    Simple parser that makes plotting the transport dynamics more user-friendly.
    """
    parser = argparse.ArgumentParser(description="Produce different plots for the different transport mechanisms")

    parser.add_argument("--transport_mechanism", action="store", dest="transport",
                        choices=("simple_diffusion", "facilitated_diffusion_carrier"),
                        help="Type of transport mechanism for which the plots will be produced")

    parser.add_argument("--join", action="store", dest="join_plots", default=False,
                        help="Join the different plots into one single figure")

    parser.add_argument("--substrate", action="store", dest="substrate", default=None,
                        help="Indicate the substrate for which the transport dynamics will be plotted")

    parser.add_argument("output_folder", action="store", help="folder were the data is stored, usually the PhysiCell output folder.")

    parser.add_argument("--figout", action="store", dest="fig_fname", default="./transport_plot.png",
                        help="Filename to save the plot")

    parser.add_argument("--csvout", action="store", dest="csv_fname", default="./transport_df.csv",
                        help="Filename to store the summary table used for the plot")



    return parser