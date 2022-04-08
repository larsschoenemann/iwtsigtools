# -*- coding: utf-8 -*-
"""
Functions for signal normalization.

Copyright (C) 2022  Lars Schönemann
Leibniz Institut für Werkstofforientierte Technologien IWT, Bremen, Germany

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

log = logging.getLogger(__package__)

def normalize(f):
    """return signal normalized to min/max"""
    maxf = max(f)
    minf = min(f)
    return ((f - maxf) + (f - minf)) / (maxf - minf)  # return normalized sig.

def normalize_to_interval(f, interval=(-500, 500)):
    """return signal normalized to given interval"""
    return \
        ((f - interval[1]) + (f - interval[0])) / (interval[1] - interval[0])
