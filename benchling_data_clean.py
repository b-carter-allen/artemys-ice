import os
import pandas as pd
import re
import math

from pprint import pprint as pp
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename

MIN_R_SQUARED = 0.85
MIN_HOMOZYGOUS_KO_SCORE = 85
MAX_HETEROZYGOUS_KO_SCORE = 70
MIN_HETEROZYGOUS_KO_SCORE = 35

ZYGOUSITY_LABEL = "ko_type"

# Running a batch analysis
def benchling_data_clean():
    """
    1. Make excel into dataframe
    2. Read filenames into numeric positions
    3. Add Well Positions to each entity
    4. Filter results based on logic.
    5. Generate a .csv
    """

    #Prevent Tkinter Gui Screen from popping up
    Tk().withdraw()

    print("Choose Results Excel File: ")
    excel_path = askopenfilename()
    print("Choose Destination folder for benchling csv")
    output_dir = askdirectory()

    #Store Results timestamp
    results_timestamp = str(excel_path).split('.')[2]

    #Process Data
    raw_results_df = pd.read_excel(excel_path, index_col=0)
    raw_results_df['Position'] = raw_results_df['sample_name'].map(lambda x: int(re.findall('_(\d+)-',str(x))[0]))
    raw_results_df['Well'] = raw_results_df['Position'].map(lambda x: convertNumericWellPosToA1Style(int(x),8,12,"col",True))
    no_na_df = raw_results_df.dropna(subset=["ice"])
    quality_df = no_na_df[(no_na_df["r_squared"] >= MIN_R_SQUARED)]
    #Filter results to 
    homo_hetero_df = quality_df[
        (quality_df["ko_score"] >= MIN_HOMOZYGOUS_KO_SCORE) |
        (((quality_df["ko_score"] >= MIN_HETEROZYGOUS_KO_SCORE)  & (quality_df["ko_score"] <= MAX_HETEROZYGOUS_KO_SCORE)))
    ]

    homo_hetero_df[ZYGOUSITY_LABEL] = homo_hetero_df.apply (lambda row: check_zygosity(row), axis=1)
    clean_df = homo_hetero_df[["sample_name","r_squared","ko_score","Guide Sequence","Well", ZYGOUSITY_LABEL]].copy()

    output_path = os.path.join(output_dir,"benchling_results_{}.csv".format(results_timestamp))
    clean_df.to_csv(output_path, index=False)

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

def check_zygosity(row):
    if row["ko_score"] >= MIN_HOMOZYGOUS_KO_SCORE:
        return "Homozygous"
    if row["ko_score"] <= MAX_HETEROZYGOUS_KO_SCORE and row["ko_score"] >= MIN_HETEROZYGOUS_KO_SCORE:
        return "Heterozygous"
    else:
        return "NaN"

if __name__ == '__main__':
    benchling_data_clean()