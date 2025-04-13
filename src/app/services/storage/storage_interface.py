from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def upload_file(self, file_obj, object_key):
        pass

    @abstractmethod
    def download_file(self, object_key):
        pass
