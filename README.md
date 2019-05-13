# SiteChecker
SiteChecker is command line python script that checks if sites changed, then push notification via [Pushbullet](https://docs.pushbullet.com/).

## Requirement
- Python 3.5 or higher
- [Pushbullet](https://docs.pushbullet.com/) API token

## Installation
1. `git clone https://github.com/Makeeyaf/SiteChecker`
1. Make python3 virtual environment
1. `pip install -r requirements.txt` in virtual environment

## How to use
### Add sites
Add new element to `Sites` in [data.json](https://github.com/Makeeyaf/SiteChecker/blob/master/data.json)  
Sample element
```json
{
  "name": "",
  "url": "",
  "pattern": "",
  "lastUpdate": "",
  "enabled": 1,
  "failCount": 0,
  "lastData": []
}
```
1. `name`: Name of item
1. `url`: Url to parse
1. `pattern`: [CSS Selector pattern](https://facelessuser.github.io/soupsieve/selectors/)
1. `lastUpdate`: Leave it empty
1. `enabled`: Set 1
1. `failCound`: Leave it 0
1. `lastData`: Leave it []

### Arguments
```
usage: SiteChecker.py [-h] -a APIKEY [-m MAXFAILCOUNT] [-u UPDATECYCLE] [-v]
                      [-q]
                      config

Check sites text.

positional arguments:
  config           Path to config json file.

optional arguments:
  -h, --help       show this help message and exit
  -a APIKEY        Pushbullet API key.
  -m MAXFAILCOUNT  Max fail count.
  -u UPDATECYCLE   Update cycle in second
  -v               Verbose mode.
  -q               Quiet mode. Does not call pushbullet
```
Simplest usage example: `python SiteChecker.py data.json -a Pushbullet_API_Token`

### Run with Crontab example
1. `crontab -e`
1. `* * * * * /usr/bin/env bash -c 'cd /VirtualEnvironmentPath/ && source /VirtualEnvironmentPath/bin/activate && python SiteChecker.py work.json -a API_KEY -v' >> cron.log 2>&1`

## Lisence
[MIT Lisence](https://github.com/Makeeyaf/SiteChecker/blob/master/LICENSE)
