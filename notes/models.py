from django.db import models

class College(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)  # Make address optional

    def __str__(self):
        return self.name

    def get_classes(self):
        return self.classes.all().values_list('name', flat=True)



class Class(models.Model):
    name = models.CharField(max_length=50)  # Exemple : "6A", "6B", etc.
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="classes")

    def __str__(self):
        return f"{self.name} ({self.college.name})"


class Student(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    classe = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="students")
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} {self.prenoms} ({self.matricule})"


class Note(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    subject = models.CharField(max_length=50, choices=[('Français', 'Français'), ('Mathématiques', 'Mathématiques')])
    grade = models.FloatField()

    def __str__(self):
        return f"{self.student.name} - {self.subject}: {self.grade}"