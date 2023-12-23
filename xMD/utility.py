import pandas as pd
from tensorboardX import SummaryWriter as SummaryWriter_

class SummaryWriter(SummaryWriter_):
    """A custom version of the Tensorboard summary writer class."""
    def __init__(self, log_dir=None, comment='', summary_period=1, steps_to_run=-1, **kwargs):
        super().__init__(log_dir=log_dir, comment=comment, **kwargs)
        self.step = 0
        self.summary_period = summary_period
        self.steps_to_run = steps_to_run

    def add_scalar(self, tag, scalar_value, global_step=None, **kwargs):
        """Add a scalar to the Tensorboard summary."""
        if global_step is None:
            global_step = self.step
        super().add_scalar(tag, scalar_value, global_step, **kwargs)

    def add_histogram(self, tag, values, global_step=None, bins='auto', **kwargs):
        """Add a histogram to the Tensorboard summary."""
        if global_step is None:
            global_step = self.step
        super().add_histogram(tag, values, global_step, bins, **kwargs)

    def add_image(self, tag, img_tensor, global_step=None, **kwargs):
        """Add an image to the Tensorboard summary."""
        if global_step is None:
            global_step = self.step
        super().add_image(tag, img_tensor, global_step, **kwargs)

    def is_summary_step(self):
        """Returns whether or not the current step is a summary step."""
        return self.step % self.summary_period == 0 or self.step == self.steps_to_run - 1







class live_GROMACS_log_reader():
    """
    A class to read the live GROMACS log file and reads the data out when called.
    To start with this will only read out the last line of the log file.
    Eventually it will read the entire log file and return a pandas dataframe.
    When it is called it will need to consider the data already read out.
    """
    def __init__(self, 
                 name, 
                 live=False,
                 log_type,
                 log_file,
                 frequency=0):
        self.name = name
        self.path = log_file
        self.data = pd.DataFrame()
        self.log_type = log_type

    def read_log(self):

        