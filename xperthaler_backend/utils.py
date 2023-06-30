import os
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime

# Function to check parameter is present in api call or missing
def getparameter(request, param_name):
    param_value = request.data.get(param_name)
    if param_value is None or param_value == '':
        raise ValueError
    else:
        return param_value

def pictureoriginalname(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s_%s.%s" % (instance.user.id, datetime.now().strftime('%Y%m%d%H%M%S'), ext)
    return os.path.join('profile_original', filename)

def picturethumbnailname(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s_%s.%s" % (instance.user.id, datetime.now().strftime('%Y%m%d%H%M%S'), ext)
    return os.path.join('profile_thumbnail', filename)

def convertblobtoimage(image):
    if not image:
        return
    im = Image.open(BytesIO(image.read()))
    image = im.convert('RGB')
    temp_handle = BytesIO()
    image.save(temp_handle, 'jpeg', quality=95)
    temp_handle.seek(0)

    # Save image to a SimpleUploadedFile which can be saved into
    # ImageField
    suf = SimpleUploadedFile(os.path.split(image.name)[-1],
            temp_handle.read(), content_type='image/jpeg')
    return suf