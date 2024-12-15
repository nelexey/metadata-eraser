from dearpygui import dearpygui as dpg

class AppUI:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.configure_styles()
        self.load_font()

    def configure_styles(self):
        dpg.set_global_font_scale(1)

        # Colors and theme
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (40, 40, 40))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 70, 70))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (180, 180, 180))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 5, category=dpg.mvThemeCat_Core)


        dpg.bind_theme(global_theme)


    def load_font(self):
        with dpg.font_registry():
            default_font = dpg.add_font("/Library/Fonts/JetBrainsMono-Regular.ttf", 16)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font)

        dpg.bind_font(default_font)

    def run(self):
        dpg.create_viewport(title="Metadata Cleaner UI Template", width=self.width, height=self.height)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    dpg.create_context()
    app = AppUI(800, 600)
    app.run()