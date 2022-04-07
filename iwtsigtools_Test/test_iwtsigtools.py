# -*- coding: utf-8 -*-
"""Test for importing measurements

Copyright (C) 2022  Lars Schönemann

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
"""
from pathlib import Path
import tkinter as tk
from configparser import ConfigParser

import matplotlib  # pylint: disable=W0611
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
import pandas as pd
import iwtsigtools as iwtsig

def onselect(vmin, vmax):
    """handling of span_selection"""
    print(f'min =  {vmin}, max = {vmax}')
    print(f'span =  {vmax - vmin}')

def read_config(config_name):
    """Read an ini-based configuration

    Args:
        config_name (str): ini file name (in current working directory)

    Returns:
        dict: dictionary with config items
    """
    config = ConfigParser()
    config.read(Path.cwd().joinpath(config_name))
    
    dir_name = Path(config.get('DEFAULT', 'data_dir', 
                    fallback=Path.cwd()))
    file_types = config.get('DEFAULT', 'file_types', 
                            fallback=[('All files', '*.*')])
    
    if isinstance(file_types, str):
        file_types = file_types.split('|')
        file_types = [tuple(ftype.split(',')) for ftype in file_types]
    
    return {'data_dir': dir_name, 'file_types': file_types}

def main():
    """main function"""
    # An ini-based configuration is used here, mainly to provide two strings
    # data_dir (str) and file_types (list of string tuples [(str, str)])
    config = read_config('iwtsigtools.ini')
    
    # Convenience function to open a file via the GUI
    print('Please select file')
    file_path = iwtsig.ui_get_file_path(
        config['data_dir'], file_types=config['file_types'])

    if not file_path:
        print('No file selected, exiting...')
        return

    # load the measurement data and metadata
    measurement_df, metadata = iwtsig.load_mesusoft_measurement(
        Path(file_path))
    print(metadata)

    # Calculate resulting force F_res = sqrt(Fx^2+Fy^2+Fz^2)
    # Assumption: first three columns contain force values for x,y,z
    f_res_df = np.sqrt(measurement_df[measurement_df.columns[0]]**2 
                     + measurement_df[measurement_df.columns[1]]**2 
                     + measurement_df[measurement_df.columns[2]]**2)

    # plot f_res for selection of idle thresholds
    axis = f_res_df.plot()
    span = SpanSelector(
        axis,
        onselect,
        "vertical",
        useblit=True,
        props=dict(alpha=0.5, facecolor="tab:orange"),
        interactive=True,
        drag_from_anywhere=True
    )
    plt.show(block=True)
    my_threshold = 50
    if span._selection_completed:  #pylint: disable=W0212
        my_threshold = span.extents[1] - span.extents[0]

    # detect nonidle segments, seek step is based on actual sampling rate
    sampling_rate = metadata['GroupProperties']['SamplingRate']
    ranges = iwtsig.detect_nonidle(
        f_res_df, 
        min_idle_len=int(np.ceil(sampling_rate*0.025)), 
        seek_step=int(np.ceil(sampling_rate*0.025)), 
        idle_thresh=my_threshold)
    
    # split signals at detected ranges
    cutting_signals = iwtsig.split_on_ranges(
        measurement_df, ranges, keep_idle=0)
    
    # plot split signals in common plot
    _, axes = plt.subplots(
        len(measurement_df.columns), 1, sharex=True, sharey=True)
    for sig in cutting_signals:
        for axis, component in zip(axes, sig):
            axis.plot(sig[component])
    plt.show(block=True)
    
    # get line numbers from file name (optional, start at 1 on fail)
    line_numbers = pd.Series(Path(file_path).stem).str.extractall(
        r'n(\d+)').astype(int).to_numpy().flatten()
    start_num = 0
    if len(line_numbers) > 1:
        if line_numbers[1] - line_numbers[0] + 1 != len(cutting_signals):
            print('Something went wrong, unclear number of segments')
            return
    if len(line_numbers) > 0:
        start_num = line_numbers[0]
    
    # export to individual TDMS files
    export_dir = Path(tk.filedialog.askdirectory())
    for i, cutting_signal in enumerate(cutting_signals):
        iwtsig.save_dataframe_to_tdms(Path(export_dir).joinpath(
                (f'{Path(file_path).stem[:-9]}_n{i+start_num:03d}'
                 f'{Path(file_path).suffix}')),
            cutting_signal,
            metadata
        )

if __name__ == '__main__':
    main()
