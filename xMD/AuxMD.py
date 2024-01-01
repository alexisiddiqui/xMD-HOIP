# auxiliary functions for xMD
import os
from copy import deepcopy
import glob
import shutil
import subprocess
import pandas as pd
import argparse
import MDAnalysis as mda

def run_MD(md_mdp: str, 
           input_path: str, 
           topo_path: str, 
           tpr_path: str, 
           gmx: str,
           gpu: bool = False):
    
    grompp_command = ["gmx", "grompp", 
                    "-f", md_mdp, 
                    "-c", input_path, 
                    "-p", topo_path, 
                    "-o", tpr_path, 
                    "-r", input_path, 
                    "-maxwarn", "1",
                    "-v"]
    subprocess.run(grompp_command, check=True)
    ### TODO add try except for gmx vs gmx_mpi
    mdrun_command = [gmx, "mdrun", "-v", "-deffnm", tpr_path.replace(".tpr","")]
    # trying out different gpu options
    if gpu: 
        mdrun_command.extend(["-pin", "on", "-pme", "gpu", "-pmefft", "gpu"])
    
    print(mdrun_command)
    subprocess.run(mdrun_command, check=True)

    input_path = tpr_path.replace(".tpr",".gro")
    return input_path


def traj_to_pdb(traj_file: str,
                tpr_path: str,
                pdb_path: str):
    pdbout_command = ["gmx", "trjconv", 
                        "-f", traj_file,
                        "-s", tpr_path,
                        "-o", pdb_path]

    subprocess.run(pdbout_command, input=b"1\n", check=True)
    print("PDB file written to: ", pdb_path)  
    
def concatenate_traj_files(traj_files: list, output_traj_file: str, top_path:str=None):
    """
    Concatenates multiple trajectory files into a single trajectory file.

    Args:
    traj_files (list): List of trajectory files to concatenate.
    output_traj_file (str): The output file name for the concatenated trajectory.

    Returns:
    None: The function does not return a value but writes the concatenated trajectory to a file.
    """
    if top_path is None:
        top_path = traj_files[0].replace(".xtc", ".pdb")

    # use MDAnalysis to concatenate trajectory files
    
    u = mda.Universe(top_path, *traj_files)

    with mda.Writer(output_traj_file, u.trajectory.n_atoms) as W:
        for ts in u.trajectory:
            W.write(u)

def PBC_conversion():

    pass
