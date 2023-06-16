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
from selenium_profiles.webdriver import Chrome
from selenium_profiles.profiles import profiles

from selenium_injector.injector import mv3_injector as injector

injector = injector()

profile = profiles.Windows()
profile["options"]["extension_paths"] = [injector.path]

mydriver = Chrome(profile,uc_driver=False)
driver = mydriver.start()


input("Enable proxy\n")
injector.proxy.set("host", 41149, scheme="http", username="username",password="password")

input("Disable proxy\n")
injector.proxy.clear()

input("Press ENTER to quit")
injector.stop()
driver.quit()
```
Don't forget to execute
`driver.quit()`
in the End. Else-wise your temporary folder will get flooded! and it keeps running

### Change proxy while running

```python
from selenium_injector.injector import mv3_injector as injector
injector = injector(host="localhost", port = 8001)

# initialize chrome here & load the extension
# options.add_argument("--load-extension="+injector.path) # as argument
# profile["options"]["extension_paths"] = [injector.path] # selenium-profiles

injector.proxy.set("host", 41149, scheme="http", username="username",password="password") # patch_webrtc = True, patch_location=True by default

input("Disable proxy\n")
injector.proxy.clear()
```

### Disable webrtc-ip-leak
```python
from selenium_injector.injector import mv3_injector as injector
injector = injector()

# initialize chrome here & load the extension here

injector.webrtc_leak.disable()
injector.webrtc_leak.clear() # reset webrtc
```
### block location api
```python
from selenium_injector.injector import mv3_injector as injector
injector = injector()

# initialize chrome here & load the extension here

injector.contentsettings.set_location(setting="ask")
injector.contentsettings.set_location(setting="allow")# reset api policies
```

for all available scripts, have a look at [selenium_injector/files/injector_extension/background.js](https://github.com/kaliiiiiiiiii/Selenium-Injector/blob/master/src/selenium_injector/files/injector_extension/background.js)

## Help

Please feel free to open an issue or fork!

## Todo

- [ ] Add MV2 extension
  - [ ] change headers
- [ ] add events
- [x] types.eval
  - [ ] for-loops
  - [x] async execution
- [x] authentificaten proxies
  - [x] manage webrtc-leak
  - [x] manage locatiom api leak
  - [ ] proxy per request
- [ ] add `chrome.scripting` support
- [ ] add automation tools
  - [ ] click
  - [ ] send_keys
  - [ ] find_element
    - [ ] by XPATH
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
