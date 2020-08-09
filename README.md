# TimeWatch Automatic Filler

Automate timewatch updating.
* Automatically update holidays and holiday eves
* Automatically decides when at office and when to inset excuse


[TOC]

---


## Requirements
* Active timeline in google (for timeline option)
* Python >= 3.6 
* [python requirements](requirements.txt)
* logged in Chrome session
* Supported chrome is version 75. Other chrome versions will require to replace the chromedriver in executables directory.
---


## Install
> **Optional** [Create and activate a new virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments) 

Install local package using pip and local path
```
pip install -e <project path>
```

After the installation - Update the parameters in the [Parameters File](params/params.json) according to the [Parameters section](#parameters)

### Parameters

* `download_dir`: The full path to the default download directory of the pc.
 If removed, the default will be  `C:\Users\<user>\Downloads (windows)` or `/home/<user>/Downloads (linux)`

* `user` - login information
    * `company`  - company No.
    * `worker` - worker ID number
    * `pswd` - password

* `work` This is information about the work place: 
    * `location`: lat and long (see [Geo Data](#geo_data))
    * `work_day`: information regarding the work day
        * `max_length`: maximum length (in hours) of the workday
        * `nominal_length`: nominal length (in hours) of the workday
        * `minimal_start_time`: minimal start time (will never set arrival before this time)
        * `maximal_end_time`: maximal end time (will never set departure after this time)
* `home`: information about home
    * `work_from_home_excuse_index`: index of the option for setting the excuse to working from home - this may change from company to company.
* `holdiay`: information about how to recognize holiday. This is meant for non-english parts of the webpage. In order to compare - utilize the ascii representation of each character.
    * `holiday_eve_index`: the index of the holiday **eve** option
    * `holiday_eve_text`: ascii for the holiday **eve** option text,
    * `holiday_index`: the index of the holiday  option
    * `holiday_text`: ascii for the holiday option text,


## Time at work calculation
#### GPS
Based on Google timeline data.
Requires a logged-in chrome session (until further notice).
GPS data is taken from the parsed KML file that can be downloaded per a single date which 
describes a single day timeline data.

#### Non-GPS
If GPS data did not indicate that user was a work, the mode switches to non-gps.
This means that either eve/holiday or work from home which requires setting an appropriate excuse.

#### Holidays
Holidays are detected from the headline in the single day edit menu in the web page.
The headline is compared to the ascii representation of the specific language in which the web page is written.
Holidays are set according the index (zero based) provided in the parameters (index of the correct option in the drop down menu when manually setting).

i.e:
If clicking on the drop down menu in the single day edit web-page is:
* hi
* holiday_eve
* holiday
* bye

Then 
* `holiday_index = 3` 
* `holiday_eve_index = 2`
* `holiday_text = [104, 111, 108, 105, 100, 97, 121]`
* `holiday_eve_text = [104, 111, 108, 105, 100, 97, 121, 95, 101, 118, 101]`

You can find ascii encoding our using the built-in function `ord()`:
```
description = 'vacation day'
[ord(x) for x in description]

>>>
[118, 97, 99, 97, 116, 105, 111, 110, 32, 100, 97, 121]
```
---
### Geo Data
  
Go to [Google Maps](https://www.google.co.il/maps) 
and extract the exact coordinates from the location:
```
right click on the address:
whats here?
```

Select Decimal Degrees notation:

|Lat|Long|
|:----|:----|
|32.166525|32.166525|


should be entered into parameters JSON as
    
    "work": {
        "location": {
            "lat": "32.166525",
            "long": "34.812895"
        }
    }
    
-----


## Usage
### Basic usage
> Assuming the parameters file is configured according to [Params section](#create_a_parameters_file) and the [example parameters file](params/params.json)


#### Run for a time period
```
python --start-date 01-07-2020 --end-date 31-07-2020
```

#### Run for a single date
Use the same date for start and end
```
python --start-date 01-07-2020 --end-date 01-07-2020
```

_________________
## Style Guide

We are following the [google python style guide](https://google.github.io/styleguide/pyguide.html).

Docstrings should also follow google's style guide, see examples in [google docstring example](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

All the modules should also follow [pep8](https://www.python.org/dev/peps/pep-0008/) (just use pyCharm it gives all the errors and warnings about pep8).

