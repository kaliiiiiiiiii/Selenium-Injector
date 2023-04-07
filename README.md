# Selenium-Injector

* Change proxy while running (auth supported)
* remotely execute functions within a Chrome-Extension

### Feel free to test my code!

## Getting Started

### Dependencies

* [Python >= 3.7](https://www.python.org/downloads/)
* [Chrome-Browser](https://www.google.de/chrome/) installed
* Selenium

### Installing

* [Windows] Install [Chrome-Browser](https://www.google.de/chrome/)
* ```pip install selenium_injector```


### Example script

```python
from selenium_profiles import driver as mydriver
from selenium_profiles.profiles import profiles

from selenium_injector.injector import injector

injector = injector()

mydriver = mydriver()
profile = profiles.Windows()
profile["options"]["extensions"] = {"extension_paths": [injector.path]}

driver = mydriver.start(profile, uc_driver=False)


input("Enable proxy\n")
injector.exec_command("proxy.set", ["http", "host", 41149])
injector.exec_command("proxy.set_auth", ["username", "password"])

input("Disable proxy\n")
injector.exec_command("proxy.clear")

input("Press ENTER to quit")
injector.stop()
driver.quit()
```
Don't forget to execute
`driver.quit()`
in the End. Else-wise your temporary folder will get flooded! and it keeps running

### Change proxy while running

```python
from selenium_injector.injector import injector
injector = injector(host="localhost", port = 8001)

# initialize chrome here & load the extension
# options.add_argument("--load-extension="+injector.path) # as argument
# profile["options"]["extensions"] = {"extension_paths": [injector.path]} # selenium-profiles

injector.exec_command("proxy.set", ["http", "host", 41149, True, True]) # patch_webrtc = True, patch_location=True by default
injector.exec_command("proxy.set_auth", ["username", "password"])

input("Disable proxy\n")
injector.exec_command("proxy.clear")
```

### Disable webrtc-ip-leak
```python
from selenium_injector.injector import injector
injector = injector()

# initialize chrome here & load the extension here

injector.exec_command("webrtc_leak.disable")
injector.exec_command("webrtc_leak.clear") # reset webrtc
```
### block location api
```python
from selenium_injector.injector import injector
injector = injector()

# initialize chrome here & load the extension here

injector.exec_command("contentsettings.set_location", ["block"])
injector.exec_command("contentsettings.set_location", ["allow"]) # reset api policies
```

for all available scripts, have a look at [selenium_injector/files/injector_extension/background.js](https://github.com/kaliiiiiiiiii/Selenium-Injector/blob/master/src/selenium_injector/files/injector_extension/background.js)

## Help

Please feel free to open an issue or fork!

## Todo

- [ ] Add MV2 extensiom
  - [ ] change headers
- [ ] add events
- [x] types.eval
  - [ ] for-loops
- [x] authentificaten proxies
  - [x] manage webrtc-leak
  - [x] manage locatiom api leak
  - [ ] proxy per request

## Deprecated

## Authors

[Aurin Aegerter](mailto:aurinliun@gmx.ch)

## License

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

## Disclaimer

I am not responsible what you use the code for!!! Also no warranty!

## Acknowledgments

Inspiration, code snippets, etc.
* [Selenium-Profiles](https://github.com/kaliiiiiiiiii/Selenium-Profiles)
* [Chrome-devtools-protocol](https://chromedevtools.github.io/devtools-protocol/tot/Fetch/#method-enable)
* [cdp_event_listeners](https://stackoverflow.com/questions/66227508/selenium-4-0-0-beta-1-how-add-event-listeners-in-cdp)
* [sync websocket server](https://stackoverflow.com/questions/68939894/implement-a-python-websocket-listener-without-async-asyncio)
* [chrome-extension-docs](https://developer.chrome.com/docs/extensions/reference/)
* [PEG-parser](https://github.com/pegjs/pegjs)
