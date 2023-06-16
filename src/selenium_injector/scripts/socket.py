from selenium_injector.scripts.sync_websocket import SynchronousWebsocketServer


class socket(SynchronousWebsocketServer):
    def __init__(self):
        self.send_back = {"type": "path", "path": "connection.send_back"}
        self.not_return = {"not_return":True}
        super().__init__()

    def post(self, message: str, timeout: int = 10, user: str = None):
        user = self.wait_user(user)
        self.send(message=message, user=user)
        return self.recv(user=user, timeout=timeout)

    def exec(self, script: dict, user: str = None, timeout: int = 10):
        user = self.wait_user(user=user)
        import json
        result = self.post(json.dumps(script), user=user, timeout=timeout)
        result = json.loads(result)
        if result["status"] == "error":
            raise Exception(result["result"]["stack"])
        return result

    def exec_async(self, script: dict, user: str = None, timeout: int = 10):
        script["not_return"] = True
        return self.exec(script=script, user=user, timeout=timeout)

    def exec_command(self, function: str, args: list or str or int or float or bool or None = None, timeout: int = 10,
                     user: str = None):
        user = self.wait_user(user)
        parsed_args = []
        arg_type = type(args)
        if arg_type == list:
            for arg in args:
                parsed_args.append({"type": "val", "val": arg})
        else:
            parsed_args.append({"type": "val", "val": args})
        return self.exec({"type": "exec", "func": {"type": "path", "path": function}, "args": parsed_args},
                         user=user, timeout=timeout)
