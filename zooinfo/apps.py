from django.apps import AppConfig


class ZooinfoConfig(AppConfig): # изначально назвал catalog - изза конфликта имён -  переименовал в zooinfo 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zooinfo'

