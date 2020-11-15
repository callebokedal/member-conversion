import pandas as pd
import numpy as np
import os, sys
from pathlib import Path
from datetime import date
import time 
from time import strftime

mc_pd = pd.read_excel('/usr/src/app/files/2020-11-15_MyClub_all_member_export.xls', usecols=['MedlemsID','Förnamn','Efternamn','Personnummer','E-post'], dtype = {
        'MedlemsID': 'string','Personnummer': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string'}) # My Club columns

email_pd = pd.read_excel('/usr/src/app/files/2020-11-03_cg_medlemmar_2020.xls', usecols=['Förnamn','Efternamn','Personnummer','E-post'], dtype = {
        'Personnummer': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string'}) # My Club columns

comp_df = pd.merge(mc_pd, email_pd, 
        on = 'E-post',
        how = 'outer',
        suffixes = ('_mc','_cg'),
        indicator = True)

diff = comp_df[comp_df['_merge'] != 'both']
print(diff)