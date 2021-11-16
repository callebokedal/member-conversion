import pandas as pd
import os

from utils import normalize_email

path = '/usr/src/app'

def list_files(path):
    """
    List files in path
    """
    files = os.listdir(path)
    for f in files:
        print(f)

def list_all_files(path):
    """
    List all files in path
    """
    with os.scandir(path) as it:
        for entry in it:
            print(entry.name)

# Dataframe for members
def read_file(file_name):
    """
    Test to read Excel via pandas
    """
    ##df = pd.read_excel(file_name, sheetname='Sheet1')
    df = pd.read_excel(file_name)

    #print("Column headings:")
    #print(df.columns)
    #print(df['Ingen tidning tack'])
    # print(df)
    return df

def read_id_file(file_name):
    """
    Read file with member id and personnummer
    """
    df = pd.read_csv(file_name, header=None, names=['MedlemsID2', 'Personnummer2'])
    #print(df)
    return df

#list_files(path)
#list_all_files(path)

# Get mapping of id <-> pnr
#id_df = read_id_file("./files/Senior-excel.txt")
# print(id_df)
#print(id_df.dtypes)
# MedlemsID       int64
# Personnummer    int64

#members = read_file("./files/Senior-excel.xls")
#print(members.dtypes)

def merge_data(mem_df, id_df):
    """
    Obsolete! Use merge_dfs instead
    Merges dataframe of members with data from id dataframe
    """
    mem_df['FullPNr'] = '' # pd.NA
    print(mem_df)

    for row in mem_df.loc[:, ['MedlemsID', 'Personnummer', 'FullPNr', 'Uppdaterad', 'Förnamn']].itertuples():
        print(row)
        # print(row.MedlemsID)
        #print(mem_df['MedlemsID'] == row.MedlemsID)

        # df.loc[['viper', 'sidewinder'], ['shield']] = 50
        #print(row.Personnummer)
        mem_df.at[row.Index,'FullPNr'] = 'test'

    print(mem_df)
        
def merge_dfs(df1, df2, left_name, right_name, dir = 'left'):
    """
    Merge dataframes based on 'MedlemsID'
    """
    merged_df = pd.merge(df1, df2, 
                     left_on = left_name, 
                     right_on = right_name, 
                     how = dir)
    return merged_df


#merge_data(members, id_df)

#mdf = merge_dfs(members, id_df, 'MedlemsID','MedlemsID2', 'left')
#print(mdf)

print("done test.py")

print(normalize_email("A"))
print(normalize_email(3))
print(normalize_email(" B"))
print(normalize_email(" C ") + ".")

import re
regex = r"\[\[MC-ID: (\d*)\]\]"
test_str = ("[[MC-ID: 123]]\n")
subst = "test"

# You can manually specify the number of replacements by changing the 4th argument
result = re.sub(regex, subst, test_str, 0, re.MULTILINE)

if result:
    print (result)

d = re.search(regex, '[[MC-ID: 123]]')
if d:
    print(d.group(0))
    print(d.group(1))


d = re.search(regex, '[[MCasdasd-ID: 123]]')
if d:
    print(d.group(0))
    print(d.group(1))

print("---")
def test_match(comment):
    regexp = r"^\d{4,}"
    m = re.match(regexp, comment)
    if m:
        print(comment)
    else:
        print("no")

test_match("1234")
test_match("123")
test_match("1 234")

def test_member_id_in_comment(comment):
    if re.match(r"\[\[MC-ID: .*", comment):
        print("Found: " + comment)
    elif re.match(r"\[\[MedlemsID: .*", comment):
        print("found: " + comment)
    else:
        print("not found: " + comment)

print("---")
test_member_id_in_comment("[[MC-ID: 1670699]][[Import: 2020-11-22_00.34]]")
test_member_id_in_comment("[[MedlemsID: 1676673]][[Import: 2020-11-16_01.20]]")
test_member_id_in_comment("[[MdC-ID: 1670699]][[Import: 2020-11-22_00.34]]")
test_member_id_in_comment("[[MeddlemsID: 1676673]][[Import: 2020-11-16_01.20]]")