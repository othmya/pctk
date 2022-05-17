#!/usr/bin/env python3
# coding: utf-8

from cmath import log10
import imageio, glob, os, sys, plots_parser
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from pcplotutils import *  # TODO: Use tools4physicell instead of this

modules_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# twice because this script is in a folder within /tools4physicell

modules_path = os.path.join(modules_path, 'modules')
sys.path.append(modules_path)
from multicellds import *

python_loader_path = "/home/oth/anaconda3/lib/python3.8/site-packages/python-loader"
sys.path.append(python_loader_path)
from pyMCDS import pyMCDS # importing the class

# TODO: Add python-loader to the tools4physicell venv, cannot do it through pip as it is not in PyPI

# path in which the plots will be stored
plots_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
plots_path = os.path.join(plots_path, "transport_plots")
gif_path = os.path.join(plots_path, "transport_gif")

if not os.path.exists(plots_path):
    os.makedirs(gif_path)
    sys.stdout.write("Transport plots folder has been created.\n")
else:
    sys.stdout.write("Transport plots folder already exists.\n")

# calling the parser
parser = plots_parser.create_parser_transport()
args = parser.parse_args()


def plot_substrate(mcds, substrate, i, filename_array, type):
    """
    Script built from a tutorial from Paul Macklin on PhysiCell's python-loader package tutorial.
    Produces a matplotlib-based plot that contains a specific diffusing substrate on the microenvironment,
    and the agents from a PhysiCell simulation.

        - mcds: pyMCDS instance
        - substrate: argparser argument indicating the relevant substrate which will be shown in the plot
        - i: index to name the output figure
        - type: two options, "agents_microenv" plots both the microenvironment and the agents, while "microenv"
                plots just the microenvironment.
    """

    t = mcds.get_time()
    substrate = substrate[0]
    pos_x = mcds.data['discrete_cells']['position_x']
    pos_y = mcds.data['discrete_cells']['position_y']

#    cycle = mcds.data['discrete_cells']['cycle_model']  # an array
#    cycle = cycle.astype(int)  # convert all values to integers
    # this is done in order to use the argwhere

#    live = np.argwhere(cycle < 100).flatten()  # flatten in order to reduce to just 1 dimension
#    dead = np.argwhere(cycle >= 100).flatten()  # flatten in order to reduce to just 1 dimension

    # fetch relevant variables - only need first item, as these are constants set prior to the simulation
    initial_E_density = mcds.data['discrete_cells'][f'Initial_E_{substrate}'][0]
    initial_I_density = mcds.data['discrete_cells'][f'Initial_I_{substrate}'][0]
    actual_E_density = mcds.data["discrete_cells"][f"E_{substrate}_near"][0]
    actual_I_density = mcds.data["discrete_cells"][f"I_{substrate}"][0]
    total_volume = mcds.data["discrete_cells"]["total_volume"][0]
    nuclear_volume = mcds.data["discrete_cells"]["nuclear_volume"][0]

    if type == "agents_microenv":
        plt.clf()

        # plot microenvironment
        mcds.get_substrate_names()
        substrate_conc = mcds.get_concentrations(f'{substrate}')
        X, Y = mcds.get_2D_mesh()

        
        if initial_E_density > initial_I_density:  # ascending or descending color gradient
            plt.contourf(X, Y, substrate_conc[:, :, 0], cmap='Blues', levels=np.linspace(0.999, 1.0, 100)) #exp A
            # plt.contourf(X, Y, substrate_conc[:, :, 0], cmap='Blues', levels=np.linspace(0.999, initial_E_density, 100)) #exp B
        else:
            plt.contourf(X, Y, substrate_conc[:, :, 0], cmap='Blues', levels=np.linspace(0.0, actual_E_density + 1e-12, 100))

        # TODO: Set properly the colorbars - don't make them dynamic

        # plt.colorbar()

        # plot agents

     

        if actual_I_density > 1.0:
            scaling_factor = (log10(initial_I_density)) + 1
            scaling_factor = int(scaling_factor.real)
            actual_I_density = 10 * scaling_factor / actual_I_density # TODO: This is a hack to make the plot look better, the value is dependant on the initial I density
            if actual_I_density > 1.0:
                actual_I_density = 1.0
            
        C = np.array([actual_I_density, 0.5, 0.5])
        scatter_cytoplasm = plt.scatter(pos_x, pos_y, color=C, s=total_volume)
        scatter_nucleus = plt.scatter(pos_x, pos_y, color=(105/255, 105/255, 105/255), s=nuclear_volume)
        plt.axis('off')

        plt.title("Simulation at t=" + str(round(t, 3)) + " min", size=20, loc='left')
        filename = f"{i}.png"
        filename_array.append(filename)
        plt.savefig(gif_path + f"/{filename}", format="png", dpi=200)

    elif type == "microenv":

        plt.clf()  # clear figure
        mcds.get_substrate_names()
        substrate_conc = mcds.get_concentrations(substrate)
        X, Y = mcds.get_2D_mesh()

        # plt.clf()
        if initial_E_density > initial_I_density:  # ascending or descending color gradient
            plt.contourf(X, Y, substrate_conc[:, :, 0], cmap='Blues', levels=np.linspace(0.0, initial_E_density, 1000))
        else:
            plt.contourf(X, Y, substrate_conc[:, :, 0], cmap='Blues', levels=np.linspace(initial_E_density, 1.0, 100))

        plt.colorbar()
        plt.axis('off')
        filename = f"frame_{i}.png"
        filename_array.append(filename)
        plt.savefig(filename, format="png", dpi=300)
        plt.close()


