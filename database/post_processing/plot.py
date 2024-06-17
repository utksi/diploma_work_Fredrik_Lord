import subprocess
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import svgutils.transform as sg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

def get_array(unique_elements, is_direct, temperatures, elements1, elements2):
    # Create 2D list with temperature values, list is symmetric
    temperature_array = [[-10 for _ in range(len(unique_elements))] for _ in range(len(unique_elements))]
    indirect_bandgap = []
    for i in range(len(elements1)):
        row1 = unique_elements.index(elements1[i])
        col1 = unique_elements.index(elements2[i])
        if not is_direct[i]:
            temperature_array[row1][col1] = abs(temperatures[i])
            indirect_bandgap.append((row1,col1))
        else:
            temperature_array[row1][col1] = temperatures[i]
        row2 = unique_elements.index(elements2[i])
        col2 = unique_elements.index(elements1[i])
        if not is_direct[i]:
            temperature_array[row2][col2] = abs(temperatures[i])
            indirect_bandgap.append((row2,col2))
        else:
            temperature_array[row2][col2] = temperatures[i]

    # Replace missing data with numpy's nan value
    for i in range(len(unique_elements)):
        for j in range(len(unique_elements)):
            if temperature_array[i][j] == -10:
                temperature_array[i][j] = np.nan
    return temperature_array, indirect_bandgap

def create_plot(temperature_array, indirect_bandgap, unique_elements, f_size, compound_base, dot_size, name):
    # Create heatmap
    fig = px.imshow(temperature_array, aspect="equal", x=unique_elements, y=unique_elements)# range_color=[0, 7]
    #title = "Bandap energies for HDPs" + name
    fig.update_layout(xaxis_title="B / B'", yaxis_title="B' / B")
    # Use Times New Roman font
    
    fig.update_layout(font_family="Times New Roman", font_size = f_size)
    #Colorbar settings; use Jet or Portland color scale
    fig.update_layout(coloraxis_colorbar=dict(x=0.9, y=0.5, len=1.0), coloraxis_colorbar_title="Bandgap energy [eV]",coloraxis_colorscale="portland")
    #Colorbar width
    fig.update_layout(coloraxis_colorbar=dict(thickness=20))
    #Add more ticks to colorbar
    fig.update_layout(coloraxis_colorbar=dict(nticks=10))
    #Colorbar tick length
    fig.update_layout(coloraxis_colorbar=dict(ticklen=10))
    #Show ticks outside colorbar
    fig.update_layout(coloraxis_colorbar=dict(ticks="outside"))

    # Add/remove grid lines
    fig.update_xaxes(showgrid=False, mirror = True, gridwidth=1, gridcolor='black', linecolor='black', linewidth=1, dtick=1)
    fig.update_yaxes(showgrid=False, mirror = True, gridwidth=1, gridcolor='black', linecolor='black', linewidth=1, dtick=1)

    #Boundary around grid squares
    shapes = []
    for i in range(len(temperature_array)):
        for j in range(len(temperature_array[i])):
            shapes.append(dict(type='rect', xref='x', yref='y', x0=j-0.5, y0=i-0.5, x1=j+0.5, y1=i+0.5, line=dict(color='black', width=1)))
    fig.update_layout(shapes=shapes)

    #Distinguish the Neel temperatures with dots
    annotations = []
    for row, col in indirect_bandgap:
        annotations.append(dict(x=col, y=row, xref='x', yref='y', 
                                text='', showarrow=True, 
                                arrowhead=6, arrowcolor = 'black', arrowsize = dot_size, ax=-0.5, ay=-0.5))
        annotations.append(dict(x=row, y=col, xref='x', yref='y', 
                                text='', showarrow=True, 
                                arrowhead=6, arrowcolor = 'black', arrowsize = dot_size, ax=-0.5, ay=-0.5))
    fig.update_layout(annotations=annotations)
    fig.show()
    #Save figure as svg
    figure = compound_base + name + "_fig.svg"
    fig.write_image(figure, format="svg")
    export_line = "--export-eps=" + compound_base + name + "_fig.eps"
    #Convert svg to eps using inkscape
    subprocess.run(["inkscape", export_line, figure])

