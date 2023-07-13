class JS:
    def __init__(self):
        self.types = self.types()
        self.find_elements = self.find_elements(self.types)

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

        def condition(self, condition: dict, do: dict, elsewise: dict = None):
            return {"type": "if", "if": condition, "do": do, "else": elsewise}

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

        def event_callback(self):
            return self.path("event_callback", obj=self.this())

        def set_event_id(self, event_id):
            return self.exec(self.path("set_event_id", obj=self.this()),
                             args=[self.value(event_id)]
                             )

    class find_elements:
        def __init__(self, types):
            self.t = types

        def _by_xpath_result_length(self, value, base_element):
            script = self._by_xpath(value, base_element)
            return self.t.path("snapshotLength", obj=script)

        def _by_xpath(self, value, base_element):
            script = self.t.exec(self.t.path("document.evaluate"), args=[
                                     self.t.value(value),
                                     base_element, self.t.value(None),
                                     self.t.value(7),  # "XPathResult.ORDERED_NODE_SNAPSHOT_TYPE"
                                     self.t.value(None)
                                 ])
            return script

        def by_xpath(self, value: str, base_element, idx: int):
            script = self._by_xpath(value, base_element)
            return self.t.exec(self.t.path("snapshotItem", obj=script), args=[self.t.value(idx)])

        def by_tag_name(self, value, base_element):
            return self.t.exec(self.t.path("getElementsByTagName", obj=base_element), args=[
                self.t.value(value)
            ])

        def by_css_selector(self, value, base_element):
            script = self.t.exec(self.t.path("querySelector", obj=base_element), args=[
                self.t.value(value)
            ])
            return self.t.list([script])
