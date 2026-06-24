import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import keyboard

from HUD.WeaponWheel import WeaponWheel
import HUD.OtherFuncs as ofs
from config.settings import settings as datas
from config.settings import SettingsEditor 

is_editing = False

def check_keys():
    global is_editing
    
    if is_editing:
        return

    if keyboard.is_pressed("ctrl") and keyboard.is_pressed("`"):
        if not wheel.isVisible():
            wheel.show_hud()
    else:
        if wheel.isVisible():
            wheel.hide_hud(func)

def func(v):
    global is_editing
    if v == 1:
        if hasattr(app, "settings_window"):
            is_editing = True
            if not app.settings_window.isVisible():
                app.settings_window.show()
                app.settings_window.raise_()
                app.settings_window.activateWindow()

# --- Custom Close Event Handler ---
def on_settings_closed():
    global is_editing
    is_editing = False
    # Cleanly hide the weapon wheel when you exit editing mode
    if wheel.isVisible():
        wheel.hide_hud(lambda v: None) 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # CRITICAL FIX: Stop PySide6 from killing the app when you close the settings UI
    app.setQuitOnLastWindowClosed(False)
    
    wheel = WeaponWheel()
    app.settings_window = SettingsEditor(datas) 
    
    # Intercept the settings window close event to reset our state
    app.settings_window.closeEvent = lambda event: on_settings_closed()
    
    timer = QTimer()
    timer.timeout.connect(check_keys)
    timer.start(16)  # ~60 FPS
    
    sys.exit(app.exec())