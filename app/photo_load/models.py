import subprocess
import sys
from datetime import datetime
from io import BytesIO
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from wand.image import Image

sizes = {'o': 'max', 'z': 1080, 'y': 807, 'x': 604, 'm': 130, 's': 100}


def get_upload_path(instance, filename):
    return instance.get_upload_path(filename)


def get_upload_path_size_o(instance, filename):
    return instance.get_upload_path("o_{0}".format(filename))


def get_upload_path_size_z(instance, filename):
    return instance.get_upload_path("z_{0}".format(filename))


def get_upload_path_size_y(instance, filename):
    return instance.get_upload_path("y_{0}".format(filename))


def get_upload_path_size_x(instance, filename):
    return instance.get_upload_path("x_{0}".format(filename))


def get_upload_path_size_m(instance, filename):
    return instance.get_upload_path("m_{0}".format(filename))


def get_upload_path_size_s(instance, filename):
    return instance.get_upload_path("s_{0}".format(filename))


class Storage(models.Model):
    original = models.FileField(upload_to=get_upload_path)
    o_size = models.ImageField(upload_to=get_upload_path_size_o)
    z_size = models.ImageField(upload_to=get_upload_path_size_z)
    y_size = models.ImageField(upload_to=get_upload_path_size_y)
    x_size = models.ImageField(upload_to=get_upload_path_size_x)
    m_size = models.ImageField(upload_to=get_upload_path_size_m)
    s_size = models.ImageField(upload_to=get_upload_path_size_s)

    def __init__(self, *args, **kwargs):
        super(Storage, self).__init__(*args, **kwargs)
        self.salt = uuid4().hex

    def get_upload_path(self, filename):
        return '{0}/{1}'.format(self.salt, filename)

    def save(self, *args, **kwargs):
        if not self.id:
            self.o_size = self.compress('o')
            self.z_size = self.compress('z')
            self.y_size = self.compress('y')
            self.x_size = self.compress('x')
            self.m_size = self.compress('m')
            self.s_size = self.compress('s')

        super(Storage, self).save(*args, **kwargs)

    def compress(self, size):
        with Image(blob=self.original.file) as image:
            image.format = 'jpeg'
            image.compression_quality = 90
            file_name = ''.join(self.original.name.split('.')[:-1])
            io_stream = BytesIO()
            if size == 'o':
                shape = image.size
            else:
                min_side = min(image.size)
                if min_side < sizes[size]:
                    min_side = sizes[size]
                proc = sizes[size] / min_side
                shape = (int(image.width * proc), int(image.height * proc))
            image.resize(*shape)
            image.save(io_stream)
            io_stream.seek(0)
            sized = InMemoryUploadedFile(io_stream, 'ImageField',
                                         "{0}.jpeg".format(file_name),
                                         'image/jpeg', sys.getsizeof(io_stream),
                                         None)
            return sized


class Photo(models.Model):
    storage = models.OneToOneField(Storage, on_delete=models.CASCADE,
                                   primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField()
    width = models.IntegerField()
    height = models.IntegerField()
    checked = models.NullBooleanField()

    def save(self, *args, **kwargs):
        for size_type in sizes:
            size = getattr(self.storage, '{0}_size'.format(size_type))
            subprocess.run(['exiftool', '-TagsFromFile',
                            self.storage.original.path, size.path],
                           stdout=subprocess.PIPE)

        with Image(blob=self.storage.o_size.file) as image:
            self.width, self.height = image.size

        result = subprocess.run(['exiftool', '-dateTimeOriginal',
                                self.storage.original.path],
                                stdout=subprocess.PIPE)

        result = result.stdout.decode('utf-8')
        if len(result) == 0:
            self.time_created = datetime.now()
        else:
            dt = (':'.join(result.split(':')[1:])).split('+')[0]
            dt = dt.strip()
            self.time_created = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')

        super(Photo, self).save(*args, **kwargs)