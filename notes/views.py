#from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import College, Class, Student, Note
import json

"""

@csrf_exempt
def import_data(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]

        # Charger le fichier Excel dans un DataFrame
        data = pd.read_excel(file)

        # Validation des colonnes attendues
        expected_columns = ["Matricule", "Nom", "Prénoms", "Sexe", "Date", "Lieu", "Etablissement", "Classe", "Contact" ]
        if not all(column in data.columns for column in expected_columns):
            return JsonResponse({"error": "Fichier Excel invalide. Vérifiez les colonnes attendues."}, status=400)

        # Réinitialiser les données existantes
        Student.objects.all().delete()
        Class.objects.all().delete()
        College.objects.all().delete()

        # Création des établissements, classes et élèves
        for _, row in data.iterrows():
            # Récupérer ou créer l'établissement
            college, _ = College.objects.get_or_create(
                name=row["Etablissement"]
            )

            # Récupérer ou créer la classe
            classe, _ = Class.objects.get_or_create(
                name=row["Classe"],
                college=college
            )

            # Créer l'élève
            Student.objects.create(
                matricule=row["Matricule"],
                name=row["Nom"],
                prenoms=row["Prénoms"],
                classe=classe,
                college=college
            )

        return JsonResponse({"message": "Importation réussie !"}, status=200)

    return JsonResponse({"error": "Aucun fichier fourni."}, status=400)


@csrf_exempt
def save_grade(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            student = Student.objects.get(matricule=data["matricule"])
            Note.objects.update_or_create(
                student=student,
                subject=data["subject"],
                defaults={"grade": data["grade"]}
            )
            return JsonResponse({"message": "Note enregistrée avec succès !"}, status=201)
        except Student.DoesNotExist:
            return JsonResponse({"error": "Élève introuvable."}, status=404)
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)


# Affichage de la liste des établissements dans le menu saisie de notes
def get_etablissements(request):
    if request.method == "GET":
        colleges = College.objects.all().values("id", "name")
        return JsonResponse(list(colleges), safe=False)
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)


# Affichage de la liste des classes dans le menu saisie de notes
def get_students(request):
    if request.method == "GET":
        etablissement_id = request.GET.get("etablissement")
        classe = request.GET.get("classe")

        if not etablissement_id or not classe:
            return JsonResponse({"error": "Paramètres manquants."}, status=400)

        students = Student.objects.filter(
            college_id=etablissement_id, class_level=classe
        ).values("matricule", "name")

        return JsonResponse(list(students), safe=False)
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)

"""


@csrf_exempt
@csrf_exempt
def import_data(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]

        # Charger le fichier Excel dans un DataFrame
        try:
            data = pd.read_excel(file)

            # Validation des colonnes attendues
            expected_columns = ["Matricule", "Nom", "Prénoms", "Sexe", "Date", "Lieu", "Etablissement", "Classe", "Contact"]
            if not all(column in data.columns for column in expected_columns):
                return JsonResponse({"error": "Fichier Excel invalide. Vérifiez les colonnes attendues."}, status=400)

            # Transaction atomique pour éviter les problèmes de cohérence
            from django.db import transaction
            with transaction.atomic():
                # Création des établissements, classes et élèves sans supprimer les existants
                for _, row in data.iterrows():
                    # Récupérer ou créer l'établissement
                    college, _ = College.objects.get_or_create(
                        name=row["Etablissement"],
                        defaults={'address': ''}  # Ajouter une valeur par défaut si nécessaire
                    )

                    # Récupérer ou créer la classe
                    classe, _ = Class.objects.get_or_create(
                        name=row["Classe"],
                        college=college
                    )

                    # Créer l'élève, en s'assurant qu'il n'existe pas déjà
                    Student.objects.get_or_create(
                        matricule=row["Matricule"],
                        defaults={
                            'name': row["Nom"],
                            'prenoms': row["Prénoms"],
                            'classe': classe,
                            'college': college
                        }
                    )

            return JsonResponse({"message": "Importation réussie !"}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Erreur lors de l'importation : {str(e)}"}, status=500)

    return JsonResponse({"error": "Aucun fichier fourni."}, status=400)


@csrf_exempt
def save_notes(request):
    """Permet d'enregistrer les notes pour plusieurs élèves."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            notes_data = data.get('notes', [])
            
            for note_entry in notes_data:
                matricule = note_entry.get('matricule')
                student_notes = note_entry.get('notes', {})
                
                try:
                    student = Student.objects.get(matricule=matricule)
                    
                    # Enregistrer les notes de Français
                    if student_notes.get('Français'):
                        Note.objects.update_or_create(
                            student=student,
                            subject='Français',
                            defaults={'grade': float(student_notes['Français'])}
                        )
                    
                    # Enregistrer les notes de Mathématiques
                    if student_notes.get('Mathématiques'):
                        Note.objects.update_or_create(
                            student=student,
                            subject='Mathématiques',
                            defaults={'grade': float(student_notes['Mathématiques'])}
                        )
                
                except Student.DoesNotExist:
                    return JsonResponse({"error": f"Élève avec matricule {matricule} introuvable."}, status=404)
                except ValueError:
                    return JsonResponse({"error": f"Notes invalides pour {matricule}."}, status=400)
            
            return JsonResponse({"message": "Notes enregistrées avec succès !"}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Données JSON invalides."}, status=400)
    
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)

def get_etablissements(request):
    """Retourne la liste des établissements avec leur ID."""
    if request.method == "GET":
        colleges = [
            {"id": college.id, "name": college.name} 
            for college in College.objects.all()
        ]
        return JsonResponse(colleges, safe=False)
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)

def get_classes(request):
    """Retourne la liste des classes pour un établissement donné."""
    if request.method == "GET":
        etablissement_id = request.GET.get("etablissement")
        
        if not etablissement_id:
            return JsonResponse({"error": "ID d'établissement manquant."}, status=400)
        
        try:
            # Trouver l'établissement par ID
            college = College.objects.get(id=etablissement_id)
            # Récupérer les classes associées à cet établissement
            classes = list(college.classes.values_list('name', flat=True))
            return JsonResponse(classes, safe=False)
        
        except College.DoesNotExist:
            return JsonResponse({"error": "Établissement non trouvé."}, status=404)
    
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)

def get_students(request):
    """Retourne la liste des élèves pour un établissement et une classe donnés."""
    if request.method == "GET":
        etablissement_id = request.GET.get("etablissement")
        classe_name = request.GET.get("classe")

        if not etablissement_id or not classe_name:
            return JsonResponse({"error": "Paramètres manquants."}, status=400)

        try:
            students = Student.objects.filter(
                college_id=etablissement_id, 
                classe__name=classe_name
            )
            
            # Récupérer les notes existantes pour chaque élève
            student_data = []
            for student in students:
                student_info = {
                    'matricule': student.matricule,
                    'nom': student.name,
                    'prenoms': student.prenoms,
                }
                
                # Récupérer les notes existantes
                french_note = student.notes.filter(subject='Français').first()
                math_note = student.notes.filter(subject='Mathématiques').first()
                
                student_info['note_francais'] = french_note.grade if french_note else None
                student_info['note_mathematiques'] = math_note.grade if math_note else None
                
                student_data.append(student_info)
            
            return JsonResponse(student_data, safe=False)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)