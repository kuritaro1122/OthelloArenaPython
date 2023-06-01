import socket

class ClientBase:
    def __init__(self, timeout:int=10, buffer:int=1024):
        self.__socket = None
        self.__address = None
        self.__timeout = timeout
        self.__buffer = buffer
    
    def __del__(self):
        self.disconnect()
    
    def connect(self, address, family:int, typ:int, proto:int):
        self.__address = address
        self.__socket = socket.socket(family, typ, proto)
        self.__socket.settimeout(self.__timeout)
        self.__socket.connect(self.__address)

    def send(self, message:str="") -> None:
        flag = False
        while True:
            if message == "":
                message_send = input("> ")
            else:
                message_send=message
                flag = True
            self.__socket.send(message_send.encode('utf-8'))
            message_recv = self.__socket.recv(self.__buffer).decode('utf-8')
            self.received(message_recv)
            if flag:
                break
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except:
            pass

    def send2(self, message:str=''):
        self.__socket.send(message.encode('utf-8'))
        message_recv = self.__socket.recv(self.__buffer).decode('utf-8')
        self.received(message_recv)

    def disconnect(self):
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except:
            pass

    def received(self, message:str):
        print(message)