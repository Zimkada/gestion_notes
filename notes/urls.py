from django.urls import path
from .views import import_data, save_notes, get_etablissements, get_students, get_classes

urlpatterns = [
    path("import_data/", import_data, name="import_data"),
    path("save_notes/", save_notes, name="save_notes"),
    path("etablissements/", get_etablissements, name="get_etablissements"),
    path("students/", get_students, name="get_students"),
    path("classes/", get_classes, name="get_classes"),
]
