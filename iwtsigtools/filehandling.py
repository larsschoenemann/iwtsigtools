# -*- coding: utf-8 -*-
"""
Functions for signal import.

Copyright (C) 2022  Lars Schönemann

This library is free software; you can redistribute it and/or modify 
it under the terms of the GNU Lesser General Public License as published by 
the Free Software Foundation; either version 2.1 of the License, or 
(at your option) any later version.

This library is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License 
along with this library; if not, write to the Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

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

def _merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def load_mesusoft_measurement(file_name, print_info=False):
    """Load a measurement made in MesuSoft and saved as TDMS

    Args:
        file_name (_type_): _description_

    Returns:
        _type_: _description_
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

def save_dataframe_to_tdms(filename, dataframe, metadata):
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
