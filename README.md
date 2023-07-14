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

#### set proxy dynamically
```python
from selenium_injector.webdriver import Chrome
driver = Chrome()

driver.injector.proxy.set_single(host="example_host.com", port=143, password="password", username="user-1")

driver.get("https://whatismyipaddress.com/")

driver.injector.proxy.clear()
driver.quit()
```
Don't forget to execute
`driver.quit()`
in the End. Else-wise your temporary folder will get flooded! and it keeps running

#### use events
```python
from selenium_injector.webdriver import Chrome
import json

driver = Chrome()

driver.get("chrome://version")

t = driver.injector.socket.js.types

event_id = driver.injector.socket.make_event_id()
user = driver.injector.any_user

driver.injector.socket.exec(t.list([
    t.set_event_id(event_id),
    t.exec(
        t.path("chrome.webRequest.onCompleted.addListener"),
        args=[t.event_callback(), t.value({"urls": ["<all_urls>"]})]
    )
]), user=user, max_depth=1)

event = driver.injector.socket.event(event_id, user=user)
for e in event:  # will block forever
    e = json.loads(e)
    data = e["result"][0]
    time = e["t"]
    print(time + "\n", data['url'])
```
warning: as `driver.quit()` isn't called in this example, it will leave files in your temp directories

#### modify network requests
note: this is only experimental yet (not included in pypi package)

example script
```python
from selenium_injector.webdriver import Chrome

driver = Chrome()

# modify headers
driver.injector.declarativeNetRequest.update_headers({"test": "test_2", "sec-ch-ua-platform": "Android"})
rules = driver.injector.declarativeNetRequest.dynamic_rules
headers = driver.injector.declarativeNetRequest._headers

driver.get("https://httpbin.org/headers")
input("press ENTER to continue")

# block images
driver.injector.declarativeNetRequest.update_block_on(resource_types=["image"])

driver.get("https://www.wikimedia.org/")

input("press ENTER to exit")
driver.quit()
```

#### use chrome-developer-protocoll
note: this is only experimental yet (not included in pypi package)

example script
```python
import json
from selenium_injector.webdriver import Chrome

driver = Chrome()

dbg = driver.injector.debugger
dbg.attach()
dbg.execute("Console.enable")

events = dbg.on_event()

driver.execute_script("console.log('Hello World!')")

for event in events:
    event = json.loads(event)
    result = event["result"]
    time = event["t"]
    if result[1] == 'Console.messageAdded':
        message_text = result[2]["message"]["text"]
        print(time, message_text)
        break

driver.quit()
```

#### execute script within tab
note: this is only experimental yet (not included in pypi package)

from string
```python
from selenium_injector.webdriver import Chrome
driver = Chrome(injector_options={"mv2":True, "mv3":True})

driver.get("https://www.wikipedia.org/")

# result only returned with mv2 extension enabled
results = driver.injector.tabs.eval_str(
            '''
            console.log(window);
            navigator.userAgent
            ''', tab_id=driver.injector.tabs.active_tab["id"])
print(results[0])

driver.quit()
```

with types, always returns
resolves promises with MV3 automatically
```python
from selenium_injector.webdriver import Chrome
driver = Chrome(injector_options={"mv3":True})

driver.get("https://www.wikipedia.org/")

t = driver.injector.socket.js.types
results = driver.injector.tabs.exec(t.exec(t.path("fetch"), args=[t.value("https://www.wikipedia.org/")]), timeout=40)
print(results["result"][0])

driver.quit()
```

#### find element
note: this is only experimental yet (not included in pypi package)
```python
from selenium_injector.webdriver import Chrome
from selenium_injector.types.by import By

driver = Chrome(injector_options={"mv2":True, "mv3":True})
driver.get("https://www.wikipedia.org/")


elem = driver.injector.find_elements(By.XPATH, '//*[@id="js-link-box-en"]')
elem[0].click()

driver.quit()
```

## Help

Please feel free to open an issue or fork!

## Todo
- [x] eval within tab scope from extension
  - [x] mv2
    - [x] return 
    - [ ] stringify obj
  - [x] mv3
    - [ ] return
    - [ ] stringify obj
- [x] add events
  - [x] make protocoll use `UUIDS`'s
  - [ ] allow response to event within scope
    - using `(...args) => {new event_handler(...args)}`
- [x] types.eval
  - [ ] for-loops
- [x] authentificaten proxies
  - [x] manage webrtc-leak
  - [x] manage location api leak
  - [ ] proxy per request
- [ ] add automation tools
  - [x] click
  - [ ] send_keys
  - [ ] find_element
    - [x] by XPATH
- [ ] undetectability
  - [x] make tab scripts private
  - [x] support base_driver argument
  - [ ] make `/files/js/utils.js` private
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
* [stringify-obj](https://stackoverflow.com/a/58416333/20443541)
* [inject code from mv3](https://stackoverflow.com/a/70949953/20443541)
