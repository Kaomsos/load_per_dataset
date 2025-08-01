# Author: Tao Wen
# Description: 
#   read data from file system or zip files.

from PIL import Image
from typing_ import DataLoaderProtocol
from data_item import ImageItem, AnnotatedImageItem
import os
import zipfile


class FolderLoader(DataLoaderProtocol):
    def __init__(self, folder_path: str):
        self._folder_path = folder_path
        self._file_name_list = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]
    
    @property
    def data_item_name_list(self) -> list[str]:
        return self._file_name_list
    
    def get_item_by_index(self, index: int) -> ImageItem:
        name = self._file_name_list[index]
        source = os.path.join(self._folder_path, name)
        return ImageItem(
            name=name,
            source=source,
            image=Image.open(source),
        )

    def __len__(self):
        return len(self._file_name_list)


def in_zipfile(path: str, zipfile: zipfile.ZipFile) -> bool:
    try:
        zipfile.getinfo(path)
        return True
    except KeyError:
        return False
    

def to_annotation_path(image_path: str, annotation_ext: str = "txt") -> str:
    """Get the annotation path for an image."""
    base = image_path.rsplit('.', 1)[0] 
    return f"{base}.{annotation_ext}"


class ZipLoader(DataLoaderProtocol):
    def __init__(self, zip_path: str):
        self._zip_path = zip_path
        self._zip_ref = zipfile.ZipFile(zip_path, 'r')
        
        self._file_name_list = list(filter(
                lambda name: name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')), 
                self._zip_ref.namelist()
            ))
        self._file_name_list.sort()

    @property
    def data_item_name_list(self) -> list[str]:
        return self._file_name_list
    
    def get_item_by_index(self, index: int) -> AnnotatedImageItem:
        name = self._file_name_list[index]
        source = os.path.join(self._zip_path, name)
        image = self._zip_ref.open(name)

        if in_zipfile(to_annotation_path(name), self._zip_ref):
            annotation = self._zip_ref.read(to_annotation_path(name)).decode('utf-8')
        else:
            annotation = None

        return AnnotatedImageItem(
            name=name,
            source=source,
            image=Image.open(image),
            annotation=annotation
        )
    
    def __len__(self):
        return len(self._file_name_list)

    def __del__(self):
        """Ensure the zip file is closed when the loader is deleted."""
        self._zip_ref.close()
