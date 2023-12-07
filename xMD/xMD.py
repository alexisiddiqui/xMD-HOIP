# xMD class for managing MD experiments
# MD_Experiment class handles all the functions for running MD experiments
# This class desribes the routines for running MD experiments

import os
from copy import deepcopy
import glob
import shutil
import subprocess
from abc import ABC, abstractmethod
import pandas as pd
import argparse

from xMD.MD_Experiment import MD_Experiment
from xMD.MD_Settings import GROMACS_Settings

class xMD(MD_Experiment):
    def __init__(self, settings: GROMACS_Settings, name=None, pdbcode: str = None, rep=None):
        super().__init__(settings, name, pdbcode, rep)


    def run_experiment(self, search=None, rep=None):
        """
        This will run the experiment for the trial.
        suffix is the suffix for the initial topology files. 
        Should revert back to the suffix set in the settings.
        """
        # TODO setup tensorboard logging
        # write parser for gromacs outputs
        # write tensorboard logger
        # use threading to run logger concurrently 
        self.set_replicate(rep)
        self.prepare_simulation(search)
        tpr_path = self.run_MD_step()
        traj_file = self.prepare_analysis(tpr_path=tpr_path)
        self.run_analysis(traj_file=traj_file)


    def run_MD_step(self):
        """
        This will run a step of MD for the trial.
        Retruns the tpr file name.
        """

        topo_files = [f for f in self.topology_files if f.endswith(".top")]
        gro_files = [f for f in self.topology_files if f.endswith(".gro")]
        tpr_name = "_".join([self.settings.suffix, 
                             self.settings.pdbcode, 
                            str(self.traj_no)]) + ".tpr"
        
        tpr_path = os.path.join(self.dirs[self.settings.data_directory], 
                                self.settings.rep_directory + str(self.rep_no), 
                                tpr_name)
        
        md_mdp = os.path.join(self.settings.config, self.config_files)
        
        topo_name = topo_files[0]
        topo_path = os.path.join(self.dirs[self.settings.data_directory], 
                                self.settings.rep_directory + str(self.rep_no), 
                                topo_name)
        
        gro_name = gro_files[0]
        input_path = os.path.join(self.dirs[self.settings.data_directory], 
                                self.settings.rep_directory + str(self.rep_no), 
                                gro_name) 

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
        mdrun_command = [self.gmx[0], "mdrun", "-v", "-deffnm", tpr_path.replace(".tpr","")]
        subprocess.run(mdrun_command, check=True)

        self.set_trajectory_number()
        return tpr_path

### TODO create analysis commands - add data to the dataframe
    def run_analysis(self, traj_file=None, tpr_path=None):
        ### This will take args from settings for what analyses to run
        # for now we just convert to pdb
        #if traj file is not given try to rebuild name
        if tpr_path is None:
            tpr_name = "_".join([self.settings.suffix, 
                                            self.settings.pdbcode, 
                                            str(self.traj_no)]) + ".tpr"
            tpr_path = os.path.join(self.dirs[self.settings.data_directory], 
                                    self.settings.rep_directory + str(self.rep_no), 
                                    tpr_name)

        if traj_file is None:
            traj_file = tpr_path.replace(".tpr", ".xtc")
            traj_file = traj_file.split(".")[-2] + self.settings.pbc_extensions[1] + ".xtc"
            pdb_name = str(self.rep_no) + "_" + tpr_name.replace(".tpr", ".pdb")
            pdb_name = pdb_name.split(os.sep)[-1]
        else:
            pdb_name = str(self.rep_no) + "_" + traj_file.replace(".xtc", ".pdb")
            pdb_name = pdb_name.split(os.sep)[-1]


        pdb_path = os.path.join(self.dirs[self.settings.viz], pdb_name)
        

        pdbout_command = ["gmx", "trjconv", 
                            "-f", traj_file,
                            "-s", tpr_path,
                            "-o", pdb_path]
        
        subprocess.run(pdbout_command, input=b"1\n", check=True)
        print("Saved pdb file to: ", pdb_path)

