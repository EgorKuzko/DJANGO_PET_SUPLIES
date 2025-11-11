from django.views.generic import ListView, TemplateView # для отоброжения списков и шаблонов
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # проверка на авторизацию + отдельная проверка для админа
from django.shortcuts import redirect, render # отпровляет на домашнюю страницу +  для заполнения форм
from django.db.models import Sum, Q, F # сумма + фильтрация с условиями
from django.urls import reverse
from django.http import HttpResponseRedirect # возврощяет после внесения данных
from django.contrib.auth.decorators import login_required # защищает функции 
from django.db import transaction as db_transaction  # для БД

from .models import Product, Transaction # достсуп к БД - для новых записей
from .forms import TransactionForm # для создания форм
# Create your views here.


# сотрудник
class EmployeeProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'zooinfo/employee_product_list.html' 
    context_object_name = 'product_list'
    paginate_by = 10 # разбавает на страницы по 10 шт
    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by('category__name', 'name') # проверяет что товары есть в наличии и сортирует их


# руководитель / админ

class ManagerRequiredMixin(UserPassesTestMixin): # проверяет что зашёл админ если - нет то кидает на страницу сотрудника
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('employee_home')


class ManagerFinancialView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'zooinfo/financial_report.html' 

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) # собирает переменные и передаёт в шаблон 
        
        report_data = Transaction.objects.aggregate( # запрос к БД что бы посчитать сколько всего - общая сумма продаж + сумма возвратов + фильтр
            total_sales_sum=Sum(F('total_amount'), filter=Q(transaction_type='SALE')),
            total_returns_sum=Sum(F('total_amount'), filter=Q(transaction_type='RETURN')),
            total_items_sold=Sum(F('quantity'), filter=Q(transaction_type='SALE'))
        )
        product_data = Product.objects.aggregate( # сколько осталось товара + сколько товаров на акции
            total_stock=Sum('stock_quantity'),
            on_sale_count=Sum(1, filter=Q(is_on_sale=True, is_active=True))
        )
        net_sales = (report_data['total_sales_sum'] or 0) - (report_data['total_returns_sum'] or 0)
        
        context.update({ #        !!!  WARNING !!! 
            'total_sales_sum': round(report_data['total_sales_sum'] or 0, 2), # общая сумма продаж + копеки
            'total_returns_sum': round(report_data['total_returns_sum'] or 0, 2), # возвраты + копейки
            'net_sales': round(net_sales, 2), # чистая прибыль
            'total_items_sold': report_data['total_items_sold'] or 0, # сколько продано товара
            'total_stock': product_data['total_stock'] or 0, # сколько осталось на складе
            'on_sale_count': product_data['on_sale_count'] or 0 # сколько товаров на акции
        })
        return context 


# формы для транзакций
@login_required 
def register_transaction(request): # проверка на регистрацию
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)

        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            transaction_type = form.cleaned_data['transaction_type']

            try:
                with db_transaction.atomic():  
                    total_amount = product.price * quantity 
                    
                    if transaction_type == 'SALE':
                        if product.stock_quantity < quantity:
                            raise Exception("Товар закончился")
                        product.stock_quantity -= quantity
                    
                    elif transaction_type == 'RETURN': # если возврат то добовляет на склад
                        product.stock_quantity += quantity
                        
                    product.save() 
                    
                    Transaction.objects.create(
                        product=product,
                        quantity=quantity,
                        transaction_type=transaction_type,
                        total_amount=total_amount 
                    )
                
                return HttpResponseRedirect(reverse('employee_home')) 

            except Exception as e: # если недостаточно товара и отоброжает это
                form.add_error(None, str(e))
                pass 

    else:
        form = TransactionForm()
    
    context = {'form': form, 'title': 'Регистрация Транзакции'}
    return render(request, 'zooinfo/transaction_form.html', context=context)