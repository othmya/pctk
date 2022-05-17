#!/usr/bin/env python3
# coding: utf-8
import glob, subprocess, shutil
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
substrates = args.substrates

print(substrates)

for substrate in substrates:
    specific_simulation_path = os.path.join(images_path, f"{args.transport}_{substrate}_exp")
    if not os.path.exists(specific_simulation_path):
        os.makedirs(specific_simulation_path)



# TODO: Make it more user-friendly - variables from PhysiCell should include specific tags


def get_relevant_constants(full_df, substrates, transport_mechanism):
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


def get_relevant_transport_dfs(full_df, substrates, transport_mechanism):
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

    print("Obtaining relevant dataframes...")

    full_df.reset_index(level=0, inplace=True)  # input df has "Time (min)" as index
    full_df = full_df[1:]  # Avoid time 0.0, no information on the dynamic stored here
    total_df_subsets = []
    empty_dfs = []


    for substrate in substrates:
        print(f"Obtaining data for substrate: {substrate}")

        try: # try-except block could be removed
            full_df[f"total_{substrate}"] = round(full_df[f"total_{substrate}"], 5)
        except:
            full_df[f"total_net_{substrate}"] = round(full_df[f"total_net_{substrate}"], 5)

        # This should be done with the loc method, replace and update

        melted_full_df = full_df.melt('time', var_name='column', value_name='value')

        density_data = melted_full_df.loc[(melted_full_df["column"] == f"I_{substrate}") | (melted_full_df["column"] == f"E_{substrate}_near")]
        flux_data = melted_full_df.loc[(melted_full_df["column"] == f"{substrate}_flux") ]  # | (melted_full_df["column"] == f"sd_flux_{substrate}")
        delta_data = melted_full_df.loc[(melted_full_df["column"] == f"D_{substrate}")]
        total_net_amount_data = melted_full_df.loc[(melted_full_df["column"] == f"total_{substrate}")]

        # Basic set of information for every simulation
        df_subsets = [density_data, flux_data, delta_data, total_net_amount_data]

        # Additional info depending on the transport system

        # A. Simple diffusion
        adjusted_flux_data = melted_full_df.loc[(melted_full_df["column"] == f"adjusted_{substrate}_flux")]
        df_subsets.append(adjusted_flux_data)

        # B. FDC
        substrate_and_receptor_density_data = melted_full_df.loc[(melted_full_df["column"] == f"Rc_{substrate}") |
                                                                 (melted_full_df["column"] == f"Rcb_{substrate}")]


        total_receptor_density_data = melted_full_df.loc[(melted_full_df["column"] == f"total_Rc_{substrate}")]

        receptor_data = melted_full_df.loc[(melted_full_df["column"] == f"Rc_{substrate}") |
                                           (melted_full_df["column"] == f"Rcb_{substrate}") |
                                           (melted_full_df["column"] == f"total_Rc_{substrate}")]

        kinetic_data = melted_full_df.loc[(melted_full_df["column"] == f"{substrate}_binding_component") |
                                          (melted_full_df["column"] == f"{substrate}_recycling_component") |
                                          (melted_full_df["column"] == f"{substrate}_endocytosis_component") |
                                          (melted_full_df["column"] == f"{substrate}_internal_recycling_component") ]

        df_subsets.append(substrate_and_receptor_density_data)
        df_subsets.append(total_receptor_density_data)
        df_subsets.append(kinetic_data)
        df_subsets.append(receptor_data)



        # C.1 FDCh - Aquaporin-like
        adjusted_flux_data = melted_full_df.loc[(melted_full_df["column"] == f"adjusted_{substrate}_flux")]
        effective_surface_data = melted_full_df.loc[(melted_full_df["column"] == "A_effective")]
        num_receptors_data = melted_full_df.loc[(melted_full_df["column"] == "n_Rc")]

        df_subsets.append(adjusted_flux_data)
        df_subsets.append(effective_surface_data)
        df_subsets.append(num_receptors_data)



        # C.2 FDCh - Ligand-gated

        RL_component_data = melted_full_df.loc[(melted_full_df["column"] == f"I_Rc") |
                                               (melted_full_df["column"] == f"I_Lg") |
                                               (melted_full_df["column"] == f"I_RL") | 
                                               (melted_full_df["column"] == f"I_total_Rc")]

        RL_kinetics_data = melted_full_df.loc[(melted_full_df["column"] == "RL_binding_component") |
                                              (melted_full_df["column"] == "RL_unbinding_component")]

        hill_cooperativity_data = melted_full_df.loc[(melted_full_df["column"] == "hill_cooperativity")]
        gompertz_data = melted_full_df.loc[(melted_full_df["column"] == "gompertz_function")]

        df_subsets.append(RL_component_data)
        df_subsets.append(RL_kinetics_data)
        df_subsets.append(hill_cooperativity_data)
        df_subsets.append(gompertz_data)

        # C. FDCh - Aquaporin-like

        # C.3. FDCh - Voltage-gated

        # D. Primary active

        ATP_ADP_density_data = melted_full_df.loc[
            (melted_full_df["column"] == f"I_ATP") | (melted_full_df["column"] == f"I_ADP")]

        receptor_bound_data = melted_full_df.loc[
            (melted_full_df["column"] == f"Rcb_{substrate}") | (melted_full_df["column"] == f"Rcb_ATP")]

        total_receptor_density_data = melted_full_df.loc[(melted_full_df["column"] == f"Rc_{substrate}_total") |
                                                         (melted_full_df["column"] == f"Rcb_{substrate}_total") |
                                                         (melted_full_df["column"] == f"Rc_total")]

        substrate_component_data = melted_full_df.loc[(melted_full_df["column"] == f"binding_component") |
                                                      (melted_full_df["column"] == f"recycling_component") |
                                                      (melted_full_df["column"] == f"movement_component") |
                                                      (melted_full_df["column"] == f"endocytosis_component") |
                                                      (melted_full_df["column"] == f"internal_binding_component")]

        ATP_component_data = melted_full_df.loc[(melted_full_df["column"] == f"ATP_binding_component") |
                                                (melted_full_df["column"] == f"ATP_unbinding_component") |
                                                (melted_full_df["column"] == f"ATP_hydrolisis_component") |
                                                (melted_full_df["column"] == f"ADP_recycling_component")]

        df_subsets.append(ATP_ADP_density_data)
        df_subsets.append(receptor_bound_data)
        df_subsets.append(total_receptor_density_data)
        df_subsets.append(substrate_component_data)
        df_subsets.append(ATP_component_data)

        # E. Secondary active


        both_substrates = melted_full_df.loc[(melted_full_df["column"] == f"I_sY") |
                                                      (melted_full_df["column"] == f"E_sY_near") |
                                                      (melted_full_df["column"] == f"I_sK") |
                                                      (melted_full_df["column"] == f"E_sK_near")]

        both_fluxes = melted_full_df.loc[(melted_full_df["column"] == f"sY_flux") |
                                             (melted_full_df["column"] == f"sK_flux") ]

        df_subsets.append(both_substrates)
        df_subsets.append(both_fluxes)



        density_data.to_csv(f"{args.output_folder}/density_data.csv", encoding="utf-8", header=True)


        for subset in df_subsets:
            if not subset.empty:
                total_df_subsets.append(subset)

    del full_df

    return total_df_subsets


