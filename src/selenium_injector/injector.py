class injector:
    def __init__(self, port: int = 8001, host: str = "localhost", username: str = "selenium_injector"):
        from selenium_injector.scripts.socket import socket
        from selenium_injector.utils.utils import read, write, sel_injector_path
        background_js = read("files/injector_extension/background.js")
        config = """
        connection.username = "%s";
        connection.host = "%s";
        connection.port = %s;
        connection.connect();
        """ % (username, host, str(port))
        self.path = sel_injector_path()+"files/tmp/injector_extension"
        write(self.path+"/background.js", background_js+config, sel_root=False)
        self.socket = socket()
        self.socket.start(port=port, host=host)
        self.stop = self.socket.stop
        self.exec = self.socket.exec
        self.exec_command = self.socket.exec_command
