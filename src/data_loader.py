# Author: Tao Wen
# Description: 
#   read data from file system or zip files.

from typing_ import DataLoader
from PIL import Image
import os
import zipfile
from typing import List

class FolderDataLoader(DataLoader):
    def __init__(self, folder_path: str):
        self._folder_path = folder_path
        self._file_list = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]
    
    @property
    def file_list(self) -> list[str]:
        return self._file_list
    
    def get_image_by_index(self, index: int) -> Image.Image:
        image_path = os.path.join(self._folder_path, self._file_list[index])
        return Image.open(image_path)

class ZipDataLoader(DataLoader):
    def __init__(self, zip_path: str):
        self._zip_path = zip_path
        self._zip_ref = zipfile.ZipFile(zip_path, 'r')
        self._file_list = [
            f for f in self._zip_ref.namelist()
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]

    @property
    def file_list(self) -> list[str]:
        return self._file_list
    
    def get_image_by_index(self, index: int) -> Image.Image:
        with self._zip_ref.open(self._file_list[index]) as file:
            image = Image.open(file)
            image.load()  # Ensure the image is read from the file
            return image

    def __del__(self):
        """Close the zip file if needed."""
        self._zip_ref.close() if self._zip_ref else None
        pass
