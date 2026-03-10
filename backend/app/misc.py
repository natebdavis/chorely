from abc import ABC, abstractmethod

class CreateFromDict(ABC): 
    '''Interface used for data classes that can be created using a dictionary.'''
    
    @abstractmethod
    def from_dict(self):
        pass
