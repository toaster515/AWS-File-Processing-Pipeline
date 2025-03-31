from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def upload_file(self, file_obj, object_key):
        pass
