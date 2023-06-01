import sys
import os
import socket
import copy
import importlib

Afm = None
def __executeOnPath(absPath:str, func:lambda:None):
    current = copy.deepcopy(sys.path)
    sys.path.append(absPath)
    func()
    sys.path = current
def __importModules():
	global Afm
	Afm = importlib.import_module('AsyncFunction').AsyncFunctionManager
__executeOnPath(os.path.dirname(__file__), __importModules)
afm = Afm()

class BlockingServerBase:
    def __init__(self, timeout:int=60, buffer:int=1024):
        self.__socket = None
        self.__timeout = timeout
        self.__buffer = buffer
        self.close()

    def __del__(self):
        self.close()

    def close(self) -> None:
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except:
            pass

    def accept(self, address, family:int, typ:int, proto:int) -> None:
        self.__socket = socket.socket(family, typ, proto)
        self.__socket.settimeout(self.__timeout)
        self.__socket.bind(address)
        self.__socket.listen(1)
        print("Server started :", address)
        conn, _ = self.__socket.accept()

        while True:
            try:
                message_recv = conn.recv(self.__buffer).decode('utf-8')
                message_resp = self.respond(message_recv)
                conn.send(message_resp.encode('utf-8'))
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break
        self.close()

    def respond(self, message:str) -> str:
        return ""

class MultipleServerBase:
    def __init__(self, timeout:int=60, buffer:int=1024):
        self.__socket = None
        self.__timeout = timeout
        self.__buffer = buffer
        self.close()

    def __del__(self):
        self.close()

    def close(self) -> None:
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except:
            pass

    def accept(self, address, family:int, typ:int, proto:int) -> None:
        self.__socket = socket.socket(family, typ, proto)
        self.__socket.settimeout(self.__timeout)
        self.__socket.bind(address)
        self.__socket.listen()
        print("Server started :", address)

        def recv_client(sock, addr):
            while True:
                try:
                    message_recv = sock.recv(self.__buffer).decode('utf-8')
                    message_resp = self.respond(message_recv)
                    sock.send(message_resp.encode('utf-8'))
                except ConnectionResetError:
                    break
                except BrokenPipeError:
                    break
        
        while True:
            sock_cl, addr = self.__socket.accept()
            afm.createAsyncFunc(lambda:recv_client(sock_cl,addr))
        self.close()

    def respond(self, message:str) -> str:
        return ""