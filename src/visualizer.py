# Author: Tao Wen
# Description: 
#   visualize dataitem converting them to image_object
from PIL import Image, ImageDraw, ImageFont
from typing_ import DataVisualizerProtocol
from data_item import AnnotatedImageItem

DPI = 96  # Standard DPI for most displays
PPI = 72  # Points per inch, used in font metrics


def get_line_height(font_size: float) -> float:
    return font_size * DPI / PPI


class AnnotatedImageVisualizer(DataVisualizerProtocol):
    COLORS = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", 
            "#FF00FF", "#00FFFF", "#FFA500", "#800080"
    ]
    LINE_WIDTH = 4
    FONT_SIZE = 24

    def to_drawn_image(self, item: AnnotatedImageItem) -> Image.Image:
        # Create a copy of the image to draw on
        image = item.image.copy()

        if not hasattr(item, 'boxes'):
            return image

        draw = ImageDraw.Draw(image)
        # Get original dimensions
        orig_width, orig_height = image.size
        # Draw boxes before resizing
        for box in item.boxes():
            # Convert normalized coordinates to pixel coordinates
            x1 = box.x * orig_width
            y1 = box.y * orig_height
            w = box.w * orig_width
            h = box.h * orig_height
            
            # Get color for class
            color = self.COLORS[box.class_id % len(self.COLORS)]
            
            # Draw rectangle
            draw.rectangle(
                [(x1, y1), (x1 + w, y1 + h)],
                outline=color,
                width=self.LINE_WIDTH
            )
            
            # Draw label
            label = f"Class {box.class_id}"
            font = ImageFont.truetype("arial.ttf", self.FONT_SIZE)
            draw.text(
                (x1, y1 - get_line_height(self.FONT_SIZE)),
                label,
                fill=color,
                font=font
            )
        return image