from django.contrib import admin
from .models import (
    Products, Manufacturers, ProductTypes, ProductPictures
)

admin.site.register(    #自分が作成したmodelsを管理サイト上に掲載する設定
    [Products, Manufacturers, ProductTypes, ProductPictures]
)