def transport_timecourse_plots(dataframe_array, simulation_info, transport_mechanism, individual_plots=False):
    """
    Using as an input an array of pandas.DataFrame obtained from get_relevant_transport_dfs(), different
    seaborn-based plots for a specific transport mechanism are stored in PNG format.
        - The simulation information string from get_relevant_constants() can be employed, but is deprecated for now.
        - Transport_mechanism refers to the argparser argument that indicates the mechanism of transport.
        - The individual_plots conditions indicates if the set of plots share the same X-axis or are actually
          separate plots.
    """

    # journal-plotting format
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300
    #mpl.rcParams['font.family'] = 'Avenir'
    plt.rcParams['font.size'] = 22
    plt.rcParams['axes.linewidth'] = 1.4

    for substrate in substrates:

        legend_array = [

            [f"Internal {substrate} density", f"External {substrate} density"],
            [f"{substrate} flux (amol/min)"], [f"{substrate} concentration gradient"],
            [f"Total net amount of {substrate} (amol)"],

            [f"Adjusted {substrate} flux (amol/min)"],

         



        ]

#    [f"Bound {substrate} Receptor density", f"Unbound {substrate} Receptor density"],
#             [f"Total {substrate} Receptor density"],
#             [f"Bound {substrate} Receptor density", f"Unbound {substrate} Receptor density", f"Total {substrate} Receptor density"],
        
        # for simple_diffusion

    # this legend array is not really dynamic - but are there any other options?

    #if transport_mechanism == "simple_diffusion":
    #elif transport_mechanism == "facilitated_diffusion_carrier" or transport_mechanism == "cytotoxic_carrier":
    #    legend_array.append([f"{substrate} unbound receptor density (mM)", f"{substrate} bound receptor density (mM)"])
    #    legend_array.append([f"Total {substrate} receptor denisty (amol/um³)"])

    plt.clf()

    print("Making plots...")

    # if not individual_plots:
    #     #fig, axs = plt.subplots(len(dataframe_array), sharex=True, figsize=(9, 30), dpi=200)  # fine-tune this
    #     pass
    # else:
    #     pass
    #     #fig, axs = plt.subplots(len(dataframe_array), sharex=False, figsize=(9, 30), dpi=200)

    for ix, df in enumerate(dataframe_array):
        plt.plot(figsize=(15,15))
        sns.set(style="ticks", palette="deep")
        sns.set_context('paper')

        g = sns.lineplot(data=df, x="time", y="value",
                         hue="column", style="column",
                         markers=False, linewidth=1.7)
        try:
            if len(legend_array[ix]) > 1:
                g.legend(title="", labels=legend_array[ix], fontsize=13)
            else:
                g.legend([], [], frameon=False)
        except IndexError:
            g.legend(title="", fontsize=16)
        # (1, 0.85) for right-aligned
        # (0.95, 0.15) for inside-lower, (0.95, 0.85) for inside-upper
        try:
            if len(legend_array[ix]) == 1:
                g.set_ylabel(legend_array[ix][0], fontsize=15)
                g.legend([], [], frameon=False)
            else:
                g.set_ylabel("Density (mM)", fontsize=15)
        except IndexError:
            g.set_ylabel("value", fontsize=15)


        g.set_yticklabels(g.get_yticks(), size = 11)
        g.set_xticklabels(g.get_xticks(), size = 11)
        
        # after plotting the data, format the labels
        current_values = plt.gca().get_yticks()
        # using format string '{:.0f}' here but you can choose others
        # plt.gca().set_yticklabels(['{:.2f}'.format(x) for x in current_values]) # 2 decimals
        plt.gca().set_yticklabels(['{:.2e}'.format(x) for x in current_values]) # scientific notation

        g.legend(title="", fontsize=16)
        # g.set_ylabel("value", fontsize=15)
        g.set_xlabel("Simulation time (min)", fontsize=17)

        # save figure in PNG, PNG (transparent), PDF and SVG
        plt.savefig(specific_simulation_path + f"/transport_plot_{transport_mechanism}_{ix}.png", format="png", dpi=300, bbox_inches="tight")
        plt.savefig(specific_simulation_path + f"/transport_plot_{transport_mechanism}_{ix}_transparent.png", format="png", dpi=300, transparent=True, bbox_inches="tight")
        plt.savefig(specific_simulation_path + f"/transport_plot_{transport_mechanism}_{ix}.pdf", format="pdf", dpi=300, bbox_inches="tight")

        plt.clf()

        #plt.tight_layout()

        #if individual_plots == False:
        #    plt.savefig(images_path + "/joint_transport_plots.png", format="png")
        #    sys.stdout.write("Joint transport parameters plot saved successfully.\n")
        #else:
        #    plt.savefig(images_path + "/individual_transport_plots.png", format="png")
        #    sys.stdout.write("Individual plots saved successfully.\n")




