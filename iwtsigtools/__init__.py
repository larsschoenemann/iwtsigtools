# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
IWT Signal Handling Tools

Copyright (C) 2022  Lars Schönemann
Leibniz Institut für Werkstofforientierte Technologien IWT, Bremen, Germany
"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('iwtsigtools')
except PackageNotFoundError:
    # package is not installed
    pass

from .filehandling import (get_start_from_filename, load_mesusoft_measurement,
                           save_dataframe_to_tdms, ui_get_file_name, 
                           export_chunks)
from .idle import (detect_idle, detect_leading_idle, detect_nonidle,
                   split_on_idle, split_on_ranges)
from .logging import get_logger, start_logger
from .normalization import normalize, normalize_to_interval
from .processdataframe import process_dataframe
