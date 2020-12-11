from django.urls import path
from . import views

urlpatterns = [
    path('add', views.add_note),
    path('all', views.list_view, name="all"),
    path('mod/<int:n_id>', views.mod_view),
    path('<int:n_id>', views.show_view),
    path('del/<int:n_id>', views.del_view)
]