def density_combined_plot(full_df, substrate, experiment_type):
    """
    Similar to transport_timecourse_plots(), but refers just to the internal and external
    densities of a provided substrate.
        - full_df: Simulation information pandas.DataFrame obtained from multicellds.full_cell_info_df()
        - substrate: argparser argument --substrate
    """
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300
    # mpl.rcParams['font.family'] = 'Avenir'
    plt.rcParams['font.size'] = 30
    plt.rcParams['axes.linewidth'] = 1.5

    # Cannot work with the melted dataframe from get_relevant_transport_dfs(), have to work
    # with the original one, but keeping just the Internal and External density columns

    density_df = full_df[["time", f"I_{substrate}", f"E_{substrate}_near"]][1:]

    total_I_substrate = len(density_df[f"I_{substrate}"])

    initial_I_substrate = density_df[f"I_{substrate}"][1]
    final_I_substrate = density_df[f"I_{substrate}"][total_I_substrate - 1]
    range_I_substrate = abs(initial_I_substrate - final_I_substrate)

    initial_E_substrate = density_df[f"E_{substrate}_near"][1]
    final_E_substrate = density_df[f"E_{substrate}_near"][total_I_substrate - 1]
    range_E_substrate = abs(initial_E_substrate - final_E_substrate)

    plt.clf()
    plt.figure(dpi=300, figsize=(9, 6))  # figsize(14, 4)
