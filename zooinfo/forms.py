from django import forms
from .models import Transaction, Product



# регистрация - продажи и возвраты
class TransactionForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by('name'),
        label='Товар',
        empty_label='Выберите товар',
    )
    # количество товара
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Количество (шт.)'
    )

    # продажа или возврат
    transaction_type = forms.ChoiceField(
        choices=Transaction.TRANSACTION_TYPES,
        label='Тип операции'
    )

    class Meta: # meta чтобы распределить что заполняет сотрудник а что внутрение формулы 
        # здесь передаются данные из транзакций 
        model = Transaction
        # fields - что бы указать какие данные должны передатся в модельку
        fields = ('product', 'quantity', 'transaction_type',) # здесь перечесляется то что может настраивать сотрудник 