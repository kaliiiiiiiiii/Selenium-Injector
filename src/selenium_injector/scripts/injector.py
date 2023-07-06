class base_injector:
    def __init__(self, socket, users: dict, injector):
        self.socket = socket
        self.users = users
        self.t = socket.js.types
        self.injector = injector

    def check_cmd(self, value, values):
        if value not in values:
            raise ValueError("Expected " + str(values) + " , but got" + str(value))

    @property
    def any_user(self):
        if "mv3" in self.users.keys():
            return self.users["mv3"]
        elif "mv2" in self.users.keys():
            return self.users["mv2"]
        else:
            raise ModuleNotFoundError("chrome not initialized with extensions")

    @property
    def mv3_user(self):
        if "mv3" in self.users.keys():
            return self.users["mv3"]
        else:
            raise ModuleNotFoundError("Chrome not initialized with mv3-extension")

    @property
    def mv2_user(self):
        if "mv2" in self.users.keys():
            return self.users["mv2"]
        else:
            raise ModuleNotFoundError("Chrome not initialized with mv2-extension")


def make_config(host: str, port: int, user: str, debug: bool or None = None):
    if debug:
        debug = "true"
    else:
        debug = "false"
    config = f"""
            (function(){{new connector("{host}",{str(port)}, "{user}", handler, {debug})}}())
                """
    return config


def make_extension(path: str, user: str, host: str, port: int, debug: bool, mv: int):
    from selenium_injector.utils.utils import read, write
    if mv not in [2, 3]:
        raise ValueError(f"mv needs to be 2 or 3, but got {mv}")

    config = make_config(host, port, user, debug=debug)
    background_js = read("files/extension/background.js", sel_root=True)
    manifest_json = read(f"files/extension/manifest_{mv}.json", sel_root=True)
    connection_js = read("files/js/connection.js", sel_root=True)

    background_js = background_js + connection_js + config
    if mv == 3:
        background_js = read("files/extension/stay_alive.js", sel_root=True) + background_js
    path = path + f"mv{mv}_extension"
    write(path + "/background.js", background_js, sel_root=False)
    write(path + "/manifest.json", manifest_json, sel_root=False)
    return path


