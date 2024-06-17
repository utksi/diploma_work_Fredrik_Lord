import pandas as pd
import numpy as np
import ast
from collections import Counter, OrderedDict

def get_elements(datafile):
    df = pd.read_csv(datafile)
    tols = []
    ids = []
    bandgaps = []
    for dict in df['bandgap']:
        dict = ast.literal_eval(dict)
        bandgaps.append(dict)
    for element in df['symbols']:
        tol = element.replace('\'','').replace('[','').replace(']','').replace(' ', '')
        tol_list = list(tol.split(','))
        tols.append(tol_list)
    for element in df['material_id']:
        #print(element)
        id = element.split('/')[1]
        id = id.replace(' ', '').replace('\n', '')
        #print(id)
        ids.append(id)
        #print(element_list)
    df['symbols'] = tols
    df['bandgap'] = bandgaps
    df['material_id'] = ids
    return df

def get_b_sites(symbol_list):
    counter = Counter(symbol_list)
    if len(symbol_list) == 10: #regular A2BB'C6
        b_sites = [item for item, count in counter.items() if count == 1]
    elif len(symbol_list) == 20: #double A4B2B'2C12
        b_sites = [item for item, count in counter.items() if count == 2]
        b_sites = list(OrderedDict.fromkeys(b_sites))
    else:
        #print(f"{len(symbol_list)} atoms in compound, currently unhandled scenario")
        b_sites = ['unknown', 'unknown']
    #something to decide B and B' ?
    #put B in [0] and B' in [1]
    return b_sites


r2scan_data = get_elements('bandgap_data.csv')
ref_data_bar = pd.read_csv('bartel_data')
ref_data_mpr = pd.read_csv('mpr_data.csv')

r2scan_mpr_bgs = []
ref_mpr_bgs = []
r2scan_bar_bgs = []
ref_bar_bgs = []

condition = r2scan_data['material_id'].isin(ref_data_mpr['material_id'])
r2scan_mpr = r2scan_data.loc[condition]
r2scan_bar = r2scan_data.loc[~condition]

for index, row in r2scan_mpr.iterrows():
    r2scan_mpr_bgs.append(float(row['bandgap']['energy']))
    id = row['material_id']
    ref_row = ref_data_mpr.loc[ref_data_mpr['material_id'] == id]
    ref_mpr_bgs.append(float(ref_row['bandgap']))

for index, row in r2scan_bar.iterrows():
    r2scan_bar_bgs.append(float(row['bandgap']['energy']))
    compound = row['symbols']
    b_sites = get_b_sites(compound)
    #were looplooping mfers
    for index, ref_row in ref_data_bar.iterrows():
        if (b_sites[0] == ref_row['B'] and b_sites[1] == ref_row['B_']) or (b_sites[1] == ref_row['B'] and b_sites[0] == ref_row['B_']):
            ref_bar_bgs.append(float(ref_row['pbe']))
            

all_r2scan_bgs = r2scan_mpr_bgs +r2scan_bar_bgs
all_ref_bgs = ref_mpr_bgs + ref_bar_bgs
normed_diffs = []

mpr_deviation = [abs(a - b) for a, b in zip(r2scan_mpr_bgs, ref_mpr_bgs)]
bar_deviation = [abs(a - b) for a, b in zip(r2scan_bar_bgs, ref_bar_bgs)]
all_deviation = [abs(a - b) for a, b in zip(all_r2scan_bgs, all_ref_bgs)]
#mad is inapplicable here, whoops
mpr_mad = sum(mpr_deviation) / len(mpr_deviation)
bar_mad = sum(bar_deviation) / len(bar_deviation)
all_mad = sum(all_deviation) / len(all_deviation)
mpr_rmse = (sum((a - b)**2 for a, b in zip(r2scan_mpr_bgs, ref_mpr_bgs)) / len(r2scan_mpr_bgs))**0.5
bar_rmse = (sum((a - b)**2 for a, b in zip(r2scan_bar_bgs, ref_bar_bgs)) / len(r2scan_bar_bgs))**0.5
all_rmse = (sum((a - b)**2 for a, b in zip(all_r2scan_bgs, all_ref_bgs)) / len(all_r2scan_bgs))**0.5


print(f"Total: \n mad is {all_mad} and root mean square error is {all_rmse}")
print(f"MPR: \n mad is {mpr_mad} and root mean square error is {mpr_rmse}")
print(f"Bartel: \n mad is {bar_mad} and root mean square error is {bar_rmse}")