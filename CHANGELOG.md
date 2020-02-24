# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This changelog is based on a previous changelog that had to depricated and removed due to the transition to GitHub.

## [0.0.6] - 2020-02-24
### Changed
* chrome now opens with a subprocess and not webbrowser package (is order to facilitage force killing of the process).
* Application will not overwrite if there was an excuse put on the date.

### Added
* CLI option: `overwrite-values`.  
This option is `False` by default. 
By default, if there are values already set in the time edit window, the application will not overwrite them.  
If it is set to `True` it will overwrite current time values in the date edit windows. Otherwise 

## [0.0.5] - 2020-02-20
### Changed
* default search radius has been updated to 300 meters

### bugfixes
* added better execptions (better messages) in case parameters file has missing work lat/long values

## [0.0.4] - 2020-02-20
### Changed
* Token aquisition is done only once per Timewatch session

### Bugfix [issue #5](https://github.com/bouncingjack/twu/)
* Bug - when multiple days are entered. The session does not transition well between edit windows. Therefore the next day recieves the wrong window to search for user token.
    * Fix - check for token before searching for it. If it exists, do nothing.

## [0.0.3]
### Added
* Timewatch fill based on timeline or spoofing

## [0.0.2]
### Added
* Timewatch login
* kml file download
* kml file parsing
* work detection
* linux support
* readme sections


## [0.0.1]
### Added
* Basic flow - still not working


## [0.0.0]
### Added
* Outlines for all modules
* Changelog
