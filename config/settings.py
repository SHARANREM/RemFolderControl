import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QSpinBox, QLineEdit, QPushButton, QColorDialog, 
    QTabWidget, QFormLayout, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont
import keyboard
# --- Your Settings Class ---
class Settings:
    def __init__(self):
        self.options = ["Store", "Settings", "Favourites", "Search"] # Fixed duplicate "Option4"
        self.center_radius = 120
        self.outer_radius = 250
        self.icon_radius = 175

        self.btn_slice_bg = (200, 150, 0, 220)
        self.btn_slice_border_width = 9
        self.btn_slice_border_bg = (255, 255, 255, 150)

        self.btn_slice_bg_u = (40, 40, 40, 180)
        self.btn_slice_border_width_u = 2
        self.btn_slice_border_bg_u = (255, 255, 255, 40)

        self.inner_circle_bg = (15, 15, 15, 255)
        self.inner_circle_width = 2 
        self.inner_circle_width_u = 3 
        self.inner_circle_border = (200, 0, 0, 200)
        self.inner_circle_border_u = (255, 255, 255, 80)

        self.btn_text_col = (255, 255, 255)
        self.btn_text_format = {"Font":"Arial","Size":11,"Bold":True}
        self.angle_offset = -43  
        self.shortcut = keyboard.is_pressed("ctrl") and keyboard.is_pressed("`")    
settings = Settings()

