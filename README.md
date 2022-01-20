
# Introduction
tools4physicell is tiny project that aims to develop tools to analysis agent-based simulation of multicellular systems produced by the multi-scale modeling framework PhysiCell ([http://physicell.org/](http://physicell.org/)) developed by Paul Macklin at MathCancer. Although there are already available tools for handling PhysiCell outputs here we are gathering together and organizing those pieces of python code that its been anyhow, requrrently useful in the past, when dealing with PhysiCell. In general, most of the functionalities provided by this toolkit also handles the output format of the PhysiCell forked version PhysiBoSS developed at Institute Curie [https://github.com/sysbio-curie/PhysiBoSS](https://github.com/sysbio-curie/PhysiBoSS).

# Installation
tools4physicell is pure python code with few dependencies and only requieres the installation of some python modules. 
### On linux systems using virtualenv + pip
- 1  create a new virtual environemnt, activate it and install the requirments
~~~~
virtualenv -p python3 myenv
source myenv/bin/activate
pip install -r requirements.txt
~~~~
Thats it! If you want to run the script from any location add the base folder to your PATH environmental variable. And if you want to access the multicellds class, add modules/multicellds.py to your PYTHONPATH.

The last step for generating 3D renders of cell from .pov files, it is done using Persistence of Vision Ray Tracer (POV-Ray). POV-Ray is a cross-platform ray-tracing standalone program that generates images from a text-based scene description. POV-Ray is open source () and can be freely obtaind from: <br>
* [http://www.povray.org/download/](http://www.povray.org/download/)

# MultiCellDS class

Upcoming

# Ready-to-run scripts
There are some ready-to-run scripts that can be used to summarize and visualize PhysiCell/PhysiBoSS simulation. These scripts allow to generate cell vs time plots as well 3D renders for time snapshots.

## Ploting time course: plot_time_course.py
The script plot_time_course.py plot number of cells vs time grouping cell by phase (alive, necrotic, apoptotic) <br>
The color mapping can be easily customized to represent other cell-agent variables (eg. color mutants or other cell states)
	
~~~~
usage: plot_time_course.py [-h] [--format {physicell,physiboss}]
                           [--figout FIG_FNAME] [--csvout CSV_FNAME]
                           data_folder

Plot total cell grouped as Alive/Necrotic/Apoptotic vs Time

positional arguments:
  data_folder           folder were the data is stored

optional arguments:
  -h, --help            show this help message and exit
  --format {physicell,physiboss}
                        Format of the input data
  --figout FIG_FNAME    File name to save the plot
  --csvout CSV_FNAME    File name to store the summary table used for the plot	
~~~~

#### Examples
`plot_time_course.py output_test --format physiboss --figout physibos_time_plot.png`

`plot_time_course.py output_test --format physicell --figout physicell_time_plot.png`


## Generations of pov files for 3D rendering: povwriter.py
The script povwriter.py reads  <br>
This script is a "literal" translation from C++ to Python 3. \
The original C++ povrtiter is developed an mantined by Paul Macklin at MatchCancer \
and can be found in the following link [https://github.com/PhysiCell-Tools/PhysiCell-povwriter](https://github.com/PhysiCell-Tools/PhysiCell-povwriter)
<br>
While I've not found many difference at the level of performance, the main advantage of having python version of PhysiCell-povwriter is that is much easiert to extend and customize. Furthermore, handling command line arguments and parsing config files is also much easier in python. Nonetheless, the original motivation of this development was to have a povwrite capable of handling PhysiBoSS output format (which is different from PhysiCell's format). In its current version povwriter.py can read and process

~~~~
usage: povwriter.py [-h] [--idxs STRN_IDXS] [--format {physicell,physiboss}]
                    [--out-format {pov,png}]
                    xml_config

Render a bunch of physicell outputfile into povray files

positional arguments:
  xml_config            XML configuration file

optional arguments:
  -h, --help            show this help message and exit
  --idxs STRN_IDXS      String specifing the indexes of the output files. The
                        supported options include: - slices: 1:10:1 - indexes:
                        1,2,5,10 - all (use glob)
  --format {physicell,physiboss}
                        Format of the input data
  --out-format {pov,png}
                        Output format
	
~~~~

#### Examples
~~~~
povwriter.py config/povwriter-settings.xml --format physicell
povwriter.py config/povwriter-settings.xml --format physicell --idxs 0:4:1
povwriter.py config/povwriter-settings.xml --format physicell --idxs 1,3,0

./povwriter.py config/povwriter-settings.xml --format physiboss
./povwriter.py config/povwriter-settings.xml --format physiboss --idxs 0:490:120
./povwriter.py config/povwriter-settings.xml --format physiboss --idxs 0,240
~~~~

Any of these commands will generate one or many .pov files. If you have povray instaled in yout system you can try
~~~~
povray -W720 -H680 -a [path to pov file]
~~~~
to render the .pov file a generate an image. Parameters -H -W and -a correspond to Width, heigh and antilaizing, respectively.


## Plots relevant for assessing biological transport mechanism dynamics

The `transport_plots` folder contains the scripts employed for obtaining 
specific plots that allow quantitative and qualitative analysis of a specific transport dynamic with specific
command-line arguments, shown below.

~~~~
usage: transport_timeseries_plot.py [-h] [--transport_mechanism {simple_diffusion,facilitated_diffusion_carrier}]
                                    [--join JOIN_PLOTS] [--substrate SUBSTRATE] [--figout FIG_FNAME] [--csvout CSV_FNAME]
                                    output_folder

Produce different plots for the different transport mechanisms

positional arguments:
  output_folder         folder were the data is stored, usually the PhysiCell output folder.

optional arguments:
  -h, --help            show this help message and exit
  --transport_mechanism {simple_diffusion,facilitated_diffusion_carrier}
                        Type of transport mechanism for which the plots will be produced
  --join JOIN_PLOTS     Join the different plots into one single figure
  --substrate SUBSTRATE
                        Indicate the substrate for which the transport dynamics will be plotted
  --figout FIG_FNAME    Filename to save the plot
  --csvout CSV_FNAME    Filename to store the summary table used for the plot

~~~~

- `plots_parser.py`: Contains the `argparser` arguments setting.
- `transport_timeseries_plot.py`: Produces various time-course plots referred to specific transport-related variables
  (e.g. Internal and external substrate density, flux, concentration gradient and net total amount of substrate) along
a given simulation. It also stores a .txt file that includes relevant information related to the substrate transport mechanism.
Results are stored within the `plots` subfolder.
- `substrate_plot.py`: Produces, for each full save time of a PhysiCell simulation, a "substrate plot" that shows a diffusing substrate
in the microenvironment, along with the agents. It also produces a GIF animation and a grid-plot JPEG with 12 snapshots from said simulations.
Results are stored within the `transport_gif` subfolder.
- `pcplotutils.py`: Small set of functions built on top of PhysiCell's [python-loader](https://github.com/PhysiCell-Tools/python-loader) that are employed for obtaining the substrate plots from
`substrate_plot.py`.