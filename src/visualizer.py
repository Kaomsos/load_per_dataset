# Author: Tao Wen
# Description: 
#   visualize dataitem converting them to image_object
from PIL import Image, ImageDraw
from typing_ import DataVisualizerProtocol
from data_item import AnnotatedImageItem


class AnnotatedImageVisualizer(DataVisualizerProtocol):
    COLORS = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", 
            "#FF00FF", "#00FFFF", "#FFA500", "#800080"
    ]

    def to_image(self, item: AnnotatedImageItem) -> Image.Image:
        # Create a copy of the image to draw on
        image = item.image.copy()
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
                width=2
            )
            
            # Draw label
            label = f"Class {box.class_id}"
            draw.text(
                (x1, y1 - 10),
                label,
                fill=color
            )
        
        # Resize image while maintaining aspect ratio
        image.thumbnail((1000, 1000))
        return image