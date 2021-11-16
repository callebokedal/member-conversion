import pandas as pd
import numpy as np
import os, sys
from pathlib import Path
from datetime import date
import time 
from time import strftime

from packages.utils import stats, validate_file, _read_io_file, _read_mc_file

# Update to correct timezone
os.environ["TZ"] = "Europe/Stockholm"
time.tzset()

today = date.today()
date_today = today.strftime("%Y-%m-%d")
timestamp = str(strftime("%Y-%m-%d_%H.%M")) # Timestamp to use for filenames

# Remeber start time
start_time = time.time()

# Config
path = '/usr/src/app/files/'            # Required base path
path_out = '/usr/src/app/files/last/'   # Output path

# Get args
if len(sys.argv) > 1:
    cmd  = sys.argv[1]

if len(sys.argv) > 2:
    exported_io_members_file = sys.argv[2]
    validate_file(exported_io_members_file, 2, "/home/me/files")

if len(sys.argv) > 3:
    exported_mc_members_file = sys.argv[3]
    validate_file(exported_mc_members_file, 3, "/home/me/files")

def compare_io_with_mc(io_file_name, mc_file_name):
    """
    Takes a IdrottOnline file and converts into a My Club Import Excel file
    """
    # IO Dataframe
    io_export_df = _read_io_file(io_file_name)
    stats("Antal medlemmar i IO: {} ({})".format(str(len(io_export_df)), Path(io_file_name).name))

    # MC Dataframe
    mc_export_df = _read_mc_file(mc_file_name)
    stats("Antal medlemmar i MC: {} ({})".format(str(len(mc_export_df)), Path(mc_file_name).name))


    """
    My Club import columns
    'Förnamn',
    'Efternamn',
    'Adress',
    'Postnummer',
    'Postadress',
    'Personnummer',
    'Hemtelefon medlem',
    'Hemtelefon kontaktperson1',
    'Hemtelefon kontaktperson2',
    'Mobiltelefon medlem',
    'Mobiltelefon kontaktperson1',
    'Mobiltelefon kontaktperson2',
    'Epost medlem',
    'Epost kontaktperson1',
    'Epost kontaktperson2',
    'Lag',
    'Medlemstyp',
    'Kön',
    'Förnamn kontaktperson1',
    'Efternamn kontaktperson1',
    'Förnamn kontaktperson2',
    'Efternamn kontaktperson2',
    'Extra 1',
    'Extra 2',
    'Extra 3',
    'Extra 4',
    'Extra 5',
    """
    pass


# Action 
print(" Start ".center(80, "-"))

if "compare" == cmd:
    compare_io_with_mc(exported_io_members_file, exported_mc_members_file)


print ("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print((" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-"))
