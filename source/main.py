from dearpygui import dearpygui as dpg

from ui.main_window import MainWindow

if __name__ == '__main__':
    dpg.create_context()
    main_window = MainWindow(800, 600)
    dpg.create_viewport(title='Drop File Example', width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()