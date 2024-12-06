from django.contrib import admin

from .models import College, Class, Student, Note

admin.site.register(College)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Note)
