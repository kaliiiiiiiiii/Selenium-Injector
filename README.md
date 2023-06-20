# Selenium-Injector

* Change proxy while running (auth supported)
* remotely contoll Chrome using websockets and extensions

### Feel free to test my code!

## Getting Started

### Dependencies

* [Python >= 3.7](https://www.python.org/downloads/)
* [Chrome-Browser](https://www.google.de/chrome/) installed
* Selenium

### Installing

* [Windows] Install [Chrome-Browser](https://www.google.de/chrome/)
* ```pip install selenium_injector```


### Example scripts


#### click on element
```python
from selenium_injector.webdriver import Chrome
# from selenium.webdriver import Chrome as base_driver
from undetected_chromedriver import Chrome as base_driver

driver = Chrome(base_driver=base_driver)

driver.get("https://www.wikipedia.org/")
driver.driverless.socket.exec_command("utils.find_element.ByXpath", '//*[@id="js-link-box-en"]/strong', user=driver.driverless.tab_user)

js = driver.driverless.socket.js
t = js.types
u = js.utils

try:
    prev_url = driver.current_url[:]
    driver.driverless.socket.exec(u.click_element(u.find_element_by_xpath('//*[@id="js-link-box-en"]/strong')), user=driver.driverless.tab_user, timeout=2)
except TimeoutError as e:
    # noinspection PyUnboundLocalVariable
    if driver.current_url != prev_url:
        pass
    else:
        raise e

driver.quit()
```
Don't forget to execute
`driver.quit()`
in the End. Else-wise your temporary folder will get flooded! and it keeps running

#### set proxy dynamically
```python
from selenium_injector.webdriver import Chrome
driver = Chrome()

driver.driverless.proxy.set(host="example_host.com", port=143, password="password", username="user-1")

driver.get("https://whatismyipaddress.com/")

driver.driverless.proxy.clear()
driver.quit()
```


## Help

Please feel free to open an issue or fork!

## Todo

- [ ] Add MV2 extension
  - [ ] change headers
- [ ] add events
  - [ ] make protocoll use `UUIDS`'s
- [x] types.eval
  - [ ] for-loops
  - [x] async execution
- [x] authentificaten proxies
  - [x] manage webrtc-leak
  - [x] manage location api leak
  - [ ] proxy per request
- [ ] add `chrome.scripting` support
- [ ] add automation tools
  - [x] click
  - [ ] send_keys
  - [ ] find_element
    - [x] by XPATH
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
* [make-SV-stayalive](https://stackoverflow.com/a/75082732/20443541)
