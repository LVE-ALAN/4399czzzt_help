from abc import ABC, abstractmethod

class BaseTask(ABC):
    def __init__(self, name, engine):
        self.name = name
        self.engine = engine  # dict with vision, clicker, state
        self.is_running = False

    @abstractmethod
    def execute(self):
        pass

    def stop(self):
        self.is_running = False