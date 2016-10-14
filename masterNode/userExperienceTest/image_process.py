# coding=utf-8

import math
import os

from PIL import Image
from django.core.files.storage import default_storage
from masterNode import settings
from .models import ImageReport


class ImageProcess:
    def __init__(self, logger):
        self.logger = logger

    def process(self, image1_path, image2_path):
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)
        return self.similarity_with_split(image1, image2)

    # def process(self, correct_img_dir, report_dir, image_name, test_id, browser):
    #     self.logger.info(u'开始图像处理')
    #     correct_image_path = os.path.join(correct_img_dir, image_name)
    #     correct_img = Image.open(correct_image_path)
    #     real_image_path = os.path.join(report_dir, image_name)
    #     real_image = Image.open(real_image_path)
    #     image_status = self.similarity_with_split(correct_img, real_image)
    #     self.logger.info(u'图像状态' + str(image_status))
    #
    #     real_image_path = real_image_path.replace(settings.MEDIA_ROOT, '')
    #     real_image_path = default_storage.url(real_image_path)
    #     correct_image_path = correct_image_path.replace(settings.MEDIA_ROOT, '')
    #     correct_image_path = default_storage.url(correct_image_path)
    #     image_report_instance = ImageReport(test_id=test_id,
    #                                         browser=browser,
    #                                         name=image_name,
    #                                         correct_image_path=correct_image_path,
    #                                         real_image_path=real_image_path,
    #                                         image_status=image_status)
    #     image_report_instance.save()
    #     self.logger.info(u'截图相关信息已存入数据库')
    #     return image_status

    def similarity(self, image1, image2):
        g = image1.histogram()
        s = image2.histogram()
        assert len(g) == len(s), "error"

        g_total = sum(g)
        s_total = sum(s)
        res = 0
        for index in range(0, len(g)):
            res += math.sqrt((float(g[index]) / g_total) * (float(s[index]) / s_total))

        return 1 if res > 0.9 else 0

    def split_image(self, image, part_size):
        pw, ph = part_size
        w, h = image.size
        sub_image_list = []

        assert w % pw == h % ph == 0, "error"

        for i in range(0, w, pw):
            for j in range(0, h, ph):
                sub_image = image.crop((i, j, i + pw, j + ph)).copy()
                sub_image_list.append(sub_image)

        return sub_image_list

    def similarity_with_split(self, image1, image2, size=(512, 512), part_size=(128, 128)):

        image1 = image1.resize(size).convert("RGB")
        sub_image1 = self.split_image(image1, part_size)
        image2 = image2.resize(size).convert("RGB")
        sub_image2 = self.split_image(image2, part_size)

        sub_data = 0
        count = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            # count += 1
            # im1.save(r"C:\tmp\img1_" + str(count) + ".png", "PNG")
            # im2.save(r"C:\tmp\img2_" + str(count) + ".png", "PNG")
            sub_data += self.similarity(im1, im2)

        x = size[0] / part_size[0]
        y = size[1] / part_size[1]

        pre = float(sub_data) / (x * y)
        self.logger.info(str(pre))
        return True if pre > 0.9 else False
