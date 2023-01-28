import pyxel
import numpy as np
from abc import ABC, abstractmethod

class BaseButton(ABC):
    @abstractmethod
    def input(self, mouse_x:int, mouse_y:int):
        pass
    @abstractmethod
    def execute(self):
        pass
    @abstractmethod
    def draw(self):
        pass

class TextButton(BaseButton):
    def __init__(self,x:int,y:int,s:str,col:int,func:lambda:function,width:int=-1,height:int=-1,backCol:int = -1):
        self.x = x
        self.y = y
        self.s = s
        self.col = col
        self.func = func
        self.width = width if width >= 0 else len(self.s) * 4
        self.height = height if height >= 0 else 6
        self.backCol = backCol
    def input(self, mouse_x:int, mouse_y:int):
        if (self.x <= mouse_x < self.x+self.width) and (self.y <= mouse_y < self.y+self.height):
            self.execute()
    def execute(self):
        self.func()
    def draw(self):
        if self.backCol > -1:
            pyxel.rect(x=self.x,y=self.y,w=self.width,h=self.height,col=self.backCol)
        pyxel.text(x=self.x,y=self.y,s=self.s,col=self.col)

class TextButtonPro(TextButton):
    def __init__(self,x:int,y:int,s:lambda:str,col:lambda:int,func:lambda:function,width:int=-1,height:int=-1,backCol:lambda:int=lambda:-1):
        super(TextButtonPro, self).__init__(x=x,y=y,s=s(),col=0,func=func,width=width,height=height,backCol=0)
        self.col:lambda:int = col
        self.s:lambda:str = s
        self.backCol:lambda:int = backCol
    def draw(self):
        if self.backCol() > -1:
            pyxel.rect(x=self.x,y=self.y,w=self.width,h=self.height,col=self.backCol())
        pyxel.text(x=self.x,y=self.y,s=self.s(),col=self.col())

class ButtonManager:
    def __init__(self, buttons:np.array([[BaseButton,lambda:bool,np.array(int)]]), click=pyxel.MOUSE_BUTTON_LEFT):
        self.buttons:np.array([[BaseButton,lambda:bool,np.array(int)]]) = buttons
        self.click = click
    def append(self, button:BaseButton, active:lambda:bool, keys:np.array(int)):
        self.buttons:np.array([[BaseButton,lambda:bool,np.array(int)]]) = np.append([self.buttons, [button,active,keys]])
    def update(self):
        for b in self.buttons:
            if b[1]() == False:
                continue
            tb:BaseButton = b[0]
            if pyxel.btnr(self.click):
                tb.input(pyxel.mouse_x,pyxel.mouse_y)
                continue
            for k in b[2]:
                if pyxel.btnr(k):
                    tb.execute()
                    continue
    def draw(self):
        for b in self.buttons:
            if b[1]() == False:
                continue
            tb:BaseButton = b[0]
            tb.draw()
