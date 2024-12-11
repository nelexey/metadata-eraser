from PIL import Image
from PIL.ExifTags import TAGS

def get_all_metadata(file_path: str):

    with Image.open(file_path) as img:

        exif = img._getexif() if hasattr(img, '_getexif') else None

        info = img.info

        if exif is not None:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                print(f"{tag:25}: {value}")

        print("EXIF:", exif)
        print("\nInfo:", info)
        print("\nAll image attributes:", vars(img))

        return exif

def update_image_metadata(file_path: str, metadata: dict):

    with Image.open(file_path) as img:

        img.info.clear()
        img = img.convert("RGB")


        if "info" in metadata:
            img.info.update(metadata["info"])


        if "exif" in metadata and metadata["exif"]:
            exif_bytes = img.getexif()
            for key, value in metadata["exif"].items():
                exif_bytes[key] = value

            img.save(file_path, exif=exif_bytes.tobytes())
        else:
            img.save(file_path)


