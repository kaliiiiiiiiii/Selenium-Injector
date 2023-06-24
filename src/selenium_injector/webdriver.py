from selenium.webdriver import ChromeOptions
from selenium_injector.scripts.driverless import Driverless


class Base:
    pass


class Chrome(Base):
    # noinspection PyDefaultArgument
    def __init__(self, driverless_options={"port": None, "host": None}, base_driver=None, **kwargs):

        if not base_driver:
            from selenium.webdriver import Chrome as base_driver

        Chrome.__bases__ = (Chrome.__base__, base_driver,)

        port = driverless_options["port"]
        host = driverless_options["host"]
        self.driverless = Driverless(port=port, host=host)

        from selenium_injector.utils.utils import read
        utils_js = read("files/js/utils.js")

        if "options" not in kwargs.keys():
            kwargs["options"] = ChromeOptions()
        kwargs["options"].add_argument(f'--load-extension={self.driverless.path}')

        super().__init__(**kwargs)

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
