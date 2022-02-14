import os
import datetime
from pprint import pprint as pp
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename

from ice.analysis import multiple_sanger_analysis

# Running a batch analysis
def ice_pipeline():
    Tk().withdraw()
    print("Choose Definition Path: ")
    definition_path = askopenfilename()
    print(definition_path)
    print("Path to all data: ")
    data_path = askdirectory()
    print("Output Directory: ")
    output_path = askdirectory()
    timestamp = '{:%Y-%m-%d-%H%M%S}'.format(datetime.datetime.now())


    definition_file = os.path.abspath(definition_path)
    data_directory = os.path.abspath(data_path)
    output_dir = os.path.join(output_path,"ice_results_{}/".format(timestamp))
    print(output_dir)

    job_args = (definition_file, output_dir)
    job_kwargs = {
        'verbose': False,
        'data_dir': data_directory
    }
    multiple_sanger_analysis(*job_args, **job_kwargs)

if __name__ == '__main__':
    ice_pipeline()
