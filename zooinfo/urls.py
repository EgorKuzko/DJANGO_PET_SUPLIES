
from django.urls import path 
from . import views # импортирует всё что есть в views

urlpatterns = [
    # cтраница руководителя
    path('manager/report/', views.ManagerFinancialView.as_view(), name='manager_report'), # для сбора статистики
    
    # Новый путь для формы транзакций
    path('transaction/register/', views.register_transaction, name='register_transaction'), # для точных действий - расчёт суммы и транзакции
    
    # cтраница сотрудника 
    path('', views.EmployeeProductListView.as_view(), name='employee_home'), # для отоброжения списков
]