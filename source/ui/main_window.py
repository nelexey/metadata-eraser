from dearpygui import dearpygui as dpg
import piexif
import os
from typing import List, Dict, Optional
from pathlib import Path

from dearpygui.dearpygui import child
from metadata_handler import MetadataHandler
from paths_walker import get_filepaths, get_all_filepaths, check_path, get_file_tree


class MainWindow:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.sidebar_width = self.width * 0.3
        self.sidebar_height = self.height
        self.metadata_window_width = self.width * 0.7 - 22
        self.metadata_window_height = self.height - 15

        if not hasattr(MainWindow, 'initiated') or not MainWindow.initiated:
            self.create_gui()
            MainWindow.initiated = True

    def create_gui(self) -> None:
        dpg.set_viewport_resize_callback(self._on_resize)

        with dpg.window(
                label="Metadata Cleaner",
                width=self.width,
                height=self.height,
                tag="main_window",
                no_collapse=True,
                no_close=True,
                no_move=True,
                no_title_bar=True,
                no_scroll_with_mouse=True,
                no_scrollbar=True,
                no_resize=True,
        ):
            with dpg.group(horizontal=True):
                with dpg.group(width=0.3 * self.width, tag='sidebar'):
                    dpg.add_input_text(tag="file_path")
                    dpg.add_button(label="Show Metadata in file", tag="btn_show_metadata", callback=self.show_metadata)
                    dpg.add_button(label="Show Metadata in dir files", tag="btn_show_metadata_list",
                                   callback=self.show_metadata_dir, enabled=True)
                    dpg.add_button(label="Show Metadata in all dirs files", tag="btn_show_metadata_list_recursive",
                                   callback=self.show_metadata_dir_recursive, enabled=True)
                    with dpg.group():
                        dpg.add_separator()
                        dpg.add_button(label="Clear Metadata", callback=self.clear_metadata, tag="btn_clear")
                        dpg.add_button(label="Clear Directory", callback=self.clear_metadata_dir)
                        dpg.add_button(label="Clear Directory Recursive", callback=self.clear_metadata_dir_recursive)

                dpg.add_child_window(
                    width=self.metadata_window_width,
                    height=self.metadata_window_height,
                    tag="metadata_window",
                )

    def _on_path_change(self, sender, path: str):
        print(path)
        status = check_path(path)
        print(status)
        if status == -1:
            return

        dpg.delete_item("metadata_window", children_only=True)
        if status == 0:
            self.show_metadata_all()
        elif status == 1:
            self.show_metadata()

    def show_metadata(self) -> None:

        file_path = dpg.get_value("file_path")
        dpg.delete_item("metadata_window", children_only=True)

        try:
            metadata = MetadataHandler.load_metadata(file_path)
            self._display_metadata_for_file(file_path, metadata)
        except Exception as e:
            dpg.add_text(e, parent="metadata_window")

    def show_metadata_dir(self) -> None:
        dpg.delete_item("metadata_window", children_only=True)

        base_path = dpg.get_value("file_path")
        paths = get_filepaths(base_path)

        main_tab_bar = dpg.add_tab_bar(parent="metadata_window", tag="files_tab_bar")

        for path in paths:
            try:
                metadata = MetadataHandler.load_metadata(path)
                file_tab = dpg.add_tab(label=Path(path).name, parent=main_tab_bar)

                type_tab_bar = dpg.add_tab_bar(parent=file_tab)

                if not metadata:
                    dpg.add_text("No metadata found.", color=(255, 165, 0), parent=file_tab)
                    continue

                has_valid_metadata = False
                for ifd, tags in metadata.items():
                    if isinstance(tags, dict) and tags:
                        has_valid_metadata = True
                        break

                if not has_valid_metadata:
                    dpg.add_text("No valid metadata found.", color=(255, 165, 0), parent=file_tab)
                    continue

                for ifd, tags in metadata.items():
                    if not isinstance(tags, dict) or not tags:
                        continue

                    try:
                        type_tab = dpg.add_tab(label=ifd, parent=type_tab_bar)
                        for tag_id, value in tags.items():
                            try:
                                tag_name = self._get_tag_name(ifd, tag_id)
                                # Обработка значения в зависимости от его типа
                                if isinstance(value, bytes):
                                    display_value = f"<binary data: {len(value)} bytes>"
                                elif isinstance(value, (list, tuple)):
                                    display_value = ", ".join(map(str, value))
                                else:
                                    display_value = str(value)

                                dpg.add_text(f"{tag_name}: {display_value}", parent=type_tab)
                            except Exception as e:
                                dpg.add_text(f"Error displaying tag {tag_id}: {str(e)}",
                                             color=(255, 165, 0), parent=type_tab)
                    except Exception as e:
                        dpg.add_text(f"Error parsing {ifd} data: {str(e)}",
                                     color=(255, 0, 0), parent=type_tab_bar)

            except Exception as e:
                error_tab = dpg.add_tab(label=f"Error: {Path(path).name}", parent=main_tab_bar)
                dpg.add_text(f"Error processing file: {str(e)}",
                             color=(255, 0, 0), parent=error_tab)

    def show_metadata_dir_recursive(self) -> None:
        dpg.delete_item("metadata_window", children_only=True)

        base_path = dpg.get_value("file_path")
        file_tree = get_file_tree(base_path)

        def process_directory(dir_data: dict, parent_id) -> None:
            dir_name = os.path.basename(dir_data['path']) or 'Root'
            dir_tab = dpg.add_tab(label=dir_name, parent=parent_id)

            if dir_data['files']:
                files_tab_bar = dpg.add_tab_bar(parent=dir_tab)
                for file_path in dir_data['files']:
                    try:
                        metadata = MetadataHandler.load_metadata(file_path)
                        file_tab = dpg.add_tab(label=Path(file_path).name, parent=files_tab_bar)

                        if not metadata:
                            dpg.add_text("No metadata found.", color=(255, 165, 0), parent=file_tab)
                            continue

                        type_tab_bar = dpg.add_tab_bar(parent=file_tab)
                        for ifd, tags in metadata.items():
                            if not isinstance(tags, dict) or not tags:
                                continue

                            type_tab = dpg.add_tab(label=ifd, parent=type_tab_bar)
                            for tag_id, value in tags.items():
                                tag_name = self._get_tag_name(ifd, tag_id)

                                if isinstance(value, bytes):
                                    display_value = f"<binary data: {len(value)} bytes>"
                                elif isinstance(value, (list, tuple)):
                                    display_value = ", ".join(map(str, value))
                                else:
                                    display_value = str(value)
                                dpg.add_text(f"{tag_name}: {display_value}", parent=type_tab)

                    except Exception as e:
                        error_tab = dpg.add_tab(label=f"Error: {Path(file_path).name}", parent=files_tab_bar)
                        dpg.add_text(f"Error processing file: {str(e)}", color=(255, 0, 0), parent=error_tab)

            if dir_data['dirs']:
                subdirs_tab_bar = dpg.add_tab_bar(parent=dir_tab)
                for subdir_data in dir_data['dirs'].values():
                    process_directory(subdir_data, subdirs_tab_bar)

        root_tab_bar = dpg.add_tab_bar(parent="metadata_window")
        process_directory(file_tree, root_tab_bar)

    def clear_metadata(self, paths_list: List[str]) -> None:
        try:
            self._set_clearing_status(True)

            for path in paths_list:
                new_path = MetadataHandler.clear_metadata(path)
                dpg.add_text(
                    f"Metadata cleared. Saved as {new_path}",
                    parent="metadata_window"
                )

            self.show_metadata()

        except Exception as e:
            self._display_error(f"Error clearing metadata: {str(e)}")
        finally:
            self._set_clearing_status(False)

    def clear_metadata_dir(self) -> None:
        paths = get_filepaths(dpg.get_value("file_path"))
        self.clear_metadata(paths)

    def clear_metadata_dir_recursive(self) -> None:
        paths = get_all_filepaths(dpg.get_value("file_path"))
        self.clear_metadata(paths)

    def _display_metadata_for_file(
            self,
            file_path: str,
            metadata: Dict,
            parent_tab_bar=None
    ) -> None:
        if not metadata or not any(metadata.values()):
            dpg.add_text("No metadata found.", color=(255, 165, 0),
                         parent="metadata_window" if not parent_tab_bar else parent_tab_bar)
            return

        file_name = Path(file_path).name
        tab_bar_id = f"tab_bar_{file_name}"

        if not parent_tab_bar:
            dpg.delete_item("metadata_window", children_only=True)
            with dpg.tab_bar(parent="metadata_window", tag=tab_bar_id):
                self._create_type_tabs(metadata, file_path)
        else:
            with dpg.tab(label=file_name, parent=parent_tab_bar):
                with dpg.tab_bar(tag=tab_bar_id):
                    self._create_type_tabs(metadata, file_path)

    def _get_tag_name(self, ifd: str, tag_id: str) -> str:
        return (piexif.TAGS[ifd][tag_id]["name"]
                if tag_id in piexif.TAGS[ifd]
                else f"Unknown ({tag_id})")

    def _display_error(self, error_message: str) -> None:
        dpg.delete_item("metadata_window", children_only=True)
        self.add_text(error_message, color=(255, 0, 0))

    def _set_clearing_status(self, is_clearing: bool) -> None:
        dpg.set_item_label('btn_clear', 'Clearing' if is_clearing else 'Clear Metadata')

    def _create_type_tabs(self, metadata: Dict, file_path: str) -> None:
        for ifd, tags in metadata.items():
            if not tags:
                continue

            try:
                with dpg.tab(label=ifd):
                    for tag_id, value in tags.items():
                        tag_name = self._get_tag_name(ifd, tag_id)
                        dpg.add_text(f"{tag_name}: {value}")
            except Exception as e:
                dpg.add_text(f"Error parsing {ifd} data: {str(e)}", color=(255, 0, 0))

    def _on_resize(self) -> None:
        new_width = dpg.get_viewport_client_width()
        new_height = dpg.get_viewport_client_height()

        self.__init__(new_width, new_height)

        dpg.set_item_width("main_window", self.width)
        dpg.set_item_height("main_window", self.height)
        dpg.set_item_width("sidebar", self.sidebar_width)
        dpg.set_item_width("metadata_window", self.metadata_window_width)
        dpg.set_item_height("metadata_window", self.metadata_window_height)
