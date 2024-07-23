from django.urls import path
from Media_App import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('Records_Management', views.Records_Management, name='Records_Management'),
    path('Query_Results', views.Query_Results, name='Query_Results'),
    path('Rankings', views.Rankings, name='Rankings'),
    path('return_a_order', views.return_a_order, name='return_a_order'),
    path('top_3', views.top_3, name='top_3'),

]