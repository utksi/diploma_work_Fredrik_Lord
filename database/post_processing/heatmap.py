from collections import Counter, OrderedDict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast

def get_elements(datafile):
    df = pd.read_csv(datafile)
    tols = []
    bandgaps = []
    for dict in df['bandgap']:
        dict = ast.literal_eval(dict)
        bandgaps.append(dict)
    for element in df['symbols']:
        tol = element.replace('\'','').replace('[','').replace(']','').replace(' ', '')
        tol_list = list(tol.split(','))
        tols.append(tol_list)
        #print(element_list)
    df['symbols'] = tols
    df['bandgap'] = bandgaps
    return df

def get_anion(symbol_list):
    counter = Counter(symbol_list)



    if len(symbol_list) == 10: #regular A2BB'C6
        anion = [item for item, count in counter.items() if count == 6]

        if len(anion) != 1:
            print(f'{symbol_list} anion broke, {anion}')
        
    elif len(symbol_list) == 20: #double A4B2B'2C12
        anion = [item for item, count in counter.items() if count == 12]

        if len(anion) != 1:
            print(f'{symbol_list} anion broke')
    else:
        #print(f"{len(symbol_list)} atoms in compound, currently unhandled scenario")
        anion = ['unknown']
 
    return anion[0]

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

def get_axes(b_sites_list):
    x_axis = []
    y_axis = []
    for b_sites in b_sites_list:
        if b_sites[0] not in x_axis:
            x_axis.append(b_sites[0])
        if b_sites[1] not in y_axis:
            y_axis.append(b_sites[1])
  

    return x_axis, y_axis

def plot_heatmaps(cl_heatmap_data, br_heatmap_data, i_heatmap_data):

    cl_x_axis, cl_y_axis = get_axes(cl_heatmap_data['b_sites'])
    grid = [[-1 for _ in range(len(cl_y_axis))] for _ in range(len(cl_x_axis))]
    for index, b_sites in enumerate(cl_heatmap_data['b_sites']):
        if b_sites[0] in cl_x_axis and b_sites[1] in cl_y_axis:
            x_index = cl_x_axis.index(b_sites[0])
            y_index = cl_y_axis.index(b_sites[1])
            grid[x_index][y_index] = cl_heatmap_data['bandgaps'][index]


    fig, ax = plt.subplots()
    im = ax.imshow(grid)
    cbar_kw = {}
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel('Bandgap energy [eV]', rotation=-90, va="bottom")



    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(cl_x_axis)), labels=cl_x_axis)
    ax.set_yticks(np.arange(len(cl_y_axis)), labels=cl_y_axis)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    ax.set_title("Bandgaps for B-B' combinations of Cl-based double halide perovskites")
    fig.tight_layout()

    plt.show()

def main():
    bandgap_data = get_elements('bandgap_data.csv')
    cl_heatmap_data = {'b_sites': [], 'bandgaps': []} # idea is to match indexes
    br_heatmap_data = {'b_sites': [], 'bandgaps': []}
    i_heatmap_data = {'b_sites': [], 'bandgaps': []}
    #bruh
    cl_element1s = []
    cl_element2s = []
    cl_energies = []
    br_element1s = []
    br_element2s = []
    br_energies = []
    i_element1s = []
    i_element2s = []
    i_energies = []
    cl_direct = []
    br_direct = []
    i_direct = []
    cl_spacegroups = []
    br_spacegroups = []
    i_spacegroups = []


    for index, row in bandgap_data.iterrows():
        compound = row['symbols']
        anion = get_anion(compound)
        bandgap = row['bandgap']['energy']
        direct = row['bandgap']['direct']
        spacegroup = row['bandgap']['direct']



        
        if anion == 'Cl':
            b_sites = get_b_sites(compound)
            cl_heatmap_data['b_sites'].append(b_sites)
            cl_heatmap_data['bandgaps'].append(bandgap)
            cl_energies.append(bandgap)
            cl_element1s.append(b_sites[0])
            cl_element2s.append(b_sites[1])
            cl_direct.append(direct)
            cl_spacegroups.append(spacegroup)

        elif anion == 'Br':
            b_sites = get_b_sites(compound)
            br_heatmap_data['b_sites'].append(b_sites)
            br_heatmap_data['bandgaps'].append(bandgap)
            br_energies.append(bandgap)
            br_element1s.append(b_sites[0])
            br_element2s.append(b_sites[1])
            br_direct.append(direct)
            br_spacegroups.append(spacegroup)


        elif anion == 'I':
            b_sites = get_b_sites(compound)
            i_heatmap_data['b_sites'].append(b_sites)
            i_heatmap_data['bandgaps'].append(bandgap)
            i_energies.append(bandgap)
            i_element1s.append(b_sites[0])
            i_element2s.append(b_sites[1])
            i_direct.append(direct)
            i_spacegroups.append(spacegroup)


        else:
            print('something wrong')
        

    cl_df = pd.DataFrame({'element1': cl_element1s, 'element2': cl_element2s, 'energy': cl_energies, 'direct': cl_direct})
    br_df = pd.DataFrame({'element1': br_element1s, 'element2':br_element2s, 'energy': br_energies, 'direct': br_direct})
    i_df = pd.DataFrame({'element1': i_element1s, 'element2': i_element2s, 'energy': i_energies, 'direct': i_direct})
    cl_df.to_csv('Cl_heat_data.csv', index=False)
    br_df.to_csv('Br_heat_data.csv', index=False)
    i_df.to_csv('I_heat_data.csv', index=False)

    #scrapped this for plot.py, only used to sort data now

    #plot_heatmaps(cl_heatmap_data, br_heatmap_data, i_heatmap_data)

if __name__ == "__main__":
    main()