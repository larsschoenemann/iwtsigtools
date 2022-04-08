# -*- coding: utf-8 -*-
"""
Logging functions.

Code taken from the pydub package (https://github.com/jiaaro/pydub) and 
modified for handling dataframes/signals.
Originally licensed under the MIT license.

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


def start_logger(loglevel=logging.INFO):
    """Start a custom logger.

    Args:
        loglevel (loggin.LOGLEVEL, optional): Logging level.
            Defaults to logging.INFO.

    Returns:
        RootLogger: The logger.
    """
    newlog = logging.getLogger(__package__)
    if not newlog.handlers:
        formatter = logging.Formatter(
            "%(asctime)s: [%(levelname)s] %(message)s")
        chandler = logging.StreamHandler()
        chandler.setLevel(logging.DEBUG)
        chandler.setFormatter(formatter)
        newlog.addHandler(chandler)
    newlog.setLevel(loglevel)
    return newlog

def get_logger():
    return logging.getLogger(__package__)