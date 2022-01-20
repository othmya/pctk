import os, sys
import plots_parser

modules_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
modules_path = os.path.join(modules_path, 'modules')
sys.path.append(modules_path)
from multicellds import *


sys.path.append("/home/oth/anaconda3/lib/python3.8/site-packages/python-loader")
from pyMCDS import pyMCDS # importing the pyMCDS class


def frame_loader(frame, output_folder):
    """
    Given a specific frame and the folder where the PhysiCell output is stored, it returns
    a pyMCDS instance.
    """

    output_folder = str(output_folder)
    frame_files = [file for file in os.listdir(output_folder) if file.endswith(".xml") and file.startswith("output")]
    frame_files.sort()
    mcds = pyMCDS(frame_files[frame], output_folder)

    return mcds


def xml_frames_iterator(output_folder, ):
    """ A generator function that allows for iteration over all XML files in the PhysiCell output folder. """

    # nested list comprehension to get array of .xml files
    filenames = [[name for name in files if name.startswith("output") and name.endswith(".xml")] \
                 for root, dirs, files in os.walk(output_folder)][0]
    filenames.sort()

    for filename in filenames:
        yield filename