# Author: Tao Wen
# Description: 
#   define interfaces for this project
from typing import Protocol, Any
from PIL import Image

class DataItemProtocol(Protocol):
    """Represents a data item that can be loaded from a source"""
    @property
    def source(self) -> str: ...    
    @property
    def name(self) -> str: ...

    def __contains__(self, field_name: str) -> bool: ...
    def as_dict(self) -> dict[str, Any]: ...


class DataVisualizerProtocol(Protocol):
    """Interface for visualizing data items"""
    def to_drawn_image(self, item: DataItemProtocol) -> Image.Image:
        """Convert data item to image"""
        ...


class DataLoaderProtocol(Protocol):
    """Interface for loading data items"""
    @property
    def data_item_name_list(self) -> list[str]:
        """Return list of item names"""
        ...
    
    def get_item_by_index(self, index: int) -> DataItemProtocol:
        """Get data item by index"""
        ...
    
    def __len__(self) -> int:
        """Number of items available"""
        ...
