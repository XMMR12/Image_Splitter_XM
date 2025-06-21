# -*- coding: utf-8 -*-
"""
Spyder Editor

Image Splitter v1.1 fast edition

"""
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QHBoxLayout, QVBoxLayout, QFileDialog, QComboBox, QCheckBox)
from PyQt5.QtGui import QPixmap,QPainter,QPen,QImage
from PyQt5.QtCore import Qt

import os
import cv2
import numpy as np

class ImageSplitter(QWidget):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Splitter [2x2 .. 30x30] V1.1")
    
        # Image display label
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
    
        # Button to select image
        self.select_button = QPushButton("Select Image")
        self.select_button.clicked.connect(self.selectImage)
    
        # Output grid size label and combo
        self.grid_size_label = QLabel("Grid size:")
        self.grid_size_label.setFixedWidth(60)
        self.grid_size_combo = QComboBox()
        self.populateGridSizes()
    
        # Overlay checkbox
        self.overlay_checkbox = QCheckBox("Show Grid Overlay")
        self.overlay_checkbox.setChecked(False)
        self.overlay_checkbox.stateChanged.connect(lambda: self.displayImage(overlay=self.overlay_checkbox.isChecked()))
    
        # Layout for grid size and overlay checkbox in one row
        grid_overlay_layout = QHBoxLayout()
        grid_overlay_layout.addWidget(self.select_button)
        grid_overlay_layout.addWidget(self.grid_size_label)
        grid_overlay_layout.addWidget(self.grid_size_combo)
        grid_overlay_layout.addWidget(self.overlay_checkbox)
   
        # Button to split the image
        self.split_button = QPushButton("Split Image")
        self.split_button.clicked.connect(self.splitImage)
        self.split_button.setEnabled(False)
    
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(grid_overlay_layout)  # Add the combined layout here
        main_layout.addWidget(self.split_button)
    
        self.grid_size_combo.currentIndexChanged.connect(lambda: self.displayImage(overlay=self.overlay_checkbox.isChecked()))
        
        self.setLayout(main_layout)
        self.resize(700, 500)

    def populateGridSizes(self):
        # Add options from 2x2 to 12x12
        for i in range(2, 31):
            self.grid_size_combo.addItem(f"{i}x{i}")
        # Add aspect ratio options
        aspect_ratios = ["1x2", "2x1", "2x2", "3x2", "2x3"]
        for ratio in aspect_ratios:
            self.grid_size_combo.addItem(ratio)

    def overlay_grid_lines(self, pixmap, rows, cols):
        """Draw grid lines on the pixmap."""
        painter = QPainter(pixmap)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)

        width = pixmap.width()
        height = pixmap.height()

        # Draw vertical lines
        for j in range(1, cols):
            x = j * width / cols
            painter.drawLine(int(x), 0, int(x), height)

        # Draw horizontal lines
        for i in range(1, rows):
            y = i * height / rows
            painter.drawLine(0, int(y), width, int(y))

        painter.end()
        return pixmap

    def selectImage(self):
        filename = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")[0]
        if filename:
            self.image_path = filename
            self.image = cv2.imread(filename)
            if self.image is not None:
                # Display without overlay initially
                self.displayImage()
                self.split_button.setEnabled(True)
            else:
                self.image_label.setText("Error loading image.")

    def convert_cv_qt(self, cv_img):
        """Convert from an OpenCV image (numpy array) to QPixmap."""
        height, width = cv_img.shape[:2]
        bytes_per_line = 3 * width
        q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        return QPixmap.fromImage(q_img)

    def displayImage(self, overlay=False):
        """Display image with optional grid lines overlay."""
        if self.image is None:
            return
    
        # Convert OpenCV image to QPixmap
        pixmap = self.convert_cv_qt(self.image)
    
        if overlay and self.overlay_checkbox.isChecked():
            selected_text = self.grid_size_combo.currentText()
            rows, cols = map(int, selected_text.split('x'))
    
            # Create a copy of the pixmap to draw on
            pixmap_with_lines = QPixmap(pixmap)
            painter = QPainter(pixmap_with_lines)
            painter.setRenderHint(QPainter.Antialiasing)  # Smoother lines
    
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
    
            width = pixmap.width()
            height = pixmap.height()
    
            # Draw vertical lines (including the right edge)
            for j in range(1, cols):
                x = round(j * width / cols)  # Use round() for better precision
                painter.drawLine(x, 0, x, height)
    
            # Draw horizontal lines (including the bottom edge)
            for i in range(1, rows):
                y = round(i * height / rows)  # Use round() for better precision
                painter.drawLine(0, y, width, y)
    
            painter.end()
        else:
            pixmap_with_lines = pixmap
    
        # Scale the pixmap to fit the label while maintaining aspect ratio
        scaled_pixmap = pixmap_with_lines.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation  # Better scaling quality
        )
        self.image_label.setPixmap(scaled_pixmap)
    '''#old code : #not working good (also decreased quality)
    def displayImage(self, overlay=False):
		"""Display image with optional grid lines overlay based on checkbox."""
        if self.image is None:
            return
        # Convert to QPixmap
        pixmap = self.convert_cv_qt(self.image)
        if overlay and self.overlay_checkbox.isChecked():
            selected_text = self.grid_size_combo.currentText()
            rows, cols = map(int, selected_text.split('x'))
            height, width = self.image.shape[:2]
            overlay_img = self.image.copy()
            q_img = QImage(overlay_img.data, width, height, 3 * width, QImage.Format_RGB888).rgbSwapped()
            painter = QPainter()
            painter.begin(q_img)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            # Draw vertical lines
            for j in range(1, cols):
                x = j * width / cols
                painter.drawLine(int(x), 0, int(x), height)
            # Draw horizontal lines
            for i in range(1, rows):
                y = i * height / rows
                painter.drawLine(0, int(y), width, int(y))
            painter.end()
            pixmap_with_lines = QPixmap.fromImage(q_img)
        else:
            pixmap_with_lines = self.convert_cv_qt(self.image)
        scaled_pixmap = pixmap_with_lines.scaled(600, 400, Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
    '''

    def splitImage(self):
        if self.image is None:
            return

        # Parse selected grid size
        selected_text = self.grid_size_combo.currentText()
        if 'x' in selected_text:
            rows, cols = map(int, selected_text.split('x'))
        else:
            # Check for aspect ratios like 1x2
            try:
                rows, cols = map(int, selected_text.split('x'))
            except:
                print("Invalid grid size.")
                return

        height, width = self.image.shape[:2]
        row_height = height // rows
        col_width = width // cols
        
        #filepath=os.getcwd()
        foldername="output_images"
        if foldername not in os.listdir():
            os.mkdir(foldername)
        # Create directory or save images with unique names
        for i in range(rows):
            for j in range(cols):
                y1 = i * row_height
                y2 = y1 + row_height if i < rows - 1 else height
                x1 = j * col_width
                x2 = x1 + col_width if j < cols - 1 else width
                cropped_img = self.image[y1:y2, x1:x2]
                filename = f"./{foldername}/output_{i}_{j}.jpg"
                cv2.imwrite(filename, cropped_img)

        print(f"{rows}x{cols} images saved successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSplitter()
    window.show()
    sys.exit(app.exec_())