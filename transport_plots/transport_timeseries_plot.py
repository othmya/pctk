#!/usr/bin/env python3
# coding: utf-8

import os, sys
import matplotlib.pyplot as plt
import seaborn as sns
import plots_parser

modules_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# twice because this script is in a folder within /tools4physicell
modules_path = os.path.join(modules_path, 'modules')
sys.path.append(modules_path)
from multicellds import *

# path in which the plots will be stored
plots_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
plots_path = os.path.join(plots_path, "transport_plots")
images_path = os.path.join(plots_path, "plots")


if not os.path.exists(images_path):
    os.makedirs(images_path)
    sys.stdout.write("Transport plots folder has been created.\n")
else:
    sys.stdout.write("Transport plots folder already exists.\n")

# calling the parser
parser = plots_parser.create_parser_transport()
args = parser.parse_args()
substrate = args.substrate


# TODO: Make it more user-friendly - variables from PhysiCell should include specific tags


def get_relevant_constants(full_df, substrate, transport_mechanism):
    """
    Obtain relevant constants (initial internal density, initial external density, diffusion coefficient)
    for a simulation in both a string format and a .txt file ("simulation_info.txt") that describes them.

    Depending on the transport mechanism, some more relevant constants might be included:
        - Simple diffusion: Includes permeability coefficient (k)
        - Facilitated diffusion carrier: Includes kinetic parameters, and receptor (bound and unbound) densities

    Returns a string that contains the info, and a simulation_info.txt file located within the folder of the script
    """

    subset_full_df = full_df[:1]  # constants are set from time 0.0, so we would just need this one row

    Initial_I_density = [subset_full_df[f"Initial_I_{substrate}"].values][0][0]
    str1 = f"Initial Internal {substrate} conc. (mM) = {Initial_I_density} um³/min\n"

    Initial_E_density = [subset_full_df[f"Initial_E_{substrate}"].values][0][0]
    str2 = f"Initial External {substrate} conc. (mM) = {Initial_E_density} um³/min\n"

    diffusion_coefficient = [subset_full_df[f"DC_{substrate}"].values][0][0]
    str3 = f"{substrate} Diffusion coefficient (D) (mM) = {diffusion_coefficient} um³/min\n"

    base_string = str1 + str2 + str3  # these parameters are common to all transport mechanisms

    if transport_mechanism == "simple_diffusion":
        permeability_coeff = [subset_full_df[f"k_{substrate}"].values][0][0]
        str4 = f"{substrate} Permeability coefficient (k) (mM) = {permeability_coeff} um³/min\n"

        with open(str(images_path + "/simulation_info.txt"), "w+") as outfile:
            outfile.write(str(base_string + str4))
        sys.stdout.write("Simulation info saved.\n")
        outfile.close()

        return str(base_string + str4)

    elif transport_mechanism == "facilitated_diffusion_carrier":
        pass # TODO: Add kinetic parameters, bound and unbound receptor densities


def get_relevant_transport_dfs(full_df, substrate, transport_mechanism):
    """
    Using as an input the pandas.DataFrame obtained from multicellds.full_cell_info_df(), different
    dataframe subsets for relevant simulation variables are obtained.

    The substrate parameter refers to the argparser argument that indicates the relevant substrate.
    The transport_nechanism parameter refers to the argparser argument that indicates the specific transport mechanism.

    The common variables for all transport mechanisms are: the internal and external substrate density,
    the substrate flux into or from the agents, the concentration grande and the total net amount of said
    substrate.

    For each specific transport mechanism, specific variables are also stored:
        - Simple diffusion: Includes the adjusted flux data.
        - Facilitated diffusion carrier: Includes bound and unbound receptor densities

    Returns an array of pandas.DataFrame objects, each one referred to a specific variable.

    """

    full_df.reset_index(level=0, inplace=True)  # input df has "Time (min)" as index
    full_df = full_df[1:]  # Avoid time 0.0, no information stored here
    full_df[f"total_{substrate}"] = round(full_df[f"total_{substrate}"], 3)
    # This should be done with the loc method, replace and update

    melted_full_df = full_df.melt('Time (min)', var_name='column', value_name='value')
    density_data = melted_full_df.loc[(melted_full_df["column"] == f"I_{substrate}") | (melted_full_df["column"] == f"E_{substrate}" )]
    flux_data = melted_full_df.loc[(melted_full_df["column"] == f"{substrate}_flux")]  # TODO: change the name in PhysiCell to "flux"
    delta_data = melted_full_df.loc[(melted_full_df["column"] == f"D_{substrate}")]
    total_net_amount_data = melted_full_df.loc[(melted_full_df["column"] == f"total_{substrate}")]

    df_subsets = [density_data, flux_data, delta_data, total_net_amount_data]
    del full_df

    if transport_mechanism == "simple_diffusion":
        adjusted_flux_data = melted_full_df.loc[(melted_full_df["column"] == f"adjusted_{substrate}_flux")]   # TODO: change the name to "adjusted_flux" in PhysiCell
        df_subsets.append(adjusted_flux_data)
        return df_subsets

    elif transport_mechanism == "facilitated_diffusion_carrier":
        substrate_and_receptor_density_data = melted_full_df.loc[(melted_full_df["column"] == f"I_{substrate}") |
                                                                 (melted_full_df["column"] == f"E_{substrate}" ) |
                                                                 (melted_full_df["column"] == f"Rc_{substrate}") |
                                                                 (melted_full_df["column"] == f"Rcb_{substrate}") ]

        total_receptor_density_data = melted_full_df.loc[(melted_full_df["column"] == f"total_Rc_{substrate}")]

        df_subsets.append(substrate_and_receptor_density_data)
        df_subsets.append(total_receptor_density_data)

        return df_subsets