def substrate_plot_gif(output_folder, output_path, substrate, type="agents_microenv"):
    """
    Produces a "substrate plot" for each given simulation full_save time, and joins them into an
    animated GIF file.
        - output_folder: PhysiCell output folder
        - output_path: Folder in which the subst
    """
    # TODO: Instead of using functions from pcplotutils.py, which is built on top of PhysiCell's python-loader, just use pctk from Miguel 

    filenames = []

    for xml_name in xml_frames_iterator(output_folder):
        xml_index = int(xml_name.split(".")[0].split("output")[1])
        mcds = frame_loader(xml_index, output_folder)

        # First, plot for each frame a "substrate plot"
        plot_substrate(mcds, substrate, xml_index, filenames, type)

    # Then, create GIF
    with imageio.get_writer(str(gif_path + "/substrate.gif"), mode="I") as writer:
        for filename in filenames:
            image = imageio.imread(gif_path + f"/{filename}")
            writer.append_data(image)


def ten_frames_plot(gif_output_folder):
    """
    From the "substrate plots" obtained from substrate_plot_gif(), it saves 12 frames of the PhysiCell
    simultation, and plots them in a single JPEG image.
        - gif_output_folder: Folder in which the substrate plot images from substrate_plot_gif() are stored
    """

    frames = [file for file in os.listdir(gif_output_folder) if file.endswith(".png")]
    frames_index = sorted([int(frame.split(".png")[0]) for frame in frames if not frame.startswith("ten_")])

    ten_frames = []

    for i in range(0, 110, 10):
        percent = int(np.percentile(frames_index, i))
        ten_frames.append(percent)

    # replace duplicated elements from list
    ten_frames = list(dict.fromkeys(ten_frames))

    plt.rcParams.update({'figure.figsize': (30, 30)})
    images = [mpimg.imread(gif_output_folder + f"/{str(frame)}" + ".png", format="png") for frame in ten_frames]

    fig = plt.figure(dpi=200)

    for ix, frame in enumerate(images):
        fig.add_subplot(4, 3, ix+1)
        plt.imshow(frame, interpolation="bilinear")
        plt.axis("off")

    plt.tight_layout()
    plt.savefig(gif_path + "/ten_frames.jpg")
    # save figure in PNG, PNG (transparent), PDF and SVG
    plt.savefig(gif_path + f"/ten_frames.png", format="png", dpi=200)
    plt.savefig(gif_path + f"/ten_franes_transparent.png", format="png", dpi=200, transparent=True)
    plt.savefig(gif_path + f"/ten_frames.pdf", format="pdf", dpi=200)
    sys.stdout.write("Ten frames plot saved succesfully.\n")


def delete_substrate_plots(substrate_gif_path):
    """ Deletes substrate plots from gif folder. """

    for file in glob.glob(f"{substrate_gif_path}*.png"):
        os.remove(file)


def main():
    delete_substrate_plots(gif_path)
    substrate_plot_gif(args.output_folder, gif_path, args.substrates, type="agents_microenv")
    ten_frames_plot(gif_path)


if __name__ == "__main__":
    main()