# Read file and separate element names and temperature values
data_file_names = ['Cl_heat_data.csv', 'Br_heat_data.csv']
elements_3d = ['Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn']
rare_earths = ['Sc', 'Y', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']



for file in data_file_names:
    compound_base = file.split('_')[0]
    with open(file) as f:
        data = f.readlines()
    #i know this shit ugly af but whatever
    elements1 = []
    elements2 = []
    temperatures = []
    is_direct = []

    both_3d_elements1 = []
    both_3d_elements2 = []
    both_3d_temperatures = []
    both_3d_is_direct = []

    first_3d_elements1 = []
    first_3d_elements2 = []
    first_3d_temperatures = []
    first_3d_is_direct = []

    second_3d_elements1 = []
    second_3d_elements2 = []
    second_3d_temperatures = []
    second_3d_is_direct = []

    none_3d_elements1 = []
    none_3d_elements2 = []
    none_3d_temperatures = []
    none_3d_is_direct = []

    
    both_rare_elements1 = []
    both_rare_elements2 = []
    both_rare_temperatures = []
    both_rare_is_direct = []

    first_rare_elements1 = []
    first_rare_elements2 = []
    first_rare_temperatures = []
    first_rare_is_direct = []

    second_rare_elements1 = []
    second_rare_elements2 = []
    second_rare_temperatures = []
    second_rare_is_direct = []

    none_rare_elements1 = []
    none_rare_elements2 = []
    none_rare_temperatures = []
    none_rare_is_direct = []

    temp_splits_1 = [[], [], [], [], [], [], []] #7 bins now
    temp_splits_2 = [[], [], [], [], [], [], []] 
    temp_splits_temperatures = [[], [], [], [], [], [], []] #7 bins now
    temp_splits_is_direct = [[], [], [], [], [], [], []] #7 bins now
    cnt_dir = 0
    cnt_indir = 0
    rare_none_cnt_dir = 0
    rare_none_cnt_indir = 0
    rare_first_cnt_dir = 0
    rare_first_cnt_indir = 0
    rare_both_cnt_dir = 0
    rare_both_cnt_indir = 0
    ddd_none_cnt_dir = 0
    ddd_none_cnt_indir = 0
    ddd_both_cnt_dir = 0
    ddd_both_cnt_indir = 0
    ddd_first_cnt_dir = 0
    ddd_first_cnt_indir = 0
    for line in data[1:]:
        element1, element2, temperature, direct = line.strip().split(',')
        elements1.append(element1)
        elements2.append(element2)
        temperatures.append(float(temperature)) #should be energies but whatever
        if direct == 'True':
            is_direct.append(True)
        elif direct == 'False':
            is_direct.append(False)
        for index in range(len(temp_splits_1)): #bins of 1 eV width, downward leaning
            if float(temperature) >= index and float(temperature) < index + 1:
                temp_splits_1[index].append(element1)
                temp_splits_2[index].append(element2)
                temp_splits_temperatures[index].append(float(temperature))
                if direct == 'True':
                    temp_splits_is_direct[index].append(True)
                elif direct == 'False':
                    temp_splits_is_direct[index].append(False)
        #3d sites
        #both
        if element1 in elements_3d and element2 in elements_3d:
            both_3d_elements1.append(element1)
            both_3d_elements2.append(element2)
            both_3d_temperatures.append(float(temperature))
            if direct == 'True':
                both_3d_is_direct.append(True)
            elif direct == 'False':
                both_3d_is_direct.append(False)
        #first
        if element1 in elements_3d and not (element2 in elements_3d):
            first_3d_elements1.append(element1)
            first_3d_elements2.append(element2)
            first_3d_temperatures.append(float(temperature))
            if direct == 'True':
                first_3d_is_direct.append(True)
            elif direct == 'False':
                first_3d_is_direct.append(False)
        #second
        
        if not (element1 in elements_3d )and element2 in elements_3d:
            first_3d_elements1.append(element1)
            first_3d_elements2.append(element2)
            first_3d_temperatures.append(float(temperature))
            if direct == 'True':
                first_3d_is_direct.append(True)
            elif direct == 'False':
                first_3d_is_direct.append(False)
        #none
        if not (element1 in elements_3d) and not (element2 in elements_3d):
            none_3d_elements1.append(element1)
            none_3d_elements2.append(element2)
            none_3d_temperatures.append(float(temperature))
            if direct == 'True':
                none_3d_is_direct.append(True)
            elif direct == 'False':
                none_3d_is_direct.append(False)

        #rare earths
        #both
        if element1 in rare_earths and element2 in rare_earths:
            both_rare_elements1.append(element1)
            both_rare_elements2.append(element2)
            both_rare_temperatures.append(float(temperature))
            if direct == 'True':
                both_rare_is_direct.append(True)
            elif direct == 'False':
                both_rare_is_direct.append(False)
        #first
        if element1 in rare_earths and not (element2 in rare_earths):
            first_rare_elements1.append(element1)
            first_rare_elements2.append(element2)
            first_rare_temperatures.append(float(temperature))
            if direct == 'True':
                first_rare_is_direct.append(True)
            elif direct == 'False':
                first_rare_is_direct.append(False)
        #first
        if not (element1 in rare_earths )and element2 in rare_earths:
            first_rare_elements1.append(element1)
            first_rare_elements2.append(element2)
            first_rare_temperatures.append(float(temperature))
            if direct == 'True':
                first_rare_is_direct.append(True)
            elif direct == 'False':
                first_rare_is_direct.append(False)
        #none
        if not (element1 in rare_earths) and not (element2 in rare_earths):
            none_rare_elements1.append(element1)
            none_rare_elements2.append(element2)
            none_rare_temperatures.append(float(temperature))
            if direct == 'True':
                none_rare_is_direct.append(True)
            elif direct == 'False':
                none_rare_is_direct.append(False)

    all_indirects = is_direct.count(False)
    all_directs = is_direct.count(True)
    rare_none_indirects = none_rare_is_direct.count(False)
    rare_none_directs = none_rare_is_direct.count(True)
    rare_first_indirects = first_rare_is_direct.count(False)
    rare_first_directs = first_rare_is_direct.count(True)
    rare_both_indirects = both_rare_is_direct.count(False)
    rare_both_directs = both_rare_is_direct.count(True)
    ddd_none_indirects = none_3d_is_direct.count(False)
    ddd_none_directs = none_3d_is_direct.count(True)
    ddd_first_indirects = first_3d_is_direct.count(False)
    ddd_first_directs = first_3d_is_direct.count(True)
    ddd_both_indirects = both_3d_is_direct.count(False)
    ddd_both_directs = both_3d_is_direct.count(True)
    print(f"all: direct={all_directs}, indirect={all_indirects}")

    print(f"none 3d: direct={ddd_none_directs}, indirect={ddd_none_indirects}")

    print(f"one 3d: direct={ddd_first_directs}, indirect={ddd_first_indirects}")

    print(f"both 3d: direct={ddd_both_directs}, indirect={ddd_both_indirects}")

    print(f"none rare: direct={rare_none_directs}, indirect={rare_none_indirects}")

    print(f"one rare: direct={rare_first_directs}, indirect={rare_first_indirects}")

    print(f"both rare: direct={rare_both_directs}, indirect={rare_both_indirects}")

    # all
    all_unique_elements = list(set(elements1 + elements2))
    all_temperature_array, all_indirect_bandgap = get_array(all_unique_elements, is_direct, temperatures, elements1, elements2)
    #both 3d
    both_3d_unique_elements = list(set(both_3d_elements1 + both_3d_elements2))
    both_3d_temperature_array, both_3d_indirect_bandgap = get_array(both_3d_unique_elements, both_3d_is_direct, both_3d_temperatures, both_3d_elements1, both_3d_elements2)
    #first 3d
    first_3d_unique_elements = list(set(first_3d_elements1 + first_3d_elements2))
    first_3d_temperature_array, first_3d_indirect_bandgap = get_array(first_3d_unique_elements, first_3d_is_direct, first_3d_temperatures, first_3d_elements1, first_3d_elements2)
    #first 3d
    first_3d_unique_elements = list(set(first_3d_elements1 + first_3d_elements2))
    first_3d_temperature_array, first_3d_indirect_bandgap = get_array(first_3d_unique_elements, first_3d_is_direct, first_3d_temperatures, first_3d_elements1, first_3d_elements2)
    #none 3d
    none_3d_unique_elements = list(set(none_3d_elements1 + none_3d_elements2))
    none_3d_temperature_array, none_3d_indirect_bandgap = get_array(none_3d_unique_elements, none_3d_is_direct, none_3d_temperatures, none_3d_elements1, none_3d_elements2)
    #rare earths
    #both
    both_rare_unique_elements = list(set(both_rare_elements1 + both_rare_elements2))
    both_rare_temperature_array, both_rare_indirect_bandgap = get_array(both_rare_unique_elements, both_rare_is_direct, both_rare_temperatures, both_rare_elements1, both_rare_elements2)
    #first 
    first_rare_unique_elements = list(set(first_rare_elements1 + first_rare_elements2))
    first_rare_temperature_array, first_rare_indirect_bandgap = get_array(first_rare_unique_elements, first_rare_is_direct, first_rare_temperatures, first_rare_elements1, first_rare_elements2)
    #first
    #first_rare_unique_elements = list(set(first_rare_elements1 + first_rare_elements2))
    #first_rare_temperature_array, first_rare_indirect_bandgap = get_array(first_rare_unique_elements, first_rare_is_direct, first_rare_temperatures, first_rare_elements1, first_rare_elements2)
    #none
    none_rare_unique_elements = list(set(none_rare_elements1 + none_rare_elements2))
    none_rare_temperature_array, none_rare_indirect_bandgap = get_array(none_rare_unique_elements, none_rare_is_direct, none_rare_temperatures, none_rare_elements1, none_rare_elements2)
    
    #temperature bins
    for index in range(len(temp_splits_1)): #bins of 1 eV width, downward leaning  
        temp_bin_unique_elements = list(set(temp_splits_1[index] + temp_splits_2[index]))
        temp_bin_temperature_array, temp_bin_indirect_bandgap = get_array(temp_bin_unique_elements, temp_splits_is_direct[index], temp_splits_temperatures[index], temp_splits_1[index] , temp_splits_2[index])
        f_size = 12
        dot_size = 1
        if temp_bin_unique_elements:
            create_plot(temp_bin_temperature_array, temp_bin_indirect_bandgap, temp_bin_unique_elements, f_size, compound_base, dot_size, 'temp' + str(index))
      
    
    #noooo dont look at me
    f_size = 6 #scale these somehow
    dot_size = 1
    f_size = 6 if compound_base == 'Cl' else 12
    dot_size = 0.3 if compound_base == 'Cl' else 1
    if all_unique_elements:
        create_plot(all_temperature_array, all_indirect_bandgap, all_unique_elements, f_size, compound_base, dot_size, 'all')
    #3ds
    #only matters for cl
    f_size = 12
    dot_size = 1
    if both_3d_unique_elements: 
        create_plot(both_3d_temperature_array, both_3d_indirect_bandgap, both_3d_unique_elements, f_size, compound_base, dot_size, 'both_3d')
    #only matters for cl
    f_size = 9
    dot_size = 1 #whatever, more clear
    if first_3d_unique_elements:
        create_plot(first_3d_temperature_array, first_3d_indirect_bandgap, first_3d_unique_elements, f_size, compound_base, dot_size, 'first_3d')
    #only Cl
    f_size = 6
    dot_size = 0.5
    #if first_3d_unique_elements:
    #    create_plot(first_3d_temperature_array, first_3d_indirect_bandgap, first_3d_unique_elements, f_size, compound_base, dot_size, 'first_3d')
    #both matter
    f_size = 6 if compound_base == 'Cl' else 12
    dot_size = 0.5 if compound_base == 'Cl' else 1
    if none_3d_unique_elements:
        create_plot(none_3d_temperature_array, none_3d_indirect_bandgap, none_3d_unique_elements, f_size, compound_base, dot_size, 'none_3d')
   
    #rare earths
    #never happens
    if both_rare_unique_elements: 
        create_plot(both_rare_temperature_array, both_rare_indirect_bandgap, both_rare_unique_elements, f_size, compound_base, dot_size, 'both_rare')
    #only cl
    f_size = 9
    dot_size = 1
    if first_rare_unique_elements:
        create_plot(first_rare_temperature_array, first_rare_indirect_bandgap, first_rare_unique_elements, f_size, compound_base, dot_size, 'first_rare')
    #only cl
    f_size = 9
    dot_size = 1
    #if first_rare_unique_elements:
    #    create_plot(first_rare_temperature_array, first_rare_indirect_bandgap, first_rare_unique_elements, f_size, compound_base, dot_size, 'first_rare')
    #both matter
    f_size = 6 if compound_base == 'Cl' else 12
    dot_size = 0.5 if compound_base == 'Cl' else 1
    if none_rare_unique_elements:
        create_plot(none_rare_temperature_array, none_rare_indirect_bandgap, none_rare_unique_elements, f_size, compound_base, dot_size, 'none_rare')
    
