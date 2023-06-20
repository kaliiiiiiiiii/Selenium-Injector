import selenium.webdriver.chromium.webdriver
from selenium.webdriver import ChromeOptions
from selenium_injector.scripts.driverless import Driverless


# noinspection PyDefaultArgument
def Chrome(driverless_options: dict = {"port": None, "host": None}, base_driver=None, *args, **kwargs):
    if not base_driver:
        from selenium.webdriver import Chrome as base_driver

    class _Chrome(base_driver):
        # noinspection PyDefaultArgument
        def __init__(self, _driverless_options={"port": None, "host": None}, *_args, **_kwargs):
            port = _driverless_options["port"]
            host = _driverless_options["host"]
            self.driverless = Driverless(port=port, host=host)

            from selenium_injector.utils.utils import read
            utils_js = read("files/js/utils.js")

            if "options" not in _kwargs.keys():
                _kwargs["options"] = ChromeOptions()
            _kwargs["options"].add_argument(f'--load-extension={self.driverless.path}')

            super().__init__(*_args, **_kwargs)

            tab_index = self.window_handles.index(self.current_window_handle).__str__()
            self.driverless.tab_user = "tab-" + tab_index
            config = f"""
                    var connection = new connector("{self.driverless.socket.host}", {self.driverless.socket.port}, "{self.driverless.tab_user}")
                    connection.connect();
                    """
            self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                                 {"source": "(function(){%s})()" % (utils_js + self.driverless.connection_js + config)})

        def quit(self) -> None:
            self.driverless.stop()
            super().quit()

    return _Chrome(_driverless_options=driverless_options, *args, **kwargs)
