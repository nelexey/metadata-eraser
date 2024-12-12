from dearpygui import dearpygui as dpg
import piexif
from typing import List, Dict, Optional
from pathlib import Path

from metadata_handler import MetadataHandler
from paths_walker import get_filepaths, get_all_filepaths, check_path


class MainWindow:
    """
    Главное окно приложения для просмотра и очистки метаданных изображений.
    """

    def __init__(self, width: int, height: int):
        """
        Инициализация главного окна.

        Args:
            width: Ширина окна
            height: Высота окна
        """
        self.width = width
        self.height = height
        self.create_gui()

    def create_gui(self) -> None:
        """Создание основного интерфейса приложения."""
        dpg.set_viewport_resize_callback(self._on_resize)

        with dpg.window(
                label="Metadata Cleaner",
                width=self.width,
                height=self.height,
                tag="main_window",
                no_collapse=True,
                no_close=True
        ):

            """Создание секции с полем ввода и кнопками."""
            with dpg.group():
                dpg.add_input_text(label="File path", width=400, tag="file_path", callback=self._on_path_change)
                dpg.add_button(label="Show Metadata", callback=self.show_metadata)
                dpg.add_button(label="Show Metadata list", callback=self.show_metadata_all, enabled=False)

            """Создание основной области контента с метаданными и кнопками."""
            with dpg.group(horizontal=True):
                # Левая панель - отображение метаданных
                with dpg.child_window(
                        height=self.height - 300,
                        width=self.width - 150,
                        tag="metadata_container"
                ):
                    dpg.add_group(tag="metadata_display")

                # Правая панель - колонка кнопок
                with dpg.group():
                    self._create_action_buttons()

    def _on_path_change(self, sender, path: str):
        print(path)
        status = check_path(path)
        print(status)
        if status == -1:
           return

        dpg.delete_item("metadata_display", children_only=True)
        if status == 0:
            self.show_metadata_all()
        elif status == 1:
            self.show_metadata()

    def _create_action_buttons(self) -> None:
        """Создание кнопок действий."""
        dpg.add_button(
            label="Clear Metadata",
            callback=self.clear_metadata,
            tag="btn_clear",
            width=100,
            height=100
        )
        dpg.add_button(label="Clear Directory",
                       callback=self.clear_metadata_dir,
                       width=100,
                       height=100)
        dpg.add_button(label="Clear Directory Recursive",
                       callback=self.clear_metadata_dir_recursive,
                       width=100,
                       height=100)

    def show_metadata(self) -> None:
        file_path = dpg.get_value("file_path")
        metadata = MetadataHandler.load_metadata(file_path)
        self._display_metadata_for_file(file_path, metadata)

    def show_metadata_all(self) -> None:
        """Отображение метаданных для всех файлов в директории."""
        base_path = dpg.get_value("file_path")
        paths = get_filepaths(base_path)
        print(paths)
        for path in paths:
            print(path)
            metadata = MetadataHandler.load_metadata(path)
            self._display_metadata_for_file(path, metadata, color=(255, 165, 0))

    def clear_metadata(self, paths_list: List[str]) -> None:
        try:
            self._set_clearing_status(True)

            for path in paths_list:
                new_path = MetadataHandler.clear_metadata(path)
                dpg.add_text(
                    f"Metadata cleared. Saved as {new_path}",
                    parent="metadata_display"
                )

            self.show_metadata()

        except Exception as e:
            self._display_error(f"Error clearing metadata: {str(e)}")
        finally:
            self._set_clearing_status(False)

    def clear_metadata_dir(self) -> None:
        """Очистка метаданных для всех файлов в директории."""
        paths = get_filepaths(dpg.get_value("file_path"))
        self.clear_metadata(paths)

    def clear_metadata_dir_recursive(self) -> None:
        """Очистка метаданных для всех файлов в директории рекурсивно."""
        paths = get_all_filepaths(dpg.get_value("file_path"))
        self.clear_metadata(paths)

    def _display_metadata_for_file(
            self,
            file_path: str,
            metadata: Dict,
            color: Optional[tuple] = None
    ) -> None:
        if not metadata or not any(metadata.values()):
            self._add_text("No metadata found.", color=(255, 165, 0))
            return

        self._add_text(f"Metadata for file {file_path}:", color=color)

        for ifd, tags in metadata.items():
            if not tags:
                continue

            try:
                self._add_text(f" --- {ifd} ---")
                for tag_id, value in tags.items():
                    tag_name = self._get_tag_name(ifd, tag_id)
                    self._add_text(f"     {tag_name}: {value}")
            except:
                self._add_text(f"     Can't parse data", color=(255, 0, 0))
                continue

    def _get_tag_name(self, ifd: str, tag_id: str) -> str:
        return (piexif.TAGS[ifd][tag_id]["name"]
                if tag_id in piexif.TAGS[ifd]
                else f"Unknown ({tag_id})")

    def _add_text(self, text: str, color: Optional[tuple] = None) -> None:
        kwargs = {"parent": "metadata_display"}
        if color:
            kwargs["color"] = color
        dpg.add_text(text, **kwargs)

    def _display_error(self, error_message: str) -> None:
        dpg.delete_item("metadata_display", children_only=True)
        self._add_text(error_message, color=(255, 0, 0))

    def _set_clearing_status(self, is_clearing: bool) -> None:
        dpg.set_item_label('btn_clear', 'Clearing' if is_clearing else 'Clear Metadata')

    def _on_resize(self) -> None:
        """Обработчик изменения размера окна."""
        dpg.set_item_width("main_window", dpg.get_viewport_client_width())
        dpg.set_item_height("main_window", dpg.get_viewport_client_height())