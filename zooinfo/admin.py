from django.contrib import admin # для работы с админкой

# Register your models here.
from .models import Category, Product, Transaction , Tag , ProductDetail # мои медельки

# Регистрация модели Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',) # поля

# Регистрация модели Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_on_sale') # таблца с полями
    list_filter = ('category', 'is_on_sale') # фильтры для поиска  - корм , игрушка или ешё чтонибуть
    search_fields = ('name', 'description') # поле для поиска

# Регистрация модели Transaction
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'total_amount', 'transaction_date') # название товара + возрат/продажа + количество + итоговая цена + дата транзакции
    list_filter = ('transaction_type', 'transaction_date') # фильтрует по продажам и возваратам + дата

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# описание товаров
@admin.register(ProductDetail)
class ProductDetail(admin.ModelAdmin):
    list_display = ('product', 'country_of_origin')