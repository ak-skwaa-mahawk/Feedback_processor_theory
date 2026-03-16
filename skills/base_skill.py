from abc import ABC, abstractmethod

class BaseSkill(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass