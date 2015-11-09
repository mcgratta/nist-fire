# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
from pylab import *
from itertools import cycle

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

#  =================
#  = User Settings =
#  =================

# Choose Test Number
current_test = 'Test_27_West_070814'

# Location of experimental data files
data_dir = '../Experimental_Data/'

# Location of file with timing information
all_times_file = '../Experimental_Data/All_Times.csv'

# Location of scaling conversion files
scaling_file_default = '../DAQ_Files/Delco_DAQ_Channel_List.csv'
scaling_file_master = '../DAQ_Files/Master_DelCo_DAQ_Channel_List.csv'
scaling_file_west = '../DAQ_Files/West_DelCo_DAQ_Channel_List.csv'
scaling_file_east = '../DAQ_Files/East_DelCo_DAQ_Channel_List.csv'

# Location of test description file
info_file = '../Experimental_Data/Description_of_Experiments.csv'

# Time averaging window for data smoothing
data_time_averaging_window = 5

# Duration of pre-test time for bi-directional probes and heat flux gauges (s)
pre_test_time = 60

# List of sensor groups for each plot
sensor_groups = [['TC_A1_'], ['TC_A2_'], ['TC_A3_'], ['TC_A4_'], ['TC_A5_'],
                 ['TC_A6_'], ['TC_A7_'], ['TC_A8_'], ['TC_A9_'], ['TC_A10_'],
                 ['TC_A11_'], ['TC_A12_'], ['TC_A13_'], ['TC_A14_'], ['TC_A15_'],
                 ['TC_A16_'], ['TC_A17_'], ['TC_A18_'], ['TC_A19_'],
                 ['TC_Ignition'],
                 ['TC_Helmet_'],
                 ['BDP_A4_'], ['BDP_A5_'], ['BDP_A6_'], ['BDP_A7_'],
                 ['BDP_A8_'], ['BDP_A9_'], ['BDP_A10_'], ['BDP_A11_'],
                 ['BDP_A12_'], ['BDP_A13_'], ['BDP_A14_'], ['BDP_A15_'],
                 ['BDP_A18_'],
                 ['HF_', 'RAD_'],
                 ['GAS_', 'CO_', 'CO2_', 'O2_'],
                 ['HOSE_']]

# Common quantities for y-axis labelling
heat_flux_quantities = ['HF_', 'RAD_']
gas_quantities = ['CO_', 'CO2_', 'O2_']

# Load exp. timings and description file
all_times = pd.read_csv(all_times_file)
all_times = all_times.set_index('Time')
info = pd.read_csv(info_file, index_col=3)

# Files to skip
skip_files = ['_times', '_reduced', 'description_']

#  ===============================
#  = Loop through all data files =
#  ===============================

