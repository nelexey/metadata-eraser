import dearpygui.dearpygui as dpg
from ui.main_window import MainWindow
from ui.ui import AppUI  # Класс AppUI из вашего файла

# Создание контекста DearPyGui
dpg.create_context()

# Настройка стилей приложения
ui_styler = AppUI(800, 600)
ui_styler.configure_styles()

# Создание главного окна
window = MainWindow(800, 600)

# Настройка и запуск интерфейса
dpg.create_viewport(title="Metadata Cleaner", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
