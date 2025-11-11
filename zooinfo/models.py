from django.db import models # импортирут все типы полей

# Create your models here.
# ORM описание баз данных как классы питона 
# class __ (models.Model) - класс который наследуется  , превращяется с помощью Django в таблицу в БД при миграции

    

class Tag(models.Model): # многие ко многим
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        
    def __str__(self):
        return self.name
    
# 1 модель категории
class Category(models.Model):
    """
    Модель для классификации товаров (Корм, Игрушки, Аксессуары).
    """
    name = models.CharField(
        max_length=100, # максимальный размер строки в БД 
        unique=True, # проверка на уникальность чтобы категории не повторялись 
        verbose_name="Название категории"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self): # опредляет как будет отоброжатся  - если нету то ничего не будет работать 
        return self.name

# 2 модель товаров
class Product(models.Model):
    """
    Модель для хранения основной информации о зоотоваре.
    """
    # Связь "Один-ко-Многим" с Category 
    #
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, # Если удалить категорию и не поставить NULL - то удалятся все товары !!! WARNING !!!
        null=True, # разрешает полю быть пустым
        verbose_name="Категория"
    )

    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Цена товара (DecimalField  - для того чтобы точно посчитать сумму + копейки)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Цена (BYN)"
    )
    
    # Остаток на складе
    stock_quantity = models.IntegerField(default=0, verbose_name="Остаток на складе") # default=0  при создании нового товара будет показывать 0
    
    # отслеживание акций
    is_on_sale = models.BooleanField(default=False, verbose_name="Акционный товар") # подсветка что товар на акции

    is_active = models.BooleanField(
        default=True,
        verbose_name="В продаже"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        # проверяет что бы небыло одинаковых названий в одной котегории
        unique_together = ('name', 'category')

    tags = models.ManyToManyField(
        Tag, # изза того что добавил тэг в низ - тэг был невидим для товаров 
        blank=True, # разрешает быть пустым
        verbose_name="Теги")

    def __str__(self):
        return f"{self.name} ({self.category.name if self.category else 'Без категории'})"

# 3 модель транзакций - (Продажи и Возвраты)
class Transaction(models.Model):
    """
    Модель для отслеживания продаж и возвратов.
    """
    TRANSACTION_TYPES = [
        ('SALE', 'Продажа'),
        ('RETURN', 'Возврат'),
    ] # выбор продаётся или возвращается товар

    product = models.ForeignKey( # один ко многим 
        Product,
        on_delete=models.PROTECT, # PROTECT чтобы 100% транзакции не удалились
        verbose_name="Товар"
    )
    
    transaction_type = models.CharField(
        max_length=6,
        choices=TRANSACTION_TYPES,
        default='SALE',
        verbose_name="Тип транзакции"
    )
    
    quantity = models.IntegerField(verbose_name="Количество")
    
    # Общая сумма транзакции (quantity * price на момент транзакции)
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Общая сумма"
    )
    
    # Дата и время совершения транзакции
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время") # auto_now_add что бы django сам подтянул время

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-transaction_date'] # Сортировка от новых к старым

    def __str__(self):
        return f"{self.transaction_type} {self.quantity}x {self.product.name} ({self.transaction_date.strftime('%Y-%m-%d')})"
        # transaction_type - определяет возврат или продажа
        # quantity - количество товаров
        # product.name - название товара 
        # transaction_date - берёт дату и время и форматирует в год-месяц-день
        # это всё преобразуется в строку и можно смотреть какие транзакции были 


class ProductDetail(models.Model): # детали продукта/описание товара - один товар одно описание
    # попытка сделать 1-1 
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE, # если удалить товар, его детали тоже удалятся
        primary_key=True, # Делаем эту связь первичным ключом для эффективности
        verbose_name="Товар"
    )
    
    country_of_origin = models.CharField(max_length=100, verbose_name="Производитель")
    description = models.TextField(blank=True, verbose_name="Подробное описание")
    
    class Meta:
        verbose_name = "Детали товара"
        verbose_name_plural = "Детали товаров"
        
    def __str__(self):
        return f"Описание для {self.product.name}"