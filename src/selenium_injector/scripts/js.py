class JS:
    def __init__(self):
        self.types = self.types()
        self.utils = self.utils(self.types)

    class types:
        def __init__(self):
            self.not_return = {"not_return": True}

        def path(self, path: str, obj: dict = None):
            return {"type": "path", "path": path, "obj": obj}

        def exec(self, func: dict, args: list = None):
            if not args:
                args = []
            return {"type": "exec", "func": func, "args": args}

        def value(self, value):
            return {"type": "val", "val": value}

        def condition(self, condition: dict, do: dict, elsewhise: dict = None):
            return {"type": "if", "if": condition, "do": do, "else": elsewhise}

        # noinspection PyShadowingBuiltins
        def list(self, list: list = None):
            return {"type": "list", "list": list}

        def dict(self, dict_list: list = None):
            return {"type": "dict", "dict_list": dict_list}

        def operator(self, a: dict, b: dict, operator: str):
            return {"type": "op", "a": a, "b": b, "op": operator}

        def negation(self, obj: dict):
            return {"type": "!", "obj": obj}

        def this(self):
            return {"type": "this"}

        def send_back(self):
            return self.path("send_back", obj=self.this())

    class utils:
        def __init__(self, types):
            self.types = types

        def find_element_by_xpath(self, xpath: str):
            return self.types.exec(self.types.path("utils.find_element.ByXpath"),
                                   args=[self.types.value(xpath)])

        def click_element(self, element: dict):
            return self.types.exec(self.types.path("click", element))
