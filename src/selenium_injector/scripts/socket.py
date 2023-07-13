from selenium_injector.scripts.sync_websocket import SynchronousWebsocketServer
from selenium_injector.types.js import JS


class JSEvalException(Exception):
    def __init__(self, message: str, stack: str = None):
        super().__init__(stack)
        self.message = message
        self.stack = stack


class socket(SynchronousWebsocketServer):
    def __init__(self):
        self.js = JS()
        self.send_back = self.js.types.send_back()
        self.not_return = {"not_return": True}
        super().__init__()

    def exec(self, script: dict, user: str = None, max_depth=2, timeout: int = 10, start_time=None,
             interval: float = 0.1):
        if not start_time:
            start_time = self.time

        script["max_depth"] = max_depth

        import json
        result = self.post(json.dumps(script), user=user, timeout=timeout, start_time=start_time, interval=interval)
        result = json.loads(result)
        if result["status"] == "error":
            message = result["result"][0]["message"]
            stack = result["result"][0]["stack"]
            raise JSEvalException(message, stack)
        return result

    def exec_async(self, script: dict, user: str = None, max_depth=2, timeout: int = 10, start_time=None,
                   interval: float = 0.1):
        if not start_time:
            start_time = self.time

        script["not_return"] = True
        return self.exec(script=script, user=user, max_depth=max_depth, timeout=timeout, start_time=start_time,
                         interval=interval)

    def exec_command(self, function: str, args: list or str or int or float or bool or None = None, user: str = None,
                     max_depth=2, timeout: int = 10, start_time=None, interval: float = 0.1):
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
                         user=user, max_depth=max_depth, timeout=timeout, start_time=start_time, interval=interval)
