# Author: Tao Wen
# Description: 
#   data_item is a dataclass created by data_loader
from typing import Any
from typing_ import DataItemProtocol
from dataclasses import dataclass, asdict
from PIL import Image


@dataclass
class ImageItem:
    """Represents a simple image data item."""
    name: str
    image: Image.Image
    source: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def __contains__(self, field_name: str) -> bool:
        return field_name in self.as_dict()


@dataclass
class Box:
    """Represents a bounding box with class ID and coordinates."""
    class_id: int
    x: float
    y: float
    w: float
    h: float


@dataclass
class AnnotatedImageItem:
    name: str
    image: Image.Image
    annotation: str
    source: str

    def boxes(self) -> list[Box]:
        result = []
        if self.annotation:
            for line in self.annotation.split("\n"):
                parts = line.split()
                if len(parts) >= 4:
                    class_id = int(parts[0])
                    # center coordinates and width/height
                    x0, y0, w, h = map(float, parts[1:])
                    # convert center coordinates to top-left coordinates
                    x1 = x0 - w / 2
                    y1 = y0 - h / 2
                    result.append(Box(class_id, x1, y1, w, h))
        return result

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    def __contains__(self, field_name: str) -> bool:
        return field_name in self.as_dict()