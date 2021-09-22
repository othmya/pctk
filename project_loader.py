#!/usr/bin/env python3
# coding: utf-8

import os, sys, subprocess


def load_project(physiboss_folder_path, project_name="template_BM", make=True, gif=True):
    """
    Given the absolute path to the PhysiBoSSv2 folder, and a specific project name,
    it runs the "reset" and "data-cleanup" commands from PhysiCell. By default, it also
    compiles and runs a template project.

    """

    # folder check

    if not os.path.isdir(physiboss_folder_path):
        sys.stderr.write("Wrong folder indicated. Write the absolute path to where the PhysiBossv2 folder is located\n")
        sys.stderr.flush()
    else: # physiboss folder is located
        files = [file for file in os.listdir(physiboss_folder_path)]
        reset = subprocess.run(["make reset"], cwd=physiboss_folder_path, shell=True)
        cleanup = subprocess.run(["make data-cleanup"], cwd=physiboss_folder_path, shell=True)

        if project_name in files: # small bug, this can be corrected from the Makefiles
            rm_project = subprocess.run([f"rm {project_name}"], cwd=physiboss_folder_path, shell=True)

        del files # free some space

        if make is True:
            new_project = subprocess.run([f"make {project_name}"], cwd=physiboss_folder_path, shell=True)
            new_project_make = subprocess.run(["make"], cwd=physiboss_folder_path, shell=True)
            new_project_execute = subprocess.run([f"./{project_name}"], cwd=physiboss_folder_path, shell=True)
            #print(new_project_execute)

        if gif is True:
            make_gif = subprocess.run([f"magick convert {physiboss_folder_path}/output/s*.svg {physiboss_folder_path}/output/out.gif "], cwd=physiboss_folder_path, shell=True)

    return 0


if __name__ == "__main__":
    path = sys.argv[1]
    project_name = sys.argv[2]
    load_project(path, project_name)

