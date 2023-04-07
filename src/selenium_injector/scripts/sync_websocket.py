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
        user = await websocket.recv()
        self.users[user] = {"ws": websocket, "rxqueue": queue.Queue()}

        # noinspection PyUnresolvedReferences
        try:
            async for message in websocket:
                self.users[user]["rxqueue"].put(message)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            del self.users[user]

    def recv(self, user:str=None, timeout:int=60):
        import time
        user = self.def_user(user)
        for i in range(timeout * 10):
            self.process()
            if not self.users[user]["rxqueue"].empty():
                return self.users[user]["rxqueue"].get_nowait()
            time.sleep(0.1)

    def send(self, message:str, user:str=None):
        user = self.def_user(user)
        self.loop.run_until_complete(self.users[user]["ws"].send(message))

    def def_user(self, user: str = None, timeout: int = 60):
        if user is None:
            if timeout is False:
                self.process(nloop=5)
                users = list(self.users.keys())
                if len(users) > 0:
                    return users[0]
                else:
                    raise LookupError("No users connected")
            else:
                import time
                for i in range(timeout * 10):
                    self.process(nloop=5)
                    users = list(self.users.keys())
                    if len(users) > 0:
                        return users[0]
                    time.sleep(0.1)
                raise TimeoutError("No users connected")

        else:
            return user

    def process(self, nloop:int=3) -> None:
        for i in range(nloop):  # Process events few times to make sure we handle events generated within the loop
            self.loop.call_soon(self.loop.stop)
            self.loop.run_forever()

    def start(self, host:int, port:str) -> None:
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