class Injector(base_injector):
    # noinspection PyMissingConstructor
    def __init__(self, port: int = None, host: str = None, user: str = None, temp_dir: str = None,
                 debug: bool or None = None, mv2: bool = True, mv3: bool = True):
        from selenium_injector.scripts.socket import socket
        from selenium_injector.utils.utils import sel_injector_path, random_port

        if not host:
            host = "localhost"
        if not port:
            port = random_port(host=host)

        if temp_dir:
            path = temp_dir
        else:
            path = sel_injector_path() + "files/tmp/"

        if not user:
            user = f"selenium-injector-mv"
        if not (mv2 or mv3):
            raise ValueError("either mv3 or mv2 extension required")

        self.users = {}
        self.paths = []

        self.mv2 = mv2
        self.mv3 = mv3
        if mv2:
            mv_user = user + "_2"
            # noinspection PyTypeChecker
            self.users["mv2"] = mv_user
            self.paths.append(
                make_extension(host=host, port=port, user=mv_user, path=path, mv=2, debug=debug))
        if mv3:
            mv_user = user + "_3"
            # noinspection PyTypeChecker
            self.users["mv3"] = mv_user
            self.paths.append(
                make_extension(host=host, port=port, user=mv_user, path=path, mv=3, debug=debug)
            )

        self.socket = socket()
        self.socket.start(port=port, host=host)
        self.stop = self.socket.stop
        self.exec = self.socket.exec
        self.exec_command = self.socket.exec_command

        # subclasses
        kwargs = {"socket": self.socket, "users": self.users, "injector": self}
        self.proxy = self.proxy(**kwargs)
        self.webrtc_leak = self.webrtc_leak(**kwargs)
        self.contentsettings = self.contentsettings(**kwargs)
        self.tabs = self.tabs(**kwargs)
        self.declarativeNetRequest = self.declarativeNetRequest(**kwargs)
        self.cookies = self.cookies(**kwargs)
        self.debugger = self.debugger(**kwargs)

    @property
    def connection_js(self):
        from selenium_injector.utils.utils import read
        return read("files/js/connection.js", sel_root=True)

    @property
    def page_source(self):
        try:
            return self.socket.exec(self.socket.js.types.path("document.documentElement.outerHTML"),
                                    user="tab-0", timeout=1)["result"][0]
        except TimeoutError:
            # 'data:,' startup url
            return '<html><head></head><body></body></html>'

    @property
    def current_url(self):
        try:
            return self.tabs.active_tab['url']
        except TimeoutError:
            return None

    @property
    def title(self):
        try:
            return self.tabs.active_tab['title']
        except TimeoutError:
            return None

    class proxy(base_injector):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.supported_schemes = ["http", "https", "socks4", "socks5"]
            self.auth_user = self.any_user

        def _get(self, timeout: int = 1):
            req = self.t.exec(func=self.t.path("proxy.get"), args=[self.t.send_back()])
            req.update(self.t.not_return)
            return self.socket.exec(req, user=self.any_user, timeout=timeout, max_depth=4)["result"][0]

        @property
        def rules(self):
            try:
                return self._get()["value"]["rules"]
            except KeyError:
                return None

        @property
        def mode(self):
            return self._get()["value"]["mode"]

        @property
        def auth(self):
            return self.socket.exec(self.socket.js.types.path("proxy.credentials"),
                                    user=self.auth_user, timeout=1)["result"][0]

        def set(self, config, patch_webrtc: bool = True, patch_location: bool = True, timeout: int = 10,
                start_time=None, interval: float = 0.1):
            if not start_time:
                start_time = self.socket.time
            self.socket.exec_command("proxy.set", [config, patch_webrtc, patch_location],
                                     timeout=timeout, user=self.any_user, start_time=start_time, interval=interval)

        # noinspection PyDefaultArgument
        def set_single(self, host: str, port: int, scheme: str = "http", bypass_list=["localhost", "127.0.0.1"],
                       patch_webrtc: bool = True,
                       patch_location: bool = True,
                       username: str = None, password: str = None,
                       timeout: int = 10):
            start_time = self.socket.time
            self.check_cmd(scheme, self.supported_schemes)
            # auth
            if username and password:
                if self.auth:
                    self.clear_auth(timeout=timeout)
                self.set_auth(username=username, password=password, timeout=timeout, start_time=start_time)
            elif username or password:
                raise ValueError("For authentication, username and password need to get specified, only got one")

            config = {"mode": "fixed_servers", "rules": {
                "singleProxy": {"host": host, "port": port, "scheme": scheme},
                "bypassList": bypass_list
            }}

            self.set(config=config, patch_webrtc=patch_webrtc, patch_location=patch_location, timeout=timeout,
                     start_time=start_time)

        # noinspection PyDefaultArgument
        def set_auth(self, username: str, password: str, urls=["<all_urls>"], timeout=10, start_time=None,
                     interval: float = 0.1):
            if not start_time:
                start_time = self.socket.time
            self.socket.exec_command("proxy.set_auth", [username, password, urls], timeout=timeout, user=self.auth_user,
                                     start_time=start_time, interval=interval)

        # noinspection PyDefaultArgument
        def clear_auth(self, urls=["<all_urls>"], timeout=10, start_time=None, interval: float = 0.1):
            self.socket.exec_command("proxy.clear_auth", [urls], timeout=timeout, user=self.auth_user,
                                     start_time=start_time,
                                     interval=interval)

        def clear(self, clear_webrtc=True, clear_location=True, timeout=10):
            start_time = self.socket.time
            self.socket.exec_command("proxy.clear", [clear_webrtc, clear_location], timeout=timeout,
                                     start_time=start_time,
                                     user=self.any_user)
            self.clear_auth(timeout=timeout, start_time=start_time)

    class webrtc_leak(base_injector):
        def __init__(self, *args, **kwargs):
            self.supported_values = ["default", "default_public_and_private_interfaces",
                                     "default_public_interface_only", "disable_non_proxied_udp"]
            super().__init__(*args, **kwargs)

        def disable(self, value="disable_non_proxied_udp", timeout=10):
            self.check_cmd(value, self.supported_values)
            self.socket.exec_command("webrtc_leak.disable", [value], timeout=timeout, user=self.any_user)

        def clear(self, timeout=10):
            self.socket.exec_command("webrtc_leak.clear", timeout=timeout, user=self.any_user)

    class contentsettings(base_injector):
        def __init__(self, *args, **kwargs):
            self.supported_location_settings = ["ask", "allow", "block"]
            self.supported_settings = ["automaticDownloads", "autoVerify", "camera", "cookies", "fullscreen", "images",
                                       "javascript", "location", "microphone", "mouselock", "notifications", "plugins",
                                       "popups", "unsandboxedPlugins"]
            super().__init__(*args, **kwargs)

        def set(self, setting, value, urls="<all_urls>", timeout=10):
            self.check_cmd(setting, self.supported_settings)
            self.socket.exec_command("contentsettings.set", [setting, value, urls], timeout=timeout, user=self.any_user)

        def set_location(self, setting="ask", urls="<all_urls>", timeout=10):
            self.check_cmd(setting, self.supported_location_settings)
            self.socket.exec_command("contentsettings.set_location", [setting, urls], timeout=timeout,
                                     user=self.any_user)

    class tabs(base_injector):
        def query(self, query=None, timeout=5):
            if not query:
                query = {}
            return self.socket.exec_async(script={"type": "exec", "func": {"type": "path", "path": "chrome.tabs.query"},
                                                  "args": [{"type": "val", 'val': query}, self.socket.send_back]
                                                  }, user=self.any_user, timeout=timeout)

        @property
        def all_tabs(self):
            return self.query()["result"][0]

        @property
        def active_tab(self):
            try:
                return self.query({"active": True, "lastFocusedWindow": True})["result"][0][0]
            except IndexError:
                return None

    class declarativeNetRequest(base_injector):
        def __init__(self, *args, **kwargs):
            self._headers = {}
            self._block_on = {}
            self._header_rule_id = 1
            self._block_rule_id = 2
            self.all_resource_types = [
                "main_frame", "sub_frame", "stylesheet",
                "script", "image", "font", "object",
                "xmlhttprequest", "ping", "csp_report",
                "media", "websocket", "webtransport",
                "webbundle", "other"]
            super().__init__(*args, **kwargs)

        def update_dynamic_rules(self, add_rules: list = None, remove_ids: list = None):
            rules = {}
            if add_rules:
                rules["addRules"] = add_rules
            if remove_ids:
                rules["removeRuleIds"] = remove_ids
            if rules:
                script = self.t.exec(self.t.path("chrome.declarativeNetRequest.updateDynamicRules"),
                                     args=[self.t.value(rules), self.t.send_back()])
                self.socket.exec_async(script, user=self.any_user)

        def update_headers(self, headers: dict, resource_types=None, url_filter='*'):

            _headers = [self._headers][0]
            _headers.update(headers)

            if resource_types:
                self._check_resource_types(resource_types)
            else:
                resource_types = self.all_resource_types

            request_headers = []
            for key, value in _headers.items():
                if value:
                    request_headers.append({
                        "header": key,
                        "operation": 'set',
                        "value": value})

            rule = {
                "id": self._header_rule_id,
                "priority": 1,
                "action": {
                    "type": 'modifyHeaders',
                    "requestHeaders": request_headers,
                },
                "condition": {
                    "urlFilter": url_filter,
                    "resourceTypes": resource_types,
                },
            }
            self.update_dynamic_rules(add_rules=[rule], remove_ids=[self._header_rule_id])
            self._headers = _headers

        def update_block_on(self, url_filter="*", resource_types=None):
            self._check_resource_types(resource_types)
            if resource_types:
                self._check_resource_types(resource_types)
            else:
                resource_types = self.all_resource_types
            rule = {
                "id": self._block_rule_id,
                "priority": 1,
                "action": {
                    "type": "block",
                },
                "condition": {
                    "urlFilter": url_filter,
                    "resourceTypes": resource_types,
                },
            }
            self.update_dynamic_rules(add_rules=[rule], remove_ids=[self._block_rule_id])
            self._block_on = {"url_filter": url_filter, "resource_types": resource_types}

        def _check_resource_types(self, resource_types):
            for type_ in resource_types:
                self.check_cmd(type_, self.all_resource_types)

        @property
        def dynamic_rules(self):
            script = self.t.exec(func=self.t.path("chrome.declarativeNetRequest.getDynamicRules"),
                                 args=[self.t.value({}), self.t.send_back()])
            dynamic_rules = {}
            result = self.socket.exec_async(script, user=self.any_user, max_depth=5)["result"][0]
            for rule in result:
                dynamic_rules[rule["id"]] = rule
            return dynamic_rules

    class cookies(base_injector):

        def domain2url(self, domain: str):
            return "https://" + domain

        def _get(self, cookie_details: dict):
            script = self.t.exec(
                self.t.path("chrome.cookies.get"), args=[self.t.value(cookie_details), self.t.send_back()])
            return self.socket.exec_async(script, user=self.any_user)["result"]

        def get_cookie(self, name: str, url: str = None):
            cookie_details = {"name": name}
            if url:
                cookie_details["url"] = url
                return self._get(cookie_details)["result"][0]
            else:
                for cookie in self.get_cookies():
                    if cookie["name"] == name:
                        cookie_details["url"] = self.domain2url(cookie["domain"])
                        return self._get(cookie_details)

        def add_cookies(self, cookie_details: dict):
            script = self.t.exec(
                self.t.path("chrome.cookies.set"), args=[self.t.value(cookie_details), self.t.send_back()])
            return self.socket.exec_async(script, user=self.any_user)["result"]

        def get_cookies(self, domain: str = None):
            details = {}
            if domain:
                details["domain"] = domain
            script = self.t.exec(
                self.t.path("chrome.cookies.getAll"), args=[self.t.value(details), self.t.send_back()])
            return self.socket.exec_async(script, user=self.any_user)["result"][0]

        def _remove(self, cookie_details):
            script = self.t.exec(
                self.t.path("chrome.cookies.remove"), args=[self.t.value(cookie_details), self.t.send_back()])
            return self.socket.exec_async(script, user=self.any_user)["result"][0]

        def delete_cookie(self, name: str, url: str = None):
            cookie_details = {"name": name}
            if url:
                cookie_details["url"] = url
                return self._remove(cookie_details)
            else:
                results = []
                for cookie in self.get_cookies():
                    if cookie["name"] == name:
                        cookie_details["url"] = self.domain2url(cookie["domain"])
                        results.append(self._remove(cookie_details))
                return results

        def delete_all_cookies(self, domain: str = None):
            results = []
            for cookie in self.get_cookies(domain=domain):
                url = self.domain2url(cookie["domain"])
                result = self.delete_cookie(cookie["name"], url=url)
                results.append(result)
            return results

    class debugger(base_injector):
        def __init__(self, *args, **kwargs):
            self.required_version = "1.2"
            self.event_id = None
            self.debug_user = None
            self.available_methods = ["Accessibility", "Audits", "CacheStorage",
                                      "Console", "CSS", "Database", "Debugger",
                                      "DOM", "DOMDebugger", "DOMSnapshot", "Emulation",
                                      "Fetch", "IO", "Input", "Inspector", "Log",
                                      "Network", "Overlay", "Page", "Performance",
                                      "Profiler", "Runtime", "Storage", "Target",
                                      "Tracing", "WebAudio", "WebAuthn"]
            super().__init__(*args, **kwargs)

        def _target(self, tab_id: str = None, target_id: str = None, attached=True):
            target = {}
            if target_id:
                target["targetId"] = target_id
                return target
            elif tab_id:
                target["tabId"] = tab_id
                return target
            else:
                active_tab = self.injector.tabs.active_tab
                if active_tab:
                    active_tab_id = active_tab["id"]
                    target["tabId"] = active_tab_id
                    if not attached:
                        return target

                    for i in self.targets:
                        if 'tabId' in i.keys() and i['tabId'] == active_tab_id and i['attached']:
                            return target
                    self.attach(active_tab_id)
            raise LookupError("No attached Target found")

        def attach(self, tab_id: str = None, target_id: str = None, target:dict=None):
            if not target:
                target = self._target(tab_id, target_id, attached=False)
            if not self.debug_user:
                self.debug_user = self.any_user

            script = self.t.exec(self.t.path("chrome.debugger.attach"), args=[
                self.t.value(target), self.t.value(self.required_version),
                self.t.send_back()])
            return self.socket.exec_async(script, user=self.debug_user)["result"]

        def detach(self, tab_id: str = None, target_id: str = None):
            if not self.debug_user:
                raise TypeError("not attached to any targets yet")
            target = self._target(tab_id, target_id)
            script = self.t.exec(self.t.path("chrome.debugger.detach"), args=[
                self.t.value(target),
                self.t.send_back()])
            return self.socket.exec_async(script, user=self.debug_user)["result"]

        def execute(self, method: str, params: dict = None, tab_id: str = None, target_id: str = None):
            if not self.debug_user:
                self.debug_user = self.any_user
            self.check_cmd(method.split(".")[0], self.available_methods)
            if not params:
                params = {}
            target = self._target(tab_id, target_id)
            script = self.t.exec(self.t.path("chrome.debugger.sendCommand"), args=[
                self.t.value(target), self.t.value(method), self.t.value(params),
                self.t.send_back()])
            return self.socket.exec_async(script, user=self.debug_user)["result"][0]

        def on_event(self):
            if not self.debug_user:
                self.debug_user = self.any_user
            if not self.event_id:
                self.event_id = self.socket.make_event_id()

                self.socket.exec(self.t.list([
                    self.t.set_event_id(self.event_id),
                    self.t.exec(
                        self.t.path("chrome.debugger.onEvent.addListener"),
                        args=[self.t.event_callback()]
                    )
                ]), user=self.debug_user)

            event = self.socket.event(self.event_id, user=self.debug_user)
            return event

        @property
        def targets(self):
            if not self.debug_user:
                self.debug_user = self.any_user
            script = self.t.exec(self.t.path("chrome.debugger.getTargets"), args=[self.t.send_back()])
            return self.socket.exec_async(script, user=self.debug_user)["result"][0]
