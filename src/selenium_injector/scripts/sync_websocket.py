import asyncio
import queue

import websockets
import websockets.server


class SynchronousWebsocketServer:
    """
    Synchronous wrapper around asynchronous websockets server by Pier-Yves Lessard, modified by Aurin Aegerter
    https://stackoverflow.com/questions/68939894/implement-a-python-websocket-listener-without-async-asyncio
    """

    def __init__(self):

        self.loop = asyncio.new_event_loop()
        self.ws_server = None
        self.users = {}
        self.host = None
        self.port = None

    # Executed for each websocket
    async def server_routine(self, websocket, path):
        # noinspection PyUnresolvedReferences
        try:
            user = await websocket.recv()
        except websockets.exceptions.ConnectionClosedError:
            return
        self.users[user] = {"ws": websocket, "rx": {}}

        # noinspection PyUnresolvedReferences
        try:
            async for message in websocket:
                response = message[32:]
                resp_id = message[0:32]
                self.users[user]["rx"].update({resp_id: response})
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            try:
                del self.users[user]
            except KeyError:
                pass

    def recv(self, resp_id: str, user: str = None, timeout: int = 10, start_time=None, intervall: float = 0.1):
        import time
        if not start_time:
            start_time = self.time

        while True:
            user = self.wait_user(user, timeout=timeout, start_time=start_time, intervall=intervall)
            self.process()
            try:
                if resp_id in self.users[user]["rx"].keys():
                    response = self.users[user]["rx"][resp_id]
                    del self.users[user]["rx"][resp_id]
                    return response
            except KeyError:
                pass
            time.sleep(intervall)  # user not connected atm
            if (self.time - start_time) >= timeout:
                raise TimeoutError(f"Didn't get a response within {timeout} seconds")

    def send(self, message: str, user: str = None, timeout=10, intervall: float = 0.1, start_time=None):
        if not start_time:
            start_time = self.time

        user = self.wait_user(user, timeout=timeout, intervall=intervall, start_time=start_time)
        self.loop.run_until_complete(self.users[user]["ws"].send(message))

    def post(self, message: str, user: str = None, timeout: int = 10, start_time=None, intervall: float = 0.1):
        import uuid
        if not start_time:
            start_time = self.time

        # protocoll
        # fist 32 chars is request_id, rest is message
        req_id = uuid.uuid4().hex
        parsed = req_id + message

        self.send(message=parsed, user=user, timeout=timeout, start_time=start_time, intervall=intervall)
        response = self.recv(resp_id=req_id, user=user, timeout=timeout, start_time=start_time, intervall=intervall)
        return response

    def wait_user(self, user: str = None, timeout: int = 10, start_time=None, intervall: float = 0.1):
        if not start_time:
            start_time = self.time

        if timeout is False:
            self.get_user(user)
        else:
            import time
            while True:
                try:
                    return self.get_user(user=user)
                except LookupError:
                    pass
                time.sleep(intervall)
                if (self.time - start_time) >= timeout:
                    raise TimeoutError("User not connected")

    def get_user(self, user=None):
        self.process(nloop=5)
        users = list(self.users.keys())
        if user:
            if user in users:
                return user
            else:
                raise LookupError("User not Found")
        else:
            if len(users) > 0:
                return users[0]
            else:
                raise LookupError("No users connected")

    def process(self, nloop: int = 3) -> None:
        for i in range(nloop):  # Process events few times to make sure we handle events generated within the loop
            self.loop.call_soon(self.loop.stop)
            self.loop.run_forever()

    @property
    def time(self):
        import time
        return time.perf_counter()

    def start(self, host: str, port: int) -> None:
        self.port = port
        self.host = host
        # Warning. websockets source code says that loop argument might be deprecated.
        self.ws_server = websockets.serve(self.server_routine, host, port, loop=self.loop)
        self.loop.run_until_complete(self.ws_server)  # Initialize websockets async server

    def stop(self) -> None:
        if self.ws_server is not None:
            self.ws_server.ws_server.close()
            self.loop.run_until_complete(asyncio.ensure_future(self.ws_server.ws_server.wait_closed(), loop=self.loop))
            self.loop.stop()
