"""Test for importing measurements"""
from pathlib import Path

import matplotlib  # pylint: disable=W0611
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from configparser import ConfigParser, NoOptionError
import numpy as np
import pandas as pd
import iwtsigtools as iwtsig
import tkinter as tk

def onselect(vmin, vmax):
    """handling of span_selection"""
    print(f'min =  {vmin}, max = {vmax}')
    print(f'span =  {vmax - vmin}')
    

def main():
    """main function"""
    config = ConfigParser()
    config.read(Path.cwd().joinpath('iwtsigtools.ini'))
    print('Please select file')
    file_path = iwtsig.ui_get_file_path(config)

    if not file_path:
        print('No file selected, exiting...')
        return

    measurement_df, metadata = iwtsig.load_mesusoft_measurement(
        Path(file_path))
    print(metadata)

    fc_df = np.sqrt(measurement_df['Fx']**2 
                  + measurement_df['Fy']**2 
                  + measurement_df['Fz']**2)

    axis = fc_df.plot()
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

    ranges = iwtsig.detect_nonidle(
        fc_df, 
        min_idle_len=1000, 
        seek_step=1000, idle_thresh=my_threshold)
    cutting_signals = iwtsig.split_on_ranges(
        measurement_df, ranges, keep_idle=0)
    _, axes = plt.subplots(len(measurement_df.columns), 1, sharex=True)
    
    # plotting
    for sig in cutting_signals:
        for axis, component in zip(axes, sig):
            axis.plot(sig[component])
    plt.show(block=True)
    
    # export
    line_numbers = pd.Series(Path(file_path).stem).str.extractall(
        r'n(\d+)').astype(int).to_numpy().flatten()
    num_el = line_numbers[1] - line_numbers[0] + 1
    
    if num_el != len(cutting_signals):
        print('Something went wrong, unclear number of segments')
        return
    
    export_dir = Path(tk.filedialog.askdirectory())
    for i, cutting_signal in enumerate(cutting_signals):
        # i = 0
        iwtsig.save_dataframe_to_tdms(Path(export_dir).joinpath(
                (f'{Path(file_path).stem[:-9]}_n{i+line_numbers[0]:03d}'
                 f'{Path(file_path).suffix}')),
            cutting_signals[i],
            metadata
        )

if __name__ == '__main__':
    main()
