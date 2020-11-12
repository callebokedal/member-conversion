import pandas as pd 

df = pd.DataFrame({'A': ['A0', 'A1', 'A2'],
    'B': ['B0', 'B1', 'B2'],
    'C': ['C0', 'C1', 'C2']},
    index=pd.Index(['K0', 'K1', 'K2'], name='key'))

df2 = pd.DataFrame({'A': ['A0', 'A1', 'A2'],
    'B': ['B0', 'B1', 'B2'],
    'C': ['C0', 'C1', 'C2']},
    index=pd.Index(['K0', 'K1', 'K2'], name='key2'))

#     io_current_df['E-post arbete'] = io_current_df['E-post arbete'].map(lambda x: x if type(x)!=str else x.lower())
def to_lower(val,d):
    """
    Test of lowercase
    """
    return val + "-" + str(d)

df['A'] = df['A'].apply(to_lower, args=(4,))
df['B'] = df['A'].apply(to_lower, args=("A",))
print(df)


#     io_current_df['E-post arbete'] = io_current_df['E-post arbete'].map(lambda x: x if type(x)!=str else x.lower())
def test2(val,d):
    """
    Test of lowercase
    """
    #print(d)
    #print(type(d))
    return val + "-" + str(d)

df2['A'] = df2['A'].apply(test2, args=("",))
#df2['B'] = df2['A'].apply(test2, args=("A",))
df2['B'] = df2['A'].apply(test2, args=(df2['B'],))
print(df2)


# creating a DataFrame 
df = pd.DataFrame({'Integers' :[1, 2, 3, 4, 5], 
				'Float' :[1.1, 2.2, 3.3, 4.4 ,5.5]}) 

# displaying the DataFrame 
print(df) 

# function for prepending 'Geek' 
def multiply_by_2(number): 
	return 2 * number 

# executing the function 
df[["Integers", "Float"]] = df[["Integers", "Float"]].apply(multiply_by_2) 

# displaying the DataFrame 
print(df) 
