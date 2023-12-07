"""
Settings classes
"""

import platform
import os
from copy import deepcopy
import pandas as pd


class Settings:
    "Represents the global settings for MD and Docking runs"
    def __init__(self, name=None, pdbcode: str = None):
        if pdbcode is not None:
            self.pdbcode = pdbcode
        else:
            self.pdbcode = None

        if name is not None:
            self.trial_name = name
        else:
            self.trial_name = 'base'
        self.temporary_directory = 'temporary'
        self.logs_directory = 'logs'
        self.data_directory = 'data'
        self.structures_input = "start_structures"
        self.structures_output = "prod_structures"
        self.config = 'config'
        self.topology = 'topology'
        self.viz = 'visualisation'
        self.ana = 'analysis'
        self.search = None
        self.suffix = None
        self.pH = 7.4
        self.parent = None
        self.replicates = 5
        self.rep_directory = 'R_'
        self.dirs_to_create = [self.temporary_directory, 
                               self.logs_directory, 
                               self.data_directory,
                               self.viz, 
                               self.ana]
        # self.ARGS = None # we set this using argparse


# inhrerit from Settings
class GROMACS_Settings(Settings):
    "Represents the settings for a given run of MD"
    def __init__(self, name=None, pdbcode: str = None):
        super().__init__(name, pdbcode)
        if name is None:
            self.trial_name = self.trial_name + '_MD'
        self.structures_input = os.path.join(self.structures_input,"APO")
        self.structures_output = os.path.join(self.structures_output,"APO")
        self.parent = "MD"
        self.suffix = "MD"
        self.search_traj = ".gro"
        self.pbc_commands = [("-pbc", "mol", "-center"), ("-pbc", "nojump")]
        self.pbc_extensions = ["-"+ext[1] for ext in self.pbc_commands]
        self.environ_path = os.getcwd()
        self.environ = "GMXLIB"
        self.gmx = ("gmx","gmx_mpi")
        self.gmx_mpi_on = True
