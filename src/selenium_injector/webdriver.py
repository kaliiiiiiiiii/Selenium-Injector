from selenium.webdriver import ChromeOptions
from selenium_injector.scripts.driverless import Driverless
from selenium.webdriver import Chrome as BaseDriver
import warnings


class Chrome(BaseDriver):
    # noinspection PyDefaultArgument
    def __init__(self, driverless_options={"port": None, "host": None}, base_drivers: tuple = None, **kwargs):

        if not base_drivers:
            base_drivers = tuple()

        if len(base_drivers) > 1:
            warnings.warn(
                "More than one base_driver might not initialize correctly, seems buggy.\n Also, you might try different order")
        if (len(base_drivers) == 1) and (base_drivers[0] == Chrome.__base__):
            pass  # got selenium.webdriver.Chrome as BaseDriver
        elif not base_drivers:
            pass
        else:
            Chrome.__bases__ = base_drivers

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
