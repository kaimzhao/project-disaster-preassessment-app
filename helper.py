from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


# Open Image
def get_exif(img):
    exif = Image.open(img)._getexif()

    if exif is not None:
        for key, value in exif.items():
            name = TAGS.get(key, key)
            exif[name] = exif.pop(key)

        if 'GPSInfo' in exif:
            for key in exif['GPSInfo'].keys():
                name = GPSTAGS.get(key, key)
                exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)

    return exif or {}

#Extract Lat Lng and Convert to Decimals
def get_decimal_coordinates(info):
    for key in {'GPSLatitude', 'GPSLongitude'}:
        if key in info and key + 'Ref' in info:
            new_key = 'lat' if key == 'GPSLatitude' else 'long'
            e = info[key]
            ref = info[key + 'Ref']
            info[new_key] = ( e[0][0]/e[0][1] +
                          e[1][0]/e[1][1] / 60 +
                          e[2][0]/e[2][1] / 3600
                        ) * (-1 if ref in {'S','W'} else 1)

    if 'lat' in info and 'long' in info:
        return info['lat'], info['long']
    return None, None


def get_lat_long(img):
    return get_decimal_coordinates(get_exif(img).get('GPSInfo') or {})

