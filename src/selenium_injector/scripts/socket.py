from selenium_injector.scripts.sync_websocket import SynchronousWebsocketServer


class socket(SynchronousWebsocketServer):
    def post(self, message: str, timeout: int = 10, user: str = None):
        user = self.wait_user(user)
        self.send(message=message, user=user)
        return self.recv(user=user, timeout=timeout)

    def exec(self, script: dict, user: str = None, timeout: int = 10):
        user = self.wait_user(user=user)
        import json
        result = json.loads(self.post(json.dumps(script), user=user, timeout=timeout))
        if result["status"] == "error":
            raise Exception(result["result"]["stack"])
        return result

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
