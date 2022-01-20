#!/usr/bin/env python3
# coding: utf-8

import os, sys, subprocess


# TO DO
# Read CMD standard output, to detect whenever an error is made


def load_project(physiboss_folder_path, project_name="template_BM", make=True, gif=True):
    """
    Given the absolute path to the PhysiBoSSv2 folder, and a specific project name,
    it runs the "reset" and "data-cleanup" commands from PhysiCell. By default, it also
    compiles and runs a template project.

    """

    # folder check:
    # double negative condition, checks both

    if not os.path.isdir(physiboss_folder_path):
        sys.stderr.write("Wrong folder indicated. Write the absolute path to where the PhysiBoss folder is located\n")
        sys.stderr.flush()
    else: # physiboss folder is located
        sys.stderr.write("PhysiBoSS folder found!\n")
        files = [file for file in os.listdir(physiboss_folder_path)]

        reset = subprocess.run(["make reset"], cwd=physiboss_folder_path, shell=True)
        cleanup = subprocess.run(["make data-cleanup"], cwd=physiboss_folder_path, shell=True)

        sys.stderr.write("\n\n\nData reset and cleanup done.\n\n\n")
        sys.stderr.flush()

        if project_name in files: # small bug, this can be corrected from the Makefiles
            rm_project = subprocess.run([f"rm {project_name}"], cwd=physiboss_folder_path, shell=True)

            # just a workaround, ideally do NOT run heterogeneity if selected project cannot be run
            rm_heterogeneity = subprocess.run([f"rm heterogeneity"], cwd=physiboss_folder_path, shell=True)


        if make is True:
            sys.stderr.write(f"\n\n\nBuilding the selected project: {project_name}.\n\n\n")
            sys.stderr.flush()
            new_project = subprocess.run([f"make {project_name}"], cwd=physiboss_folder_path, shell=True)
            new_project_make = subprocess.run(["make"], cwd=physiboss_folder_path, shell=True)

            sys.stderr.write("\n\n----------------------------------------------\n\nStarting simulation.\n\n\n----------------------------------------------\n\n")
            sys.stderr.flush()

            new_project_execute = subprocess.run([f"./{project_name}"], cwd=physiboss_folder_path, shell=True)

        if gif is True and len([svg_files for svg_files in os.listdir(physiboss_folder_path + "/output/") if svg_files.endswith(".svg")]) >= 1:
            make_gif = subprocess.run([f"convert {physiboss_folder_path}/output/s*.svg {physiboss_folder_path}/output/out.gif "], cwd=physiboss_folder_path, shell=True)
            sys.stderr.write("\n\n\n GIF made. Opening... \n\n\n")
            sys.stderr.flush()

            open_gif = subprocess.run([f"xdg-open {physiboss_folder_path}/output/out.gif &"], cwd=physiboss_folder_path, shell=True)
            # this only works for unix systems?



        else:
            sys.stderr.write("\n\n\n No SVG files found. Could not make GIF. \n\n\n")
            sys.stderr.flush()

        del files # free some space


    return 0


if __name__ == "__main__":
    path = sys.argv[1]
    project_name = sys.argv[2]
    load_project(path, project_name)

