# TimeWatch Automatic Filler

Automate timewatch updating.
* single day/batch
* Mode 1: Based on actual Google Timeline
* Mode 2: Based on randomized entry and exit times.
* Automatically update holidays and holiday eves
* Allow to insert an excuse with/without hours for each day


# TOC
* [Requirements](##Requirements)  
* [Install](##Install)  
* [Use](##Use)
---


## Requirements
* Active timeline in google (for timeline option)
* Python >= 3.6 
* [python requirements](requirements.txt)
* logged in Chrome session
* Supported chrome is version 75. Other chrome versions will require to replace the chromedriver in executables directory.
---


## Install
Install all required pacakges pacakges
```
pip install -r requirements.txt
```
Create a parameters file (name and location are up to you).  
this file should contains the following JSON:  
(parameters are explained in the section [Params](#params))
```
{
    "download_dir": "<full path>",
    "user": {
        "company": "x*", 
        "worker": "y*",
        "pswd": "p*"
    },
    "work": {
        "lat": "xx.yyyyyy",
        "long": "xx.yyyyyy"
    },
    "holiday_index":{
        "vacation_index": x,
        "vacation_text": ["y", "z",],
        "eve_index": "k",
        "eve_text": ["m", "n", ...]
    }
}

``` 
---
### Google
Make sure you chrome is logged in to your Google account.

---
### Params
**_download_dir_** - Download path for kml files from google  
**_user.company_** - Company ID No.  
**_user.worker_** - Workder ID No.  
**_user.pswd_** - password for login.  
[**_work.lat/long_**](###geo_data) - lat and long of location of the work place
[**_holiday_index.vaction_index_**](#holiday-index) - index in the excuse list for a holiday option
[**_holiday_index.eve_index_**](#holiday-index) - index in the excuse list for holiday eve option
[**_holiday_index.vacation_text_**](#holiday-index) - textual description of the day for holiday (list of ascii values)  
[**_holiday_index.eve_text_**](#holiday-index) - textual description of the day for holiday eve (list of ascii values)  


---
### Geo Data
  
Go to [Google Maps](https://www.google.co.il/maps) 
and extract the exact coordinates from the location:

    right click on the address:
    whats here?
    
Select Decimal Gegrees notation:
    
    32.166525, 34.812895 

should be entered into parameters JSON as
    
    "work": {
        "lat": "32.166525",
        "long": "34.812895"
    }
    

---

### holiday index
This part of the parameters data adds the indexes for holdiay and holiday eve in the excuse list in the site.

`vacation_index` and `eve_index` are the indeces (zero based) of the respective option on the excuse select box

`vacation_text` and `eve_text` is the textual description of this day in ascii notation.
Using ascii in order to enable other languages other than english without (hopefully) encoding problems.

You can find ascii encoding our using `ord`:
```
description = 'vacation day'
[ord(x) for x in description]

>>>
[118, 97, 99, 97, 116, 105, 111, 110, 32, 100, 97, 121]
```


if not existing will set to the following defaults:
```
"holiday": {
    "holdiay_eve_index": 3,
    "holiday_eve_text": [1506, 1512, 1489, 32, 1495, 1490],
    "holiday_index": 17,
    "holiday_text": [1495, 1490]
  }
```

## Use


### Using Google timeline data
date range:
    
    python timewatch.py --start-date 01-11-2019 --end-date 22-11-2019

single specific date (overrides --start-date/--end-date):
```
python timewatch.py --specific-date 13-11-2019
```
equivalently enter the same date in start and end:
```
python timewatch.py --start-date 13-11-2019 --end-date 13-11-2019
```
---
### parameters file
By default the parameters file is `params` in the root of this project (protected by .gitignore).  
If you wish to change:

```
    python timewatch.py --start-date 01-11-2019 --end-date 22-11-2019 --parameters-file <full path to file>
```
---

### Random time spoofing (No Google timelne)
Randomizes arrival and leave time around provided values with +- 43 minutes. 
    
date range
```
python timewatch.py --start-date 01-11-2019 --end-date 22-11-2019 --force-time 07:30 19:22
```
single specific date:
```
python timewatch.py --specific-date 13-11-2019 --force-time 07:30 19:22
```
---

### Overwrite values
By default, if the date has already been filled with time values **OR** if there is an excuse filled in, the application **WILL NOT** overwrite the values.

If you want to overwrite time values:
#### Google timeline
```
python timewatch.py --start-date 01-11-2019 --end-date 22-11-2019 --overwrite-values
```
#### spoofing
```
python timewatch.py --start-date 01-11-2019 --end-date 22-11-2019 --force-time 07:30 19:22 --overwrite-values
```
__________________________

### insert excuse
Add excuse (with or without hours)
Enter the excuse index as an argument together with date range. 
The result will be populating all the working dates withing this range with this excuse.

The excuse list is different between companies.

The default mode is to NOT use this setting.
```
python timewatch.py --start-date 01-11-2019 --end-date 22-11-2019 --excuse 7
```

## Real-world Example
Craete a spoof of times with an excuse - overwrite values
```
python timewatch.py --start-date 01-04-2019 --end-date 30-04-2019 --overwrite-values --excuse-index 16 --force-times 07:00 17:30
```
_________________
## Style Guide

We are following the [google python style guide](https://google.github.io/styleguide/pyguide.html).

Docstrings should also follow google's style guide, see examples in [google docstring example](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

All the modules should also follow [pep8](https://www.python.org/dev/peps/pep-0008/) (just use pyCharm it gives all the errors and warnings about pep8).