# --- Custom Color Button Component ---
class ColorButton(QPushButton):
    def __init__(self, color_tuple, callback):
        super().__init__()
        self.color = QColor(*color_tuple)
        self.callback = callback
        self.setMinimumHeight(30)
        self.update_style()
        self.clicked.connect(self.pick_color)

    def update_style(self):
        # Set background to current color and invert text color for visibility
        rgba_str = f"rgba({self.color.red()}, {self.color.green()}, {self.color.blue()}, {self.color.alpha()})"
        text_color = "black" if self.color.lightness() > 128 else "white"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {rgba_str};
                color: {text_color};
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{ border: 1px solid #aaa; }}
        """)
        self.setText(f"RGBA({self.color.red()}, {self.color.green()}, {self.color.blue()}, {self.color.alpha()})")

    def pick_color(self):
        color = QColorDialog.getColor(self.color, self, "Select Color", QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.color = color
            self.update_style()
            # Convert back to tuple for the settings object
            self.callback((color.red(), color.green(), color.blue(), color.alpha()))

# --- Main Editor Window ---
class SettingsEditor(QMainWindow):
    def __init__(self, settings_obj):
        super().__init__()
        self.cfg = settings_obj
        self.setWindowTitle("Radial Menu Configurator")
        self.resize(500, 650)
        
        # Apply Global Dark Stylesheet
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #1e1e24; color: #e0e0e0; font-family: 'Segoe UI', Arial; }
            QGroupBox { font-weight: bold; border: 1px solid #3a3a42; border-radius: 6px; margin-top: 12px; padding-top: 12px;}
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #00adb5; }
            QLabel { font-size: 12px; }
            QSlider::groove:horizontal { height: 6px; background: #393e46; border-radius: 3px; }
            QSlider::handle:horizontal { background: #00adb5; width: 14px; margin: -4px 0; border-radius: 7px; }
            QSpinBox, QLineEdit { background-color: #2d2d35; border: 1px solid #3a3a42; border-radius: 4px; padding: 4px; color: white; }
            QSpinBox:focus, QLineEdit:focus { border: 1px solid #00adb5; }
            QTabBar::tab { background: #2d2d35; padding: 10px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px;}
            QTabBar::tab:selected { background: #00adb5; color: #1e1e24; font-weight: bold; }
            QPushButton#save_btn { background-color: #00adb5; color: #1e1e24; font-weight: bold; font-size: 14px; border-radius: 6px; padding: 10px; }
            QPushButton#save_btn:hover { background-color: #08d9e3; }
        """)

        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Tab Widget
        tabs = QTabWidget()
        tabs.addTab(self.create_geometry_tab(), "Dimensions")
        tabs.addTab(self.create_styles_tab(), "Visuals & Theme")
        tabs.addTab(self.create_misc_tab(), "Preferences")
        layout.addWidget(tabs)

        # Save Button
        # save_button = QPushButton("Save")
        # save_button.setObjectName("save_btn")
        # save_button.clicked.connect(self.print_settings)
        # layout.addWidget(save_button)

    def create_geometry_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)

        # Helper to create a slider + spinbox synced row
        def add_slider_row(label_text, min_v, max_v, current_v, setter_func):
            row_layout = QHBoxLayout()
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(current_v)
            
            spin = QSpinBox()
            spin.setRange(min_v, max_v)
            spin.setValue(current_v)

            slider.valueChanged.connect(spin.setValue)
            spin.valueChanged.connect(slider.setValue)
            spin.valueChanged.connect(setter_func)

            row_layout.addWidget(slider)
            row_layout.addWidget(spin)
            form.addRow(QLabel(label_text), row_layout)

        add_slider_row("Center Radius:", 10, 500, self.cfg.center_radius, lambda v: setattr(self.cfg, 'center_radius', v))
        add_slider_row("Outer Radius:", 10, 500, self.cfg.outer_radius, lambda v: setattr(self.cfg, 'outer_radius', v))
        add_slider_row("Icon Radius:", 10, 500, self.cfg.icon_radius, lambda v: setattr(self.cfg, 'icon_radius', v))
        add_slider_row("Angle Offset:", -180, 180, self.cfg.angle_offset, lambda v: setattr(self.cfg, 'angle_offset', v))

        return widget

    def create_styles_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)

        # Group 1: Hovered Slices
        hover_group = QGroupBox("Slice Styles (Hovered)")
        h_form = QFormLayout(hover_group)
        h_form.addRow("Background Color:", ColorButton(self.cfg.btn_slice_bg, lambda c: setattr(self.cfg, 'btn_slice_bg', c)))
        h_form.addRow("Border Color:", ColorButton(self.cfg.btn_slice_border_bg, lambda c: setattr(self.cfg, 'btn_slice_border_bg', c)))
        hb_width = QSpinBox()
        hb_width.setValue(self.cfg.btn_slice_border_width)
        hb_width.valueChanged.connect(lambda v: setattr(self.cfg, 'btn_slice_border_width', v))
        h_form.addRow("Border Width:", hb_width)
        layout.addWidget(hover_group)

        # Group 2: Unhovered Slices
        unhover_group = QGroupBox("Slice Styles (Idle)")
        u_form = QFormLayout(unhover_group)
        u_form.addRow("Background Color:", ColorButton(self.cfg.btn_slice_bg_u, lambda c: setattr(self.cfg, 'btn_slice_bg_u', c)))
        u_form.addRow("Border Color:", ColorButton(self.cfg.btn_slice_border_bg_u, lambda c: setattr(self.cfg, 'btn_slice_border_bg_u', c)))
        ub_width = QSpinBox()
        ub_width.setValue(self.cfg.btn_slice_border_width_u)
        ub_width.valueChanged.connect(lambda v: setattr(self.cfg, 'btn_slice_border_width_u', v))
        u_form.addRow("Border Width:", ub_width)
        layout.addWidget(unhover_group)

        # Group 3: Inner Circle
        inner_group = QGroupBox("Center Center Circle")
        i_form = QFormLayout(inner_group)
        i_form.addRow("Center Background:", ColorButton(self.cfg.inner_circle_bg, lambda c: setattr(self.cfg, 'inner_circle_bg', c)))
        i_form.addRow("Border (Hovered):", ColorButton(self.cfg.inner_circle_border, lambda c: setattr(self.cfg, 'inner_circle_border', c)))
        i_form.addRow("Border (Idle):", ColorButton(self.cfg.inner_circle_border_u, lambda c: setattr(self.cfg, 'inner_circle_border_u', c)))
        layout.addWidget(inner_group)

        return scroll

    def create_misc_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)

        # Font Color
        form.addRow("Text Color:", ColorButton(self.cfg.btn_text_col, lambda c: setattr(self.cfg, 'btn_text_col', c[:3]))) # slicing to RGB

        # Shortcut Text
        # shortcut_input = QLineEdit(str(self.cfg.shortcut))
        # shortcut_input.textChanged.connect(lambda t: setattr(self.cfg, 'shortcut', t))
        # form.addRow(QLabel("Shortcut String:"), shortcut_input)

        return widget

    def print_settings(self):
        print("\n--- Updated Settings Values ---")
        settings.center_radius = self.cfg.center_radius
        settings.outer_radius = self.cfg.outer_radius
        settings.btn_slice_bg = self.cfg.btn_slice_bg
        settings.angle_offset = self.cfg.angle_offset
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsEditor(settings)
    window.show()
    sys.exit(app.exec())