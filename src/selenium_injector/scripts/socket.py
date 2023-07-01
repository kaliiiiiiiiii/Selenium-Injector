from selenium_injector.scripts.sync_websocket import SynchronousWebsocketServer
from selenium_injector.scripts.js import JS


class socket(SynchronousWebsocketServer):
    def __init__(self):
        self.js = JS()
        self.send_back = self.js.types.send_back()
        self.not_return = {"not_return": True}
        super().__init__()

    def exec(self, script: dict, user: str = None, timeout: int = 10, start_time=None, intervall: float = 0.1):
        if not start_time:
            start_time = self.time

        import json
        result = self.post(json.dumps(script), user=user, timeout=timeout, start_time=start_time, intervall=intervall)
        result = json.loads(result)
        if result["status"] == "error":
            raise Exception(result["result"][0]["stack"])
        return result

    def exec_async(self, script: dict, user: str = None, timeout: int = 10, start_time=None, intervall: float = 0.1):
        if not start_time:
            start_time = self.time

        script["not_return"] = True
        return self.exec(script=script, user=user, timeout=timeout, start_time=start_time, intervall=intervall)

    def exec_command(self, function: str, args: list or str or int or float or bool or None = None, user: str = None
                     , timeout: int = 10, start_time=None, intervall: float = 0.1):
        if not start_time:
            start_time = self.time

        parsed_args = []
        arg_type = type(args)
        if arg_type == list:
            for arg in args:
                parsed_args.append({"type": "val", "val": arg})
        else:
            parsed_args.append({"type": "val", "val": args})
        return self.exec({"type": "exec", "func": {"type": "path", "path": function}, "args": parsed_args},
                         user=user, timeout=timeout, start_time=start_time, intervall=intervall)
