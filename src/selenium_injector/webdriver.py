from selenium.webdriver import ChromeOptions
from selenium_injector.scripts.injector import Injector
from selenium.webdriver import Chrome as BaseDriver
import warnings


class Chrome(BaseDriver):
    # noinspection PyDefaultArgument
    def __init__(self, injector_options={"port": None, "host": None, "temp_dir": None}, base_drivers: tuple = None,
                 **kwargs):

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

        if not injector_options or injector_options is True:
            injector_options = {}

        self.injector = Injector(**injector_options)

        if "options" not in kwargs.keys():
            kwargs["options"] = ChromeOptions()
        kwargs["options"].add_argument(f'--load-extension={self.injector.path}')

        super().__init__(**kwargs)

        # connection to tab-0
        tab_index = self.window_handles.index(self.current_window_handle).__str__()
        self.injector.tab_user = "tab-" + tab_index
        config = f"""
                var connection = new connector("{self.injector.socket.host}", {self.injector.socket.port}, "{self.injector.tab_user}")
                connection.connect();
                """

        from selenium_injector.utils.utils import read
        utils_js = read("files/js/utils.js")
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                             {"source": "(function(){%s})()" % (utils_js + self.injector.connection_js + config)})

    def quit(self) -> None:
        self.injector.stop()
        super().quit()
