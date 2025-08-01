# Author: Tao Wen
# Description: 
#   define interfaces for this project

from abc import ABC, abstractmethod
from PIL import Image

class DataLoader(ABC):
    @property
    @abstractmethod
    def file_list(self) -> list[str]:
        """Return list of image file names"""
        pass
    
    @abstractmethod
    def get_image_by_index(self, index: int) -> Image.Image:
        """Get image by index"""
        pass
    
    def __len__(self):
        return len(self.file_list)
