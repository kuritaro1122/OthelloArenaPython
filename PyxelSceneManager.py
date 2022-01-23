from abc import ABC, abstractclassmethod
import numpy as np

class BaseSceneManager:
    def __init__(self, scenes:np.array, beginIndex:int=0) -> None: #scenes -> np.array(BaseScene)
        self.scenes = scenes
        for s in self.scenes:
            scene:BaseScene = s
            scene.setSceneManager(self)
        self.loadScene(index=beginIndex)
    def update(self) -> None:
        self.scene().update()
    def draw(self) -> None:
        self.scene().draw()
    def scene(self) -> None:
        return self.scenes[self.sceneIndex]
    def loadScene(self, index:int) -> None:
        self.sceneIndex = index
        self.scene().start()

class BaseScene(ABC):
    @abstractclassmethod
    def start(self) -> None:
        pass
    @abstractclassmethod
    def update(self) -> None:
        pass
    @abstractclassmethod
    def draw(self) -> None:
        pass
    def setSceneManager(self, sceneManager:BaseSceneManager) -> None:
        self.sceneManager = sceneManager
    def loadScene(self, index:int) -> None:
        self.sceneManager.loadScene(index)