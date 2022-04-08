# -*- coding: utf-8 -*-
"""Exemplary use of iwtsigtools.

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
import logging
# from logging import getLogger as log
from pathlib import Path
import tkinter as tk
from configparser import ConfigParser

import matplotlib  # pylint: disable=W0611
import matplotlib.pyplot as plt
import iwtsigtools as iwtsig

log = logging.getLogger('iwtsigtools')

def read_config(config_name):
    """Read an ini-based configuration

    Args:
        config_name (str): ini file name (in current working directory)

    Returns:
        dict: dictionary with config items
    """
    config = ConfigParser()
    config.read(Path.cwd().joinpath(config_name), encoding='utf-8')
    
    dir_name = Path(config.get('DEFAULT', 'data_dir', 
                    fallback=Path.cwd()))
    
    file_types = config.get('DEFAULT', 'file_types', 
                            fallback=[('All files', '*.*')])
    if isinstance(file_types, str):
        file_types = file_types.split('|')
        file_types = [tuple(ftype.split(',')) for ftype in file_types]
    
    default_treshold = config.getfloat('DEFAULT', 'default_treshold',
                                       fallback=42.0)
    seek_step_ratio = config.getfloat('DEFAULT', 'seek_step_ratio',
                                       fallback=0.03)
    
    return {'data_dir': dir_name, 
            'file_types': file_types,
            'default_threshold': default_treshold,
            'seek_step_ratio': seek_step_ratio}


def main():
    """main function"""
    plt.ion()
    iwtsig.start_logger(logging.INFO)
    
    # An ini-based configuration is used here, mainly to provide two settings
    # data_dir (str) and file_types (list of string tuples [(str, str)])
    config = read_config('iwtsigtools.ini')
    
    # Convenience function to open a files via the GUI
    file_names = iwtsig.ui_get_file_name(
        config['data_dir'], file_types=config['file_types'], multiple=True)
    if not file_names:
        log.error('No file selected, exiting...')
        return
    
    export_dir = tk.filedialog.askdirectory()
    if not export_dir:
        log.error('No directory selected, exiting.')
        return
    
    for file_name in file_names:
        # load the measurement data and metadata
        log.info(f'Loading file {file_name}')
        measurement_df, metadata = iwtsig.load_mesusoft_measurement(
            Path(file_name))
        log.debug(metadata)
        config['sampling_rate'] = metadata['GroupProperties']['SamplingRate']
        
        # processing
        cutting_signals = iwtsig.process_dataframe(measurement_df, **config)
        start_num = iwtsig.get_start_from_filename(
            file_name, len(cutting_signals), 'n')
        
        log.info(f'Saving files to {export_dir}')
        
        iwtsig.export_chunks(
            Path(export_dir).joinpath(Path(file_name).name), 
            metadata, cutting_signals, start_num)

if __name__ == '__main__':
    main()
