# -*- coding: utf-8 -*-
"""
Functions for signal import.

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

@author: Dr.-Ing. Lars Schönemann
@contact: schoenemann@iwt.uni-bremen.de
@address: LFM Laboratory for Precision Machining
          Leibniz-Institut für Werkstofforientierte Technologien IWT
          Badgasteiner Straße 2
          28359 Bremen
          Germany
@version: 0.1
@date:    2022-04-06
"""
import nptdms
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

def _merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def load_mesusoft_measurement(file_name, print_info=False):
    """Load a measurement made in MesuSoft and saved as TDMS

    Args:
        file_name (str): the name of the file to load
        print_info (book): print additional information to the console
                           (Default is False)

    Returns:
        dataframe: measurement dataframe
        dict: metadata
    """
    with nptdms.TdmsFile.open(file_name) as tdms_file:
        # read first group of file (should be "Measuring")
        group_name = str(
            tdms_file.groups()[0]
            ).partition("'")[2].partition("'")[0]
        group = tdms_file[group_name]
        
        # read channels as pandas dataframe
        if print_info:
            print('This group has the following channels:')
            print(group.channels())
        
        measurement_df = group.as_dataframe()
        # set index to first columns (should be "Time")
        measurement_df.set_index(measurement_df.columns[0], inplace=True)

        if print_info:
            print(f'read to dataframe with columns {measurement_df.columns}')
        
    # measurement_df.plot(subplots=True)
    metadata = {
        'RootProperties': tdms_file.properties,
        'GroupName': group_name,
        'GroupProperties': group.properties
    }
    return measurement_df, metadata

def save_dataframe_to_tdms(filename, dataframe, metadata=None):
    """Save a dataframe to a TDMS file.
    Intended for force measurements with measurment time as index.

    Args:
        filename (str): the file name
        dataframe (pd.dataframe): the dataframe to save, 
                                  Note: The index is always saved as an 
                                  additional column 'Time'
        metadata (dict): metadata to save, preferrably of the original TDMS
    """
    if metadata is None:
        metadata = {'RootProperties': '',
                    'GroupName': 'Measuring'}
    
    root_object = nptdms.RootObject(properties=metadata['RootProperties'])
    group_object = nptdms.GroupObject(
        metadata['GroupName'], 
        properties=metadata['GroupProperties'])
    
    channel_objects = [nptdms.ChannelObject(
        metadata['GroupName'], sig, list(dataframe[sig]), properties={})
        for sig in dataframe]

    time_object = nptdms.ChannelObject(
        metadata['GroupName'], 'Time', list(dataframe.index), properties={})

    with nptdms.TdmsWriter(filename) as tdms_writer:
        # Write first segment
        tdms_writer.write_segment([
                root_object,
                group_object,
                time_object])
        for channel_object in channel_objects:
            tdms_writer.write_segment([
                channel_object])

def ui_get_file_path(dir_name, file_types=None):
    """Use graphical interfaces to select files and get the file path

    Args:
        dir_name (str): start directory name
        file_types (list, optional): List of allowed file types. A file type
                                     is a tuple of ('name', '.ext').
                                     Defaults to [('All files', '*.*')].

    Returns:
        str: Path of the selected file. Empty string on cancel.
    """
    parent_dir = Path.cwd()

    if not file_types:
        file_types = [('All files', '*.*')]

    if not dir_name.is_dir():
        print(f'directory {dir_name} does not exist '
              f'using {parent_dir} instead')
        dir_name = parent_dir
    
    # hide root window -> we only want the file dialog
    root = tk.Tk()
    root.withdraw()

    file_path = ''
    try: 
        file_path = filedialog.askopenfilename(
            initialdir=dir_name.as_posix(), filetypes=file_types)
    except Exception as this_exception: 
        print(this_exception)

    return file_path
