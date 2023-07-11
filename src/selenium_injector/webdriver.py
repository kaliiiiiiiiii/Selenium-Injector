from selenium.webdriver import ChromeOptions
from selenium_injector.scripts.injector import Injector, make_config
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

        self.injector = Injector(debug=True, **injector_options)

        if "options" not in kwargs.keys():
            kwargs["options"] = ChromeOptions()

        kwargs["options"].add_argument(f'--load-extension={",".join(self.injector.paths)}')

        super().__init__(**kwargs)

    def quit(self) -> None:
        self.injector.stop()
        super().quit()
