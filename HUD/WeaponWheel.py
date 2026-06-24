import sys
import math
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QCursor
from PySide6.QtCore import Qt, QPointF,QTimer
from config.settings import settings as datas

class WeaponWheel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RemFolderControlHUD")
        self.resize(600, 600)
        
        # Make window transparent and borderless
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Track mouse movements even if buttons aren't clicked
        self.setMouseTracking(True)
        
        # Weapon slots (Works dynamically with any number of items!)
        self.weapons = datas.options
        self.num_slices = len(self.weapons)
        
        # -1 means nothing is selected (mouse is in center cancel zone)
        self.hovered_slice = -1
        self.center_radius = datas.center_radius  # Match your original cancel zone radius
    
    def mouseMoveEvent(self, event):
        """Tracks direct mouse coordinates relative to the widget center for selection."""
        # 1. Find the absolute center of the widget relative to the screen
        center_pos = self.mapToGlobal(self.rect().center())
        
        # 2. Get the current global mouse position
        current_mouse_pos = QCursor.pos()
        
        # 3. Calculate the directional vector relative to the visual center
        dx = current_mouse_pos.x() - center_pos.x()
        dy = current_mouse_pos.y() - center_pos.y()
        
        distance = math.sqrt(dx**2 + dy**2)

        # 4. Handle Deadzone / Central Cancel Area
        if distance < datas.center_radius :
            if self.hovered_slice != -1:
                self.hovered_slice = -1
                self.update()
            return

        # 5. Calculate the angle based on the pull vector (-dy accounts for flipped screen space Y)
        angle = math.atan2(-dy, dx)
        angle_deg = math.degrees(angle)
        
        # 6. Normalize angle to 0-360 degrees (0 at 12 o'clock)
        normalized_angle = (90 - angle_deg) % 360
        
        # 7. Map angle to the slice index
        span_angle = 360 / self.num_slices

        angle_offset = datas.angle_offset
        normalized_angle = (normalized_angle + angle_offset) % 360

        new_hover = int(normalized_angle // span_angle)
            
        # 8. Update selection
        if new_hover != self.hovered_slice:
            self.hovered_slice = new_hover
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2
        
        outer_radius = datas.outer_radius
        icon_radius = datas.icon_radius

        span_angle = 360 / self.num_slices
        
        # Draw the slices
        for i in range(self.num_slices):
            start_angle = 90 - (i * span_angle) - (span_angle / 2)
            
            # Highlight matching index
            if i == self.hovered_slice:
                painter.setBrush(QBrush(QColor(*datas.btn_slice_bg))) # Golden Hover
                painter.setPen(QPen(QColor(*datas.btn_slice_border_bg), datas.btn_slice_border_width))
            else:
                painter.setBrush(QBrush(QColor(*datas.btn_slice_bg_u)))  # Default Dark Gray
                painter.setPen(QPen(QColor(*datas.btn_slice_border_bg_u), datas.btn_slice_border_width_u))
            
            painter.drawPie(
                int(center_x - outer_radius), 
                int(center_y - outer_radius), 
                int(outer_radius * 2), 
                int(outer_radius * 2), 
                int(start_angle * 16), 
                int(-span_angle * 16)
            )

            # Draw weapon titles
            mid_angle_deg = start_angle - (span_angle / 2)
            mid_angle_rad = math.radians(mid_angle_deg)
            
            text_x = center_x + math.cos(mid_angle_rad) * icon_radius
            text_y = center_y - math.sin(mid_angle_rad) * icon_radius
            
            painter.setPen(QColor(*datas.btn_text_col))
            painter.setFont(QFont(datas.btn_text_format["Font"], datas.btn_text_format["Size"], QFont.Bold if datas.btn_text_format["Bold"] else QFont.Normal))
            painter.drawText(QPointF(text_x - 25, text_y + 5), self.weapons[i])

        # Draw Inner Core (Cancel Zone visual match)
        painter.setBrush(QBrush(QColor(*datas.inner_circle_bg)))
        
        # Highlight center if nothing is selected
        if self.hovered_slice == -1:
            painter.setPen(QPen(QColor(*datas.inner_circle_border), datas.inner_circle_width)) # Red border for cancel zone
        else:
            painter.setPen(QPen(QColor(*datas.inner_circle_border_u), datas.inner_circle_width_u))
            
        painter.drawEllipse(
            int(center_x - datas.center_radius ), 
            int(center_y - datas.center_radius ), 
            int(datas.center_radius  * 2), 
            int(datas.center_radius  * 2)
        )

    def show_hud(self):
        self.hovered_slice = -1
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_hud(self,func):
        func(self.hovered_slice)
        self.hide()

#====================================================================
def check_keys():
    if datas.shortcut:
        if not wheel.isVisible():
            wheel.show_hud()
    else:
        if wheel.isVisible():
            wheel.hide_hud()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wheel = WeaponWheel()
    timer = QTimer()
    timer.timeout.connect(check_keys)
    timer.start(16)  # ~60 FPS
    sys.exit(app.exec())