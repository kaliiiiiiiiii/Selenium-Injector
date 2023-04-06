from selenium_injector.scripts.sync_websocket import SynchronousWebsocketServer


class socket(SynchronousWebsocketServer):
    def post(self, message, timeout=60, user=None):
        user = self.def_user(user)
        self.send(message=message, user=user)
        return self.recv(user=user, timeout=timeout)

    def exec(self, script, user=None, timeout=60):
        user = self.def_user(user=user)
        import json
        return json.loads(self.post(json.dumps(script), user=user, timeout=timeout))

    def exec_command(self, function, args: list or str or int or float or bool or None = None, timeout=60, user=None):
        user = self.def_user(user)
        parsed_args = []
        arg_type = type(args)
        if arg_type == list:
            for arg in args:
                parsed_args.append({"type": "val", "val": arg})
        else:
            parsed_args.append({"type": "val", "val": args})
        return self.exec({"type": "exec", "func": {"type": "path", "path": function}, "args": parsed_args},
                         user=user, timeout=timeout)
