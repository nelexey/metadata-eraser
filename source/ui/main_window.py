from dearpygui import dearpygui as dpg
from metadata_handler import get_all_metadata, update_image_metadata

class MainWindow:
    def __init__(self, width: int, height: int):
        self.create_gui(width, height)

    def create_gui(self, width, height):

        with dpg.window(label="Metadata Master", width=width, height=height, tag="main_window"):
            with dpg.group():
                dpg.add_input_text(label="File path", width=200, tag="path", callback=None)
                dpg.add_button(label='Submit', callback=self.on_text_change)


            with dpg.child_window(height=-1, width=-1, tag="metadata_container", autosize_x=True, autosize_y=True):
                dpg.add_group(tag="metadata_fields")

    def on_text_change(self):
        exif = get_all_metadata(dpg.get_value('path'))


        dpg.delete_item("metadata_fields", children_only=True)


        for key, val in exif.items():
            dpg.add_input_text(label=str(key), parent="metadata_fields", default_value=str(val), tag=f"field_{key}")

        dpg.add_button(label="Update Metadata", parent="metadata_fields", callback=self.update_metadata)

    def update_metadata(self):
        file_path = dpg.get_value('path')
        updated_metadata = {"exif": {}}


        for child in dpg.get_item_children("metadata_fields", slot=1):
            if dpg.get_item_type(child) == "mvAppItemType::InputText":
                label = dpg.get_item_label(child)
                value = dpg.get_value(child)
                updated_metadata["exif"][int(label)] = value

        update_image_metadata(file_path, updated_metadata)
        print("Metadata updated successfully")
