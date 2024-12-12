from PIL import Image
import piexif
import os

from paths_walker import get_filepaths, get_all_filepaths

class MetadataHandler:
    @staticmethod
    def load_metadata(file_path):
        """Load metadata from an image file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")
        try:
            return piexif.load(file_path)
        except piexif.InvalidImageDataError:
            print(f"Warning: Invalid image data in {file_path}. Skipping.")
            return None

    @staticmethod
    def clear_metadata(file_path):
        """Clear metadata from an image file and save the cleaned file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")
        try:
            image = Image.open(file_path)
            data = list(image.getdata())
            filename, ext = os.path.splitext(file_path)
            new_path = f"{filename}_cleaned{ext}"
            image_without_metadata = Image.new(image.mode, image.size)
            image_without_metadata.putdata(data)
            image_without_metadata.save(new_path)
            return new_path
        except IOError as e:
            print(f"Error processing image {file_path}: {e}")
            return None

    @staticmethod
    def process_all_metadata(root_directory, pattern="*"):
        """Processes metadata for all files in the given directory and subdirectories."""
        filepaths = get_all_filepaths(root_directory, pattern)
        results = []
        if filepaths:
            for filepath in filepaths:
                metadata = MetadataHandler.load_metadata(filepath)
                results.append({'filepath': filepath, 'metadata': metadata})
        return results

    @staticmethod
    def clear_all_metadata(root_directory, pattern="*"):
        """Clears metadata from all files in the given directory and subdirectories."""
        filepaths = get_all_filepaths(root_directory, pattern)
        if filepaths:
            for filepath in filepaths:
                cleaned_path = MetadataHandler.clear_metadata(filepath)
                if cleaned_path:
                    print(f"Metadata cleared from {filepath}, saved as {cleaned_path}")