import logging

import numpy as np
import matplotlib  # pylint: disable=W0611
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from .idle import detect_nonidle, split_on_ranges

log = logging.getLogger(__package__)

def onselect(vmin, vmax):
    """handling of span_selection"""
    print(f'min =  {vmin}, max = {vmax}')
    print(f'span =  {vmax - vmin}')
    
def process_dataframe(measurement_df, **kwargs):
    # Calculate resulting force F_res = sqrt(Fx^2+Fy^2+Fz^2)
    # Assumption: first three columns contain force values for x,y,z
    f_res_df = np.sqrt(measurement_df[measurement_df.columns[0]]**2 
                     + measurement_df[measurement_df.columns[1]]**2 
                     + measurement_df[measurement_df.columns[2]]**2)

    sampling_rate = kwargs.get(
        'sampling_rate', 
        1/(measurement_df.index[1]-measurement_df.index[0]))
    idle_threshold = kwargs.get(
        'default_threshold', 50.0)
    seek_step_ratio = kwargs.get(
        'seek_step_ratio', 0.025)
    
    # plot f_res for selection of idle thresholds
    axis = f_res_df.plot()
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
    if span._selection_completed:  #pylint: disable=W0212
        log.info(f'Manually selected min =  '
                   f'{span.extents[0]}, max = {span.extents[1]}')
        idle_threshold = span.extents[1] - span.extents[0]
    log.info(f'selected threshold =  {idle_threshold}')
    
    # detect nonidle segments, seek step is based on actual sampling rate
    log.info(f'Sampling rate is {sampling_rate} -> using seek step of '
               f'{int(np.ceil(sampling_rate*seek_step_ratio))} '
               f'({seek_step_ratio*100} %)')
    ranges = detect_nonidle(
        f_res_df, 
        seek_step=int(np.ceil(sampling_rate*seek_step_ratio)), 
        idle_thresh=idle_threshold)
    
    # split signals at detected ranges
    cutting_signals = split_on_ranges(
        measurement_df, ranges, keep_idle=0)
    log.info(f'Detected {len(cutting_signals)} nonidle segments.')
    
    # plot split signals in common plot
    _, axes = plt.subplots(
        len(measurement_df.columns), 1, sharex=True, sharey=True)
    for sig in cutting_signals:
        for axis, component in zip(axes, sig):
            axis.plot(sig[component])
    plt.show(block=True)
    return cutting_signals