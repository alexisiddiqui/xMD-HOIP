import os
from copy import deepcopy
import glob
import shutil
import subprocess
from abc import ABC, abstractmethod
import pandas as pd
import argparse
import time
import pickle
from xMD.Experiment_ABC import Experiment
from xMD.MD_Settings import GROMACS_Settings

class MD_Experiment(Experiment):
    def __init__(self,settings: GROMACS_Settings, name=None, pdbcode=None, rep=None):
        super().__init__(settings, name, pdbcode, rep)
        self.set_mdrun_gmx()
        if __name__ == "__main__":
            self.args = self.check_args()
        self.set_environs()

    def set_mdrun_gmx(self, mpi_on: bool = None):
        if mpi_on is None:
            mpi_on = self.settings.gmx_mpi_on

        if mpi_on:
            self.gmx = ("gmx_mpi","gmx")
        else:
            self.gmx = ("gmx","gmx_mpi")

    def check_args(self):
        """
        Checks the arguments for the trial.
        """
        parser = argparse.ArgumentParser()

        parser.add_argument("-R", "--replicate", 
                            dest="replicate",
                            help="Replicate number", type=int,
                            default=0)
        
        ### TODO setup traj continuation
        # parser.add_argument("-T", "--trajectory", 
        #                     dest="traj_no", 
        #                     help="Trajectory number", type=int)
                            
        
        parser.add_argument("-P", "--pdbcode", 
                            dest="pdbcode", 
                            help="PDB code", type=str)
        
        parser.add_argument("-N", "--name",
                            dest="name",
                            help="Name of the trial", type=str)
        
        parser.add_argument("-S", "--suffix",
                            dest="suffix",
                            help="string for the trajectory files", type=str)
        
        parser.add_argument("-s", "--search",
                            dest="search",
                            help="search string for the top files", type=str)


        args = parser.parse_args()

        print("Arguments: ", args)

        if args.replicate is not None:
            self.set_replicate(args.replicate)

        # if args.traj_no is not None:
        #     self.traj_no = args.traj_no

        if args.pdbcode is not None:
            self.settings.pdbcode = args.pdbcode

        if args.name is not None:
            self.name = args.name
        
        if args.suffix is not None:
            self.settings.suffix = args.suffix

        if args.search is not None:
            self.settings.search = args.search

        return args
    
    def pbc_conversion(self, tpr_path):
        """
        Converts the trajectory file to correct for pbc.
        Returns the corrected trajectory file name.
        """
        traj_file = tpr_path.replace(".tpr", ".xtc")
        traj_file1 = traj_file.split(".")[-2] + self.settings.pbc_extensions[0] + ".xtc"
        traj_file2 = traj_file.split(".")[-2] + self.settings.pbc_extensions[1] + ".xtc"
        
        trjconv_command1 = ["gmx", "trjconv",
                             "-f", traj_file, 
                             "-s", tpr_path, 
                             *self.settings.pbc_commands[0], 
                             "-o", traj_file1]
        
        trjconv_command2 = ["gmx", "trjconv", 
                             "-f", traj_file1, 
                             "-s", tpr_path, 
                             *self.settings.pbc_commands[1], 
                             "-o", traj_file2]
        
        print("Running trjconv command 1: ", trjconv_command1)
        subprocess.run(trjconv_command1, input=b"1\n0\n", check=True)

        print("Running trjconv command 2: ", trjconv_command2)
        subprocess.run(trjconv_command2, input=b"1\n0\n", check=True)

        return traj_file2

### TODO sort out the trajfile naming
    def prepare_analysis(self, tpr_path):
        """
        This will prepare the analysis for the trial.
        """
        return self.pbc_conversion(tpr_path)

    def prepare_simulation(self, search=None):
        """
        This will prepare the simulation for the trial.
        """
        self.prepare_config()
        self.prepare_input_files(search)
        self.load_input_files()

    def save_experiment(self, save_name=None):
        super().save_experiment(save_name=save_name)

        unix_time = int(time.time())
        if save_name is None:
            save_name = [self.settings.parent,
                        self.settings.pdbcode, 
                        self.name,
                        str(self.rep_no),
                        str(unix_time)]
            save_name = "_".join(save_name)+".pkl"
            
            log_dir = self.dirs[self.settings.logs_directory]
            
            save_path = os.path.join(log_dir, save_name)

            with open(save_path, 'wb') as f:
                pickle.dump(self, f)
        print("Saved experiment to: ", save_path)
        return save_path


    def set_environs(self):
        """
        Sets the environment variables for the trial.
        """
        os.environ[self.settings.environ] = self.settings.environ_path
        print("Environment variables set: ", self.settings.environ, self.settings.environ_path)

        
