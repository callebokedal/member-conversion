# pylint: disable=import-error
import pandas as pd
import numpy as np
import os, sys
from pathlib import Path
from datetime import date
import time 
from time import strftime


from utils import  \
    validate_file

# Update to correct timezone
os.environ["TZ"] = "Europe/Stockholm"
time.tzset()

today = date.today()
date_today = today.strftime("%Y-%m-%d")
timestamp = str(strftime("%Y-%m-%d_%H.%M")) # Timestamp to use for filenames

# Remeber start time
start_time = time.time()

path = '/usr/src/app/files/'            # Required base path
path_out = '/usr/src/app/files/last/'   # Output path

# Ger args
if len(sys.argv) > 1:
    cmd  = sys.argv[1]

if len(sys.argv) > 2:
    file_1  = sys.argv[2]
    validate_file(file_1, 2)

if len(sys.argv) > 3:
    file_2 = sys.argv[3]
    validate_file(file_2, 3)

# Functions

def export_contact_list(io_file_name):
    """
    Convert IO export file to contact list
    """
    # Validate args
    validate_file(io_file_name)

    # Open file, columns of interest

    # Format

    # Create output file
    pass

# Action 
print(" Start ".center(80, "-"))

if "contact_list" == cmd:
    #from_mc_to_io(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)
    pass

print("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print(" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-")