for f in os.listdir(data_dir):
    if f.endswith('.csv'):

        # Skip files with time information or reduced data files
        if any([substring in f.lower() for substring in skip_files]):
            continue

        # Strip test name from file name
        test_name = f[:-4]
        print ('Test ' + test_name)

        # Option to specify which test is run
        if test_name != current_test:
          continue

        # Load exp. data file
        data = pd.read_csv(data_dir + f, index_col=0)

        # Uncomment the following two lines to run only DelCo June/July tests
        if 'Test' not in test_name:
            continue

        # Load exp. scaling file
        if 'West' in test_name:
            scaling_file = scaling_file_west
        elif 'East' in test_name:
            scaling_file = scaling_file_east
        else:
            scaling_file = scaling_file_default
        scaling = pd.read_csv(scaling_file, index_col=2)

        # Read in test times to offset plots
        start_of_test = info['Start of Test'][test_name]
        end_of_test = info['End of Test'][test_name]

        # Load exp. data file
        data = pd.read_csv(data_dir + f)
        data = data.set_index('TimeStamp(s)')

        # Offset data time to start of test
        data['Time'] = data['Time'].values - start_of_test

        # Smooth all data channels with specified data_time_averaging_window
        data_copy = data.drop('Time', axis=1)
        data_copy = pd.rolling_mean(data_copy, data_time_averaging_window, center=True)
        data_copy.insert(0, 'Time', data['Time'])
        data_copy = data_copy.dropna()
        data = data_copy
        #  ============
        #  = Plotting =
        #  ============

        # Generate a plot for each quantity group
        for group in sensor_groups:

            # Skip excluded groups listed in test description file
            if any([substring in group for substring in info['Excluded Groups'][test_name].split('|')]):
                continue

            fig = figure()

            # Plot style - colors and markers
            # These are the "Tableau 20" colors as RGB.
            tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                         (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                         (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                         (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                         (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

            # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
            for i in range(len(tableau20)):
                r, g, b = tableau20[i]
                tableau20[i] = (r / 255., g / 255., b / 255.)
            plt.rc('axes', color_cycle=tableau20)
            plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

            for channel in data.columns[1:]:

                # Skip excluded channels listed in test description file
                if any([substring in channel for substring in info['Excluded Channels'][test_name].split('|')]):
                    continue

                if any([substring in channel for substring in group]):

                    calibration_slope = float(scaling['Calibration Slope'][channel])
                    calibration_intercept = float(scaling['Calibration Intercept'][channel])

                    # Scale channel and set plot options depending on quantity
                    # Plot temperatures
                    if 'TC_' in channel:
                        quantity = data[channel] * calibration_slope + calibration_intercept
                        ylabel('Temperature ($^\circ$C)', fontsize=20)
                        line_style = '-'
                        if 'TC_Helmet_' in channel:
                            axis_scale = 'Y Scale TC_Helmet'
                        else:
                            axis_scale = 'Y Scale TC'
                        secondary_axis_label = 'Temperature ($^\circ$F)'
                        secondary_axis_scale = np.float(info[axis_scale][test_name]) * 9/5 + 32

                    # Plot velocities
                    if 'BDP_' in channel:
                        conv_inch_h2o = 0.4
                        conv_pascal = 248.8

                        # Convert voltage to pascals
                        # Get zero voltage from pre-test data
                        zero_voltage = np.mean(data[channel][0:pre_test_time])
                        pressure = conv_inch_h2o * conv_pascal * (data[channel] - zero_voltage)

                        # Calculate velocity
                        quantity = 0.0698 * np.sqrt(np.abs(pressure) * (data['TC_' + channel[4:]] + 273.15)) * np.sign(pressure)
                        ylabel('Velocity (m/s)', fontsize=20)
                        line_style = '-'
                        axis_scale = 'Y Scale BDP'
                        secondary_axis_label = 'Velocity (mph)'
                        secondary_axis_scale = np.float(info[axis_scale][test_name]) * 2.23694

                    # Plot heat fluxes
                    if any([substring in channel for substring in heat_flux_quantities]):

                        # Get zero voltage from pre-test data
                        zero_voltage = np.mean(data[channel][0:pre_test_time])
                        quantity = (data[channel] - zero_voltage) * calibration_slope + calibration_intercept
                        ylabel('Heat Flux (kW/m$^2$)', fontsize=20)
                        if 'HF' in channel:
                            line_style = '-'
                        elif 'RAD' in channel:
                            line_style = '--'
                        axis_scale = 'Y Scale HF'

                    # Plot gas measurements
                    if any([substring in channel for substring in gas_quantities]):
                        quantity = data[channel] * calibration_slope + calibration_intercept
                        ylabel('Concentration (%)', fontsize=20)
                        line_style = '-'
                        axis_scale = 'Y Scale GAS'

                    # Plot hose pressure
                    if 'HOSE_' in channel:
                        # Skip data other than sensors on 2.5 inch hoseline
                        if '2p5' not in channel:
                            continue
                        quantity = data[channel] * calibration_slope + calibration_intercept
                        ylabel('Pressure (psi)', fontsize=20)
                        line_style = '-'
                        axis_scale = 'Y Scale HOSE'

                    # Save converted quantity back to exp. dataframe
                    data[channel] = quantity

                    plot(data['Time'] , quantity, lw=1.5, ls=line_style, label=scaling['Test Specific Name'][channel])

            # Skip plot quantity if disabled
            if info[axis_scale][test_name] == 'None':
                continue

            # Scale y-axis limit based on specified range in test description file
            if axis_scale == 'Y Scale BDP':
                ylim([-np.float(info[axis_scale][test_name]), np.float(info[axis_scale][test_name])])
            else:
                ylim([0, np.float(info[axis_scale][test_name])])

            # Set axis options, legend, tickmarks, etc.
            ax1 = gca()
            handles1, labels1 = ax1.get_legend_handles_labels()
            xlim([0, end_of_test - start_of_test])
            ax1.xaxis.set_major_locator(MaxNLocator(8))
            ax1_xlims = ax1.axis()[0:2]
            grid(True)
            xlabel('Time', fontsize=20)
            xticks(fontsize=16)
            yticks(fontsize=16)

            # Secondary y-axis parameters
            if secondary_axis_label:
                ax2 = ax1.twinx()
                ax2.set_ylabel(secondary_axis_label, fontsize=20)
                plt.xticks(fontsize=16)
                plt.yticks(fontsize=16)
                if axis_scale == 'Y Scale BDP':
                    ax2.set_ylim([-secondary_axis_scale, secondary_axis_scale])
                else:
                    ax2.set_ylim([0, secondary_axis_scale])

            try:
                # Add vertical lines and labels for timing information (if available)
                ax3 = ax1.twiny()
                ax3.set_xlim(ax1_xlims)
                # Remove NaN items from event timeline
                events = all_times[test_name].dropna()
                # Ignore events that are commented starting with a pound sign
                events = events[~events.str.startswith('#')]
                [plt.axvline(_x - start_of_test, color='0.50', lw=1) for _x in events.index.values]
                ax3.set_xticks(events.index.values - start_of_test)
                plt.setp(plt.xticks()[1], rotation=60)
                ax3.set_xticklabels(events.values, fontsize=8, ha='left')
                plt.xlim([0, end_of_test - start_of_test])
                # Increase figure size for plot labels at top
                fig.set_size_inches(10, 6)
            except:
                pass
            plt.legend(handles1, labels1, loc='upper left', fontsize=8, handlelength=3)

            # Save plot to file
            print ('Plotting ', group)
            savefig('../Figures/Script_Figures/' + test_name + '_' + group[0].rstrip('_') + '.pdf')
            close('all')

        close('all')
        print

        # Write offset times and converted quantities back to reduced exp. data file
        data.to_csv(data_dir + test_name + '_Reduced.csv')
