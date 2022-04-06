# -*- coding: utf-8 -*-
"""
Functions for signal normalization.

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

def normalize(f):
    """return signal normalized to min/max"""
    maxf = max(f)
    minf = min(f)
    return ((f - maxf) + (f - minf)) / (maxf - minf)  # return normalized sig.

def normalize_to_interval(f, interval=(-500, 500)):
    """return signal normalized to given interval"""
    return \
        ((f - interval[1]) + (f - interval[0])) / (interval[1] - interval[0])
