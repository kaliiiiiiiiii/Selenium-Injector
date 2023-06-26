class base_driver:
    def __init__(self, socket, user: str):
        self.socket = socket
        self.user = user

    def check_cmd(self, value, values):
        if value not in values:
            raise ValueError("Expected " + str(values) + " , but got" + str(value))


class Injector:
    def __init__(self, port: int = None, host: str = None, user="selenium-injector-mv3", temp_dir: str = None):
        from selenium_injector.scripts.socket import socket
        from selenium_injector.utils.utils import read, write, sel_injector_path, random_port

        if not host:
            host = "localhost"
        if not port:
            port = random_port(host=host)

        self.user = user

        config = f"""
        var connection = new connector("{host}", {port}, "{self.user}")
        connection.connect();
        """
        if temp_dir:
            self.path = temp_dir + "/injector_extension"
        else:
            self.path = sel_injector_path() + "files/tmp/injector_extension"

        background_js = read("files/extension/background.js")
        manifest_json = read("files/extension/manifest.json")
        self.connection_js = read("files/js/connection.js")
        write(self.path + "/background.js", background_js + self.connection_js + config, sel_root=False)
        write(self.path + "/manifest.json", manifest_json, sel_root=False)

        self.socket = socket()
        self.socket.start(port=port, host=host)
        self.stop = self.socket.stop
        self.exec = self.socket.exec
        self.exec_command = self.socket.exec_command

        # subclasses
        self.proxy = self.proxy(socket=self.socket, user=self.user)
        self.webrtc_leak = self.webrtc_leak(socket=self.socket, user=self.user)
        self.contentsettings = self.contentsettings(socket=self.socket, user=self.user)
        self.tabs = self.tabs(socket=self.socket, user=self.user)

    @property
    def page_source(self):
        return \
            self.socket.exec(self.socket.js.types.path("document.documentElement.outerHTML"), user="tab-0")["result"][0]

    class proxy(base_driver):
        def __init__(self, socket, user):
            self.supported_schemes = ["http", "https", "socks4", "socks5"]
            super().__init__(socket, user=user)

        @property
        def rules(self):
            try:
                return self.socket.exec_command("proxy.get", user=self.user)["result"][0]["value"]["rules"]
            except KeyError:
                return None

        @property
        def mode(self):
            return self.socket.exec_command("proxy.get", user=self.user)["result"][0]["value"]["mode"]

        @property
        def auth(self):
            return self.socket.exec(self.socket.js.types.path("proxy.credentials"))["result"][0]

        def set(self, config, patch_webrtc: bool = True, patch_location: bool = True):
            self.socket.exec_command("proxy.set", [config, patch_webrtc, patch_location],
                                     timeout=10, user=self.user)

        # noinspection PyDefaultArgument
        def set_single(self, host: str, port: int, scheme: str = "http", bypass_list=["localhost", "127.0.0.1"], patch_webrtc: bool = True,
                       patch_location: bool = True,
                       username: str = None, password: str = None,
                       timeout=10):

            self.check_cmd(scheme, self.supported_schemes)
            # auth
            if username and password:
                timeout = int(timeout / 2)
                self.set_auth(username=username, password=password, timeout=timeout)
            elif username or password:
                raise ValueError("For authentification, username and password need to get specified, only got one")

            config = {"mode": "fixed_servers", "rules": {
                "singleProxy": {"host": host, "port": port, "scheme": scheme},
                "bypassList": bypass_list
            }}

            self.set(config=config, patch_webrtc=patch_webrtc, patch_location=patch_location)

        # noinspection PyDefaultArgument
        def set_auth(self, username: str, password: str, urls=["<all_urls>"], timeout=10):
            self.socket.exec_command("proxy.set_auth", [username, password, urls], timeout=timeout, user=self.user)

        # noinspection PyDefaultArgument
        def clear_auth(self,urls=["<all_urls>"], timeout=10):
            self.socket.exec_command("proxy.clear_auth", [urls], timeout=timeout, user=self.user)

        def clear(self, clear_webrtc=True, clear_location=True, timeout=10):
            self.socket.exec_command("proxy.clear", [clear_webrtc, clear_location], timeout=int(timeout/2), user=self.user)
            self.clear_auth(timeout=int(timeout/2))

    class webrtc_leak(base_driver):
        def __init__(self, socket, user):
            self.supported_values = ["default", "default_public_and_private_interfaces",
                                     "default_public_interface_only", "disable_non_proxied_udp"]
            super().__init__(socket, user)

        def disable(self, value="disable_non_proxied_udp", timeout=10):
            self.check_cmd(value, self.supported_values)
            self.socket.exec_command("webrtc_leak.disable", [value], timeout=timeout, user=self.user)

        def clear(self, timeout=10):
            self.socket.exec_command("webrtc_leak.clear", timeout=timeout, user=self.user)

    class contentsettings(base_driver):
        def __init__(self, socket, user):
            self.supported_location_settings = ["ask", "allow", "block"]
            self.supported_settings = ["automaticDownloads", "autoVerify", "camera", "cookies", "fullscreen", "images",
                                       "javascript", "location", "microphone", "mouselock", "notifications", "plugins",
                                       "popups", "unsandboxedPlugins"]
            super().__init__(socket, user)

        def set(self, setting, value, urls="<all_urls>", timeout=10):
            self.check_cmd(setting, self.supported_settings)
            self.socket.exec_command("contentsettings.set", [setting, value, urls], timeout=timeout, user=self.user)

        def set_location(self, setting="ask", urls="<all_urls>", timeout=10):
            self.check_cmd(setting, self.supported_location_settings)
            self.socket.exec_command("contentsettings.set_location", [setting, urls], timeout=timeout, user=self.user)

    class tabs(base_driver):
        def query(self, query=None):
            if not query:
                query = {}
            return self.socket.exec_async(script={"type": "exec", "func": {"type": "path", "path": "chrome.tabs.query"},
                                                  "args": [{"type": "val", 'val': query}, self.socket.send_back]
                                                  }, user=self.user)

        @property
        def all_tabs(self):
            return self.query()["result"][0]

        @property
        def active_tab(self):
            try:
                return self.query({"active": True, "lastFocusedWindow": True})["result"][0][0]
            except IndexError:
                return None
