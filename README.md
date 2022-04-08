# IWT signal handling tools

Various tools to handle signal processing. Mainly developed to handle
measurements made using IWT MesuSoft, but should be applicable to arbitrary
signals as well.

## Functions

### File handling

- `ui_get_file_path` helper function to select a file via a GUI for further
  handling  
- `get_mesusoft_measurement` reads an IWT MesuSoft Measurement and saves it as
  a dataframe  
- `save_dataframe_to_tdms` save a dataframe to a TDMS file  

### Idle detection

These functions are inspired by the
[pydub package v0.25.1](https://github.com/jiaaro/pydub)  
(c) James Robert, MIT License

- `detect_idle` detect idle segments in a measurements, i.e. rms amplitude  
  or peak-to-valley below a given threshold, returns index ranges  
- `detect_nonidle` inverse of detect idle  
- `split_on_ranges` split a dataframe at given ranges  
- `split_on_idle` split a dataframe on idle segments  
- `detect_leading_idle` detect leading idle in a dataframe  

### Signal normalization

- `normalize` normalize a signal to `[min|max]`
- `normalize_to_interval` normalize a signal to a given interval

## Classes

- none  

## Usage

### Example: handle machining data with idle segments

Force measurements from raster milling operations are characterized by
featuring relevant measurement data, i.e. when the cutter is engaged in cutting
as well as idle portions when the cutter is not engaged, e.g. as the machine is
repositioning. The idle detection functions are applied in this case to
separate the measurements in chunks of relevant data and saved bach to new
TDMS files.

- use `ui_get_file_path` to get filename or use a string/Path object
- read the measurement to a dataframe with `get_mesusoft_measurement`
- manipulate dataframe, e.g. by `split_on_idle`
- save manipulated dataframe to new TDMS using `save_dataframe_to_tdms`

## Contact

Leibniz-Institute for Materials Engineering IWT  
Laboratory for Precision Machining LFM  
Dr.-Ing. Lars Schönemann  
Badgasteiner Straße 3  
28359 Bremen  
Germany  
schoenemann@iwt.uni-bremen.de