def transport_timecourse_plots(dataframe_array, simulation_info, transport_mechanism, individual_plots=False):
    """
    Using as an input an array of pandas.DataFrame obtained from get_relevant_transport_dfs(), different
    seaborn-based plots for a specific transport mechanism are stored in PNG format.
        - The simulation information string from get_relevant_constants() can be employed, but is deprecated for now.
        - Transport_mechanism refers to the argparser argument that indicates the mechanism of transport.
        - The individual_plots conditions indicates if the set of plots share the same X-axis or are actually
          separate plots.
    """

    legend_array = [[f"Internal {substrate} density (mM)", f"External {substrate} density (mM)"],
                    [f"{substrate} flux (amol/min)"],
                    [f"{substrate} concentration gradient (mM)"], [f"Total net amount of {substrate} (amol)"]]

    # this legend array is not really dynamic - but are there any other options?

    if transport_mechanism == "simple_diffusion":
        legend_array.append(f"Adjusted {substrate} flux (amol/min)")
    elif transport_mechanism == "facilitated_diffusion_carrier":
        legend_array.append([f"Internal {substrate} density (mM)", f"External {substrate} density (mM)",
                             f"{substrate} receptor density (mM)", f"{substrate} bound receptor density (mM)"])

    plt.clf()

    if not individual_plots:
        fig, axs = plt.subplots(len(dataframe_array), sharex=True, figsize=(14, 16), dpi=200)  # fine-tune this
    else:
        fig, axs = plt.subplots(len(dataframe_array), sharex=False, figsize=(14, 16), dpi=200)

#    plt.figtext(x=0.14, y=0.89, s=simulation_info, wrap=True)
    # deprecated info string, not that useful

    for ix, df in enumerate(dataframe_array):
        sns.set(style="ticks", palette="Paired")
        sns.set_context('paper')

        g = sns.lineplot(data=df, x="Time (min)", y="value",
                         hue="column", legend="brief", ax=axs[ix],
                         markers=True, linewidth=3)

        g.legend(loc='center right', bbox_to_anchor=(0.95, 0.85), labels=legend_array[ix])
        # (1, 0.85) for right-aligned
        # (0.95, 0.15) for inside-lower, (0.95, 0.85) for inside-upper

        g.set_ylabel("")
        #plt.xticks(np.arange(min(df["Time (min)"]), max(df["Time (min)"]), 0.2))
        g.set_xlabel("Simulation time (min)", fontsize=12)

    plt.tight_layout()

    if individual_plots == False:
        plt.savefig(images_path + "/joint_transport_plots.png", format="png")
        sys.stdout.write("Joint transport parameters plot saved successfully.\n")
    else:
        plt.savefig(images_path + "/individual_transport_plots.png", format="png")
        sys.stdout.write("Individual plots saved successfully.\n")


def density_combined_plot(full_df, substrate):
    """
    Similar to transport_timecourse_plots(), but refers just to the internal and external
    densities of a provided substrate.
        - full_df: Simulation information pandas.DataFrame obtained from multicellds.full_cell_info_df()
        - substrate: argparser argument --substrate
    """
    # Cannot work with the melted dataframe from get_relevant_transport_dfs(), have to work
    # with the original one, but keeping just the Internal and External density columns

    density_df = full_df[["Time (min)", f"I_{substrate}", f"E_{substrate}_near"]][1:]

    plt.clf()
    plt.figure(figsize=(14, 4), dpi=200)
#    plt.figtext(x=0.14, y=0.89, s=simulation_info, wrap=True)

    ax = sns.set(style="ticks", palette="Paired")
    ax = sns.set_context('paper')

    ax = sns.lineplot(x="Time (min)", y=f"I_{substrate}", data=density_df,
                      legend=False, color = "b")
    ax.set_ylabel("Internal density (mM)", color = "b")
    ax.tick_params(axis="y")
    ax2 = ax.twinx()
    ax2 = sns.lineplot(x="Time (min)", y=f"E_{substrate}_near", data=density_df,
                    legend=False, color = "g")
    ax2.set_ylabel("External density (mM)", color = "g")
    ax2.tick_params(axis="y", color="g")
    ax2.set_xlabel("Simulation time (min)", fontsize=15)

    plt.savefig(images_path + "/density_plot.png", format="png")
    sys.stdout.write("Density plot saved succesfully.\n")


def main():
    """ Full pipeline for plotting """

    mcds = MultiCellDS(output_folder=args.output_folder)
    simulation_df = mcds.full_cell_info_df(group_by_time=True)

    transport_dfs = get_relevant_transport_dfs(simulation_df, args.substrate, args.transport)
    simulation_info = get_relevant_constants(simulation_df, args.substrate, args.transport)

    transport_timecourse_plots(transport_dfs, simulation_info, args.transport)
    transport_timecourse_plots(transport_dfs, simulation_info, args.transport, individual_plots=True)
    density_combined_plot(simulation_df, args.substrate)


if __name__ == "__main__":
    main()



