# -*- coding: utf-8 -*-
"""
Functions for handling idle signals.

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
import itertools
import numpy as np

def _get_idle_ranges(min_idle_len, seek_step, idle_starts):
    # combine the silence we detected into ranges (start index - end index)
    idle_ranges = []

    prev_i = idle_starts.pop(0)
    current_range_start = prev_i

    for idle_start_i in idle_starts:
        continuous = (idle_start_i == prev_i + seek_step)

        # sometimes two small blips are enough for one particular slice to be
        # non-idle, despite the idle parts all running together. Just combine
        # the two overlapping idle ranges.
        idle_has_gap = idle_start_i > (prev_i + min_idle_len)

        if not continuous and idle_has_gap:
            idle_ranges.append([current_range_start,
                                prev_i + min_idle_len])
            current_range_start = idle_start_i
        prev_i = idle_start_i

    idle_ranges.append([current_range_start,
                        prev_i + min_idle_len])
                        
    return idle_ranges

def _get_idle_starts(signal, min_idle_len, idle_thresh, seek_step, use_rms):
    # find idle and add start and end indicies to the to_cut list
    idle_starts = []

    # check successive (1 sample by default) chunk of signal for idle
    # try a chunk at every "seek step" (or every chunk for a seek step == 1)
    last_slice_start = len(signal) - min_idle_len
    slice_starts = range(0, last_slice_start + 1, seek_step)

    # guarantee last_slice_start is included in the range
    # to make sure the last portion of the audio is searched
    if last_slice_start % seek_step:
        slice_starts = itertools.chain(slice_starts, [last_slice_start])

    for i in slice_starts:
        thissignal = signal.iloc[i:i + min_idle_len]
        value_to_check = max(thissignal)-min(thissignal)
        if use_rms:
            value_to_check = np.sqrt(np.mean(thissignal**2))  # use RMS instead
            
        if  value_to_check <= idle_thresh:
            idle_starts.append(i)
    
    return idle_starts

def detect_idle(
        signal, 
        min_idle_len=1000, 
        idle_thresh=20, 
        seek_step=1,
        use_rms=True
    ):
    """Returns a list of all idle sections [start, end] as indices.
    Inverse of detect_nonidle()

    Args:
        signal (pandas dataframe): the dataframe to find idle signal in
        min_idle_len (int, optional): the minimum length for any idle section. 
                                      Defaults to 1000.
        idle_thresh (int, optional): the upper bound for how low idle is
                                     in absolute values. Defaults to 20.
        seek_step (int, optional):  step size for interating over the segment. 
                                    Defaults to 1.

    Returns:
        list: idle ranges
    """
    # you can't have an idle portion of a signal that is longer than the signal
    if len(signal) < min_idle_len:
        return []

    idle_starts = _get_idle_starts(signal, 
                                   min_idle_len, 
                                   idle_thresh, 
                                   seek_step, 
                                   use_rms)

    # short circuit when there is no idle
    if not idle_starts:
        return []

    idle_ranges = _get_idle_ranges(min_idle_len, seek_step, idle_starts)

    return idle_ranges

def _get_nonidle_ranges(idle_ranges, len_seg):
    # if there is no idle part, the whole signal is idle
    if not idle_ranges:
        return [[0, len_seg]]

    # short circuit when the whole signal is idle
    if idle_ranges[0][0] == 0 and idle_ranges[0][1] == len_seg:
        return []

    prev_end_i = 0
    end_i = 0
    nonidle_ranges = []
    for start_i, end_i in idle_ranges:
        nonidle_ranges.append([prev_end_i, start_i])
        prev_end_i = end_i

    if end_i != len_seg:
        nonidle_ranges.append([prev_end_i, len_seg])

    if nonidle_ranges[0] == [0, 0]:
        nonidle_ranges.pop(0)
    
    return nonidle_ranges

def detect_nonidle(
        signal, 
        min_idle_len=1000, 
        idle_thresh=20, 
        seek_step=1
    ):
    """
    Returns a list of all nonsilent sections [start, end] in milliseconds of 
    audio_segment.
    Inverse of detect_silent()
    audio_segment - the segment to find silence in
    min_silence_len - the minimum length for any silent section
    silence_thresh - the upper bound for how quiet is silent in dFBS
    seek_step - step size for interating over the segment in ms
    """
    idle_ranges = detect_idle(signal, min_idle_len, idle_thresh, seek_step)
    
    return _get_nonidle_ranges(idle_ranges, len(signal))

# from the itertools documentation
def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def split_on_ranges(signal, ranges, keep_idle=100):
    """
    Returns list of audio segments from splitting audio_segment on silent 
    sections
    audio_segment - original pydub.AudioSegment() object
    min_silence_len - (in ms) minimum length of a silence to be used for
        a split. default: 1000ms
    silence_thresh - (in dBFS) anything quieter than this will be
        considered silence. default: -16dBFS
    keep_silence - (in ms or True/False) leave some silence at the beginning
        and end of the chunks. Keeps the sound from sounding like it
        is abruptly cut off.
        When the length of the silence is less than the keep_silence duration
        it is split evenly between the preceding and following non-silent
        segments.
        If True is specified, all the silence is kept, if False none is kept.
        default: 100ms
    seek_step - step size for interating over the segment in ms
    """
    if isinstance(keep_idle, bool):
        keep_idle = len(signal) if keep_idle else 0

    output_ranges = [
        [start - keep_idle, end + keep_idle] 
        for (start,end) in ranges
    ]

    for range_i, range_ii in _pairwise(output_ranges):
        last_end = range_i[1]
        next_start = range_ii[0]
        if next_start < last_end:
            range_i[1] = (last_end + next_start) // 2
            range_ii[0] = range_i[1]

    return [
        signal.iloc[max(start,0):min(end,len(signal))]
        for start,end in output_ranges
    ]

def split_on_idle(
        signal, 
        min_idle_len=1000, 
        idle_thresh=20, 
        keep_idle=100,
        seek_step=1):
    """
    Returns list of audio segments from splitting audio_segment on silent 
    sections
    audio_segment - original pydub.AudioSegment() object
    min_silence_len - (in ms) minimum length of a silence to be used for
        a split. default: 1000ms
    silence_thresh - (in dBFS) anything quieter than this will be
        considered silence. default: -16dBFS
    keep_silence - (in ms or True/False) leave some silence at the beginning
        and end of the chunks. Keeps the sound from sounding like it
        is abruptly cut off.
        When the length of the silence is less than the keep_silence duration
        it is split evenly between the preceding and following non-silent
        segments.
        If True is specified, all the silence is kept, if False none is kept.
        default: 100ms
    seek_step - step size for interating over the segment in ms
    """
    return split_on_ranges(
        signal, 
        detect_nonidle(signal, min_idle_len, idle_thresh, seek_step),
        keep_idle)

def detect_leading_idle(signal, idle_threshold=-50.0, chunk_size=10):
    """
    Returns the millisecond/index that the leading silence ends.
    audio_segment - the segment to find silence in
    silence_threshold - the upper bound for how quiet is silent in dFBS
    chunk_size - chunk size for interating over the segment in ms
    """
    trim_ms = 0 # ms
    assert chunk_size > 0 # to avoid infinite loop
    while signal[trim_ms:trim_ms+chunk_size].dBFS < idle_threshold \
        and trim_ms < len(signal):
        trim_ms += chunk_size

    # if there is no end it should return the length of the segment
    return min(trim_ms, len(signal))
