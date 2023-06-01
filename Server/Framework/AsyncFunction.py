import threading

class AsyncFunctionManager:
    def __init__(self):
        self.running = False
        pass
    def createAsyncFunc(self, func, join:bool=False) -> lambda:bool:
        self.running = True
        self.func = func
        thread1 = threading.Thread(target=self.__func)
        thread1.start()
        if join == True:
            thread1.join()
        return lambda:self.running
    def __func(self):
        self.func()
        self.running = False
