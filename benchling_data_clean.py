import os
import pandas as pd
import re
import math

from pprint import pprint as pp
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename

# Running a batch analysis
def benchling_data_clean():
    """
    1. Make excel into dataframe
    2. Read filenames into numeric positions
    3. Add Well Positions to each entity
    4. Filter results based on logic.
    5. Generate a .csv
    """
    
    Tk().withdraw()
    print("Choose Results Excel File: ")
    excel_path = askopenfilename()
    print("Choose Destination folder for benchling csv")
    output_dir = askdirectory()
    results_timestamp = str(excel_path).split('.')[2]


    raw_results_df = pd.read_excel(excel_path, index_col=0)
    raw_results_df['Position'] = raw_results_df['sample_name'].map(lambda x: int(re.findall('_(\d+)-',str(x))[0]))
    raw_results_df['Well'] = raw_results_df['Position'].map(lambda x: convertNumericWellPosToA1Style(int(x),8,12,"col",True))
    no_na_df = raw_results_df.dropna(subset=["ice"])
    quality_df = no_na_df[(no_na_df["r_squared"] >= 0.85)]
    homo_hetero_df = quality_df[
        (quality_df["ko_score"] >= 85) |
        (((quality_df["ko_score"] >= 35)  & (quality_df["ko_score"] <= 70)))
    ]

    output_path = os.path.join(output_dir,"benchling_results_{}.csv".format(results_timestamp))
    homo_hetero_df.to_csv(output_path, index=False)

    print(output_dir)
    
def convertNumericWellPosToA1Style(numericPos, contRows, contCols, colOrRowMajor, padWithZeros):
    """
    Convert a numeric position to an A1 style position.
    Parameters
    ----------
    numericPos : int
        Numeric well position to be converted.
    contMaxRows : int
        Max number of container rows.
    contMaxCols : int
        Max number of container cols.
    colOrRowMajor : str
        'col' or 'row' for column or row major addressing.
    padWithZeros : bool
        Whether to pad the numeric portion returned, with zeros or not.
        i.e., A1 or A01
    """
    if numericPos < 1:
        raise ValueError("Container position value '" + str(numericPos) + "' must be 1 or greater.")
    if contCols < 1:
        raise ValueError("Container columns value '" + str(contCols) + "' must be 1 or greater.")
    if contRows < 1:
        raise ValueError("Container rows value '" + str(contRows) + "' must be 1 or greater.")
    if numericPos > contCols * contRows:
        raise ValueError("Container position value '" + str(numericPos) + "' exceeds the maximum container wells possible of '" + str(contCols * contRows) + "'.")
    if colOrRowMajor == "row":
        if padWithZeros:
            return 'ABCDEFGH'[(numericPos - 1) // contCols] + '%02d' % ((numericPos - 1) % contCols + 1,)
        else:
            return 'ABCDEFGH'[(numericPos - 1) // contCols] + str((numericPos - 1) % contCols + 1)
    elif colOrRowMajor == "col":
        if padWithZeros:
            return 'ABCDEFGH'[(numericPos - 1) % contRows] + '%02d' % (math.ceil(numericPos / contRows),)
        else:
            return 'ABCDEFGH'[(numericPos - 1) % contRows] + str(math.ceil(numericPos / contRows))
    else:
        raise ValueError("Container traversal value '" + colOrRowMajor + "' must be 'col' or 'row'.")

if __name__ == '__main__':
    benchling_data_clean()