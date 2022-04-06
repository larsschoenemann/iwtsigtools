"""Test for importing measurements"""
from pathlib import Path

import matplotlib  # pylint: disable=W0611
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
import iwtsigtools as iwtsig

def onselect(vmin, vmax):
    """handling of span_selection"""
    print(f'min =  {vmin}, max = {vmax}')
    print(f'span =  {vmax - vmin}')

def main():
    """main function"""
    dir_name = Path(__file__).resolve().parent
    file_name = "2022-03-29_FeTiB_n001-n010.tdms"

    measurement_df, metadata = iwtsig.load_mesusoft_measurement(
        Path(dir_name).joinpath(file_name))
    print(metadata)

    fc_df = np.sqrt(measurement_df['Fx']**2 
                  + measurement_df['Fy']**2 
                  + measurement_df['Fz']**2)

    axis = fc_df.plot()
    span = SpanSelector(
        axis,
        onselect,
        "vertical",
        useblit=True,
        props=dict(alpha=0.5, facecolor="tab:blue"),
        interactive=True,
        drag_from_anywhere=True
    )
    plt.show(block=True)
    my_threshold = 50
    if span._selection_completed:  #pylint: disable=W0212
        my_threshold = span.extents[1] - span.extents[0]
    # 

    ranges = iwtsig.detect_nonidle(
        fc_df, 
        min_idle_len=1000, 
        seek_step=1000, idle_thresh=my_threshold)
    cutting_signals = iwtsig.split_on_ranges(
        measurement_df, ranges, keep_idle=0)
    _, axes = plt.subplots(len(measurement_df.columns), 1, sharex=True)
    
    # plotting
    for sig in cutting_signals:
        for axis, component in zip(axes, sig):
            axis.plot(sig[component])
    plt.show(block=True)

    # export
    iwtsig.save_dataframe_to_tdms(
        Path(dir_name).joinpath(
            f'{Path(file_name).stem[:-9]}_n001{Path(file_name).suffix}'),
        cutting_signals[0],
        metadata
    )

if __name__ == '__main__':
    main()