#    plt.figtext(x=0.14, y=0.89, s=simulation_info, wrap=True)

    ax = sns.set(style="ticks", palette="deep")
    ax = sns.set_context('paper')

    ax = sns.lineplot(x="time", y=f"I_{substrate}", data=density_df,
                      legend=False, linestyle="solid", color="b", linewidth=1.5)

    if experiment_type == "A":
        ax.set_ylim([initial_I_substrate, final_I_substrate + range_I_substrate] )
    elif experiment_type == "B":
        ax.set_ylim([final_I_substrate - range_I_substrate, initial_I_substrate] )
    elif experiment_type == "none":
        pass
    ax.set_ylabel(f"Internal {substrate} density (mM)", color="b", fontsize=16)


    ax.tick_params(axis="y")
    ax2 = ax.twinx()

    ax2 = sns.lineplot(x="time", y=f"E_{substrate}_near", data=density_df,
                       legend=False, linestyle="--", color="orangered", linewidth=1.5)

    if experiment_type == "A":
        ax2.set_ylim([final_E_substrate + (final_E_substrate - initial_E_substrate), initial_E_substrate] )
    elif experiment_type == "B":
        ax2.set_ylim([initial_E_substrate, final_E_substrate + range_E_substrate] )
    elif experiment_type == "none":
        pass

    ax2.set_ylabel(f"External {substrate} density (mM)",  color="orangered", fontsize=16)
    ax2.tick_params(axis="y")
    ax.set_xlabel("Simulation time (min)", fontsize=16)

    # save figure
    plt.savefig(specific_simulation_path + f"/density_plot_{substrate}.png", format="png", dpi=300, bbox_inches="tight")
    plt.savefig(specific_simulation_path + f"/density_plot_{substrate}_transparent.png", format="png", dpi=300, transparent=True, bbox_inches="tight")
    plt.savefig(specific_simulation_path + f"/density_plot_{substrate}.pdf", format="pdf", dpi=300, bbox_inches="tight")

    sys.stdout.write("Density plot saved succesfully.\n")

    # Do the same for I_ATP, I_ADP
    try:
        ATP_ADP_df = full_df[["time", f"I_ATP", f"I_ADP"]][0:]
        plt.clf()
        plt.figure(figsize=(14, 4), dpi=200)
        #    plt.figtext(x=0.14, y=0.89, s=simulation_info, wrap=True)

        ax = sns.set(style="ticks", palette="Paired")
        ax = sns.set_context('paper')

        ax = sns.lineplot(x="time", y=f"I_ATP", data=ATP_ADP_df,
                          legend=False, color="b")
        ax.set_ylabel("ATP (mM)", color="b")
        ax.tick_params(axis="y")
        ax2 = ax.twinx()
        ax2 = sns.lineplot(x="time", y=f"I_ADP", data=ATP_ADP_df, legend=False, color="g")
        ax2.set_ylabel("ADP (mM)", color="g")
        ax2.tick_params(axis="y")
        ax2.set_xlabel("Simulation time (min)")

        plt.savefig(specific_simulation_path + "/ADP_ATP_density.png", format="png")
        sys.stdout.write("ATP Density plot saved succesfully.\n")
    except KeyError:
        pass




