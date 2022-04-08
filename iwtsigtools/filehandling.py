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
import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import nptdms
import pandas as pd

log = logging.getLogger(__package__)

def load_mesusoft_measurement(file_name):
    """Load a measurement made in MesuSoft and saved as TDMS

    Args:
        file_name (str): the name of the file to load
        
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
        log.info(
            f'Group {group_name} has the following channels: '
            f'{group.channels()}')
        
        measurement_df = group.as_dataframe()
        # set index to first columns (should be "Time")
        measurement_df.set_index(measurement_df.columns[0], inplace=True)

        log.info(f'Read to dataframe with columns {measurement_df.columns}')
        
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

def ui_get_file_name(dir_name, **kwargs):
    """Use graphical interfaces to select files and get the file path.

    Args:
        dir_name (str): start directory name
        file_types (list, optional): List of allowed file types. A file type
                                     is a tuple of ('name', '.ext').
                                     Defaults to [('All files', '*.*')].

    Returns:
        str: Path of the selected file. Empty string on cancel.
    """
    parent_dir = Path.cwd()
    
    file_types = kwargs.get('file_types', None)
    select_multiple_files = kwargs.get('multiple', False)

    if not file_types:
        file_types = [('All files', '*.*')]

    if isinstance(dir_name, str):
        dir_name = Path(dir_name)
    
    if not dir_name.is_dir():
        log.warning(
            f'directory {dir_name} does not exist '
            f'using {parent_dir} instead')
        dir_name = parent_dir
    
    root = tk.Tk()
    # hide root window -> we only want the file dialog
    root.withdraw() 
    # bring file dialog to top
    root.call('wm', 'attributes', '.', '-topmost', True)

    file_name = ''
    try: 
        file_name = filedialog.askopenfilename(
            initialdir=dir_name.as_posix(), 
            filetypes=file_types, 
            multiple=select_multiple_files)
    except Exception as open_filename_exception: 
        log.error(open_filename_exception)

    return file_name

def export_chunks(file_name, metadata, cutting_signals, start_num=0):
    """Export signals to individual TDMS files

    Args:
        file_path (str): The file's name.
        metadata (dict): Dictionary of metadata to use for TDMS export.
        cutting_signals (list of dataframes): The signals to export.
        start_num (int, optional): Start export numbering at start_num + 1. 
                                   Defaults to 0. (i.e. start at 1)
    """
    log.info('Starting export.')
    for i, cutting_signal in enumerate(cutting_signals):
        save_dataframe_to_tdms(Path(file_name).parent.joinpath(
                (f'{Path(file_name).stem}_{i+start_num:03d}'
                 f'{Path(file_name).suffix}')),
            cutting_signal,
            metadata
        )
    log.info(f'Finished exporting {len(cutting_signals)} files.')

def get_start_from_filename(file_name, num_elements, identifier='n'):
    """Get line numbers from file name. (optional, start at 1 on fail)

    Args:
        file_name (str): The file's  name.
        num_elements (int): Number of elements to check against
        identifier (str, optional): Identifier to extract numbering.
                                    Expects digits follwing the string. 
                                    Defaults to 'n'.

    Returns:
        int: starting line number
    """
    # 
    start_num = 0
    line_numbers = pd.Series(Path(file_name).stem).str.extractall(
        f'{identifier}' r'(\d+)').astype(int).to_numpy().flatten()
    if len(line_numbers) > 1:
        if line_numbers[1] - line_numbers[0] + 1 != num_elements:
            log.warning('Something went wrong, unclear number of segments. '
                        'Check output files!!!')
            # return
    if len(line_numbers) > 0:
        start_num = line_numbers[0]
    log.info(f'Start index is {start_num}')
    return start_num