def cancer_healthy_plot(full_df):
    """
    """
    # Cannot work with the melted dataframe from get_relevant_transport_dfs(), have to work
    # with the original one, but keeping just the Internal and External density columns

    total_healthy_cancer_df = full_df[["time", "total_healthy_cells", f"total_cancer_cells"]][1:]
    melted_healthy_cancer_df = total_healthy_cancer_df.melt('time', var_name='column', value_name='value')


    plt.clf()
    sns.set(style="ticks", palette="Paired")
    sns.set_context('paper')

    g = sns.lineplot(data=melted_healthy_cancer_df, x="time", y="value",
                     hue="column", legend="brief", markers=True, linewidth=3)

    g.legend(labels=["Healthy cells", "Cancer cells"])
    # (1, 0.85) for right-aligned
    # (0.95, 0.15) for inside-lower, (0.95, 0.85) for inside-upper

    g.set_ylabel("Net amount")
    g.set_xlabel("Simulation time (min)", fontsize=15)

    plt.savefig(specific_simulation_path + "/healthy_cancer.png", format="png")
    sys.stdout.write("Net value of healthy and cancer cells plot saved succesfully.\n")



def main():
    """ Full pipeline for plotting """

    ## Save figures in specific folder within images_path

    mcds = MultiCellDS(output_folder=args.output_folder)
    simulation_df = mcds.full_cell_info_df(group_by_time=True)  # group_by argument is deprecated

    transport_dfs = get_relevant_transport_dfs(simulation_df, args.substrates, args.transport)
    #simulation_info = get_relevant_constants(simulation_df, args.substrate, args.transport)
    simulation_info = "null"

    transport_timecourse_plots(transport_dfs, simulation_info, args.transport)
    transport_timecourse_plots(transport_dfs, simulation_info, args.transport, individual_plots=True)

    for substrate in substrates:
        density_combined_plot(simulation_df, substrate, experiment_type="A") # Indicate type of experiments

    try:
        cancer_healthy_plot(simulation_df)
    except KeyError:
        print("No healthy & cancer plot, not indicated in arguments.\n")

def get_just_fulldf():
    """
        Small pipeline, get only the full data from the output folder. Employed for when
        unit testing.
    """

    # get PBoSS parent directory, as there are different output folders
    physicell_dir = os.path.dirname(args.output_folder) #output folder
    files_dir = os.path.dirname(physicell_dir) # PBoSS folder
    top_dir = os.path.dirname(files_dir) # TFM folder -- Watch out!!

    unit_test_folder = [file for file in os.listdir(top_dir) if file == "unit_testing_outputs"][0]
    unit_test_path = os.path.join(top_dir, unit_test_folder)
    unit_test_path_specific = os.path.join(unit_test_path, f"{args.transport}", "hill_index/")

    if os.path.exists(unit_test_path_specific):
        shutil.rmtree(unit_test_path_specific)  # would be best to check if this actually exists
        os.makedirs(unit_test_path_specific)
    else:
        os.makedirs(unit_test_path_specific)

    os.chdir(files_dir)

    for file in sorted(glob.glob("output_*")):

        file_string = file.split(".")[0]
        value = int(file_string.split("_")[1])

        mcds = MultiCellDS(output_folder=file)
        mcds.full_cell_info_df(group_by_time=True)

        # Copy to unit test folder
        #subprocess.run([f"cp {files_dir}/{file}/full_data_merged.csv {unit_test_path_specific}"], cwd=top_dir, shell=True)
        subprocess.run([f"cp {files_dir}/{file}/full_data_merged_grouped_time.csv {unit_test_path_specific}"], cwd=top_dir, shell=True)

        # Change name
        #subprocess.run([f"mv {unit_test_path_specific}/full_data_merged.csv {unit_test_path_specific}/fci_N{value}.csv"], cwd=top_dir, shell=True)
        subprocess.run([f"mv {unit_test_path_specific}/full_data_merged_grouped_time.csv {unit_test_path_specific}/fci_N{value}_grouped_time.csv"], cwd=top_dir, shell=True)


if __name__ == "__main__":

    if args.just_df is True:
        get_just_fulldf()
    else:
        sys.stderr.write("Running a normal simulation")
        main()


