import sys
import pandas as pd
import requests
import openpyxl

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QWidget, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Notes - Test de Niveau")
        self.setGeometry(100, 100, 1200, 800)  # Slightly larger window

        # Initialiser la map des établissements
        self.etablissement_map = {}

        # Style général de l'application (avec quelques améliorations)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #E0F7FA;
            }
            QLabel {
                font-size: 16px;
                font-family: Arial;
            }
            QPushButton {
                background-color: #0288D1;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0277BD;
            }
            QComboBox, QLineEdit {
                padding: 5px;
                font-size: 14px;
                margin: 5px;
            }
            QTableWidget {
                alternate-background-color: #F0F0F0;
            }
        """)

        # Mise en page principale
        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.create_main_menu()

    def create_main_menu(self):
        """Crée le menu principal."""
        self.clear_layout()

        title = QLabel("Gestion des Notes")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        buttons = [
            ("Importer la liste des élèves", self.show_import_menu),
            ("Saisie des notes", self.show_saisie_menu),
            ("Modifier les notes", self.show_modif_menu)
        ]

        for label, connect_func in buttons:
            btn = QPushButton(label)
            btn.clicked.connect(connect_func)
            self.main_layout.addWidget(btn)

    def clear_layout(self):
        """Efface tous les widgets du layout principal."""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_import_menu(self):
        """Menu d'importation des élèves."""
        self.clear_layout()

        title = QLabel("Importer un fichier Excel")
        self.main_layout.addWidget(title)

        import_btn = QPushButton("Choisir un fichier Excel")
        import_btn.clicked.connect(self.import_excel)
        self.main_layout.addWidget(import_btn)

        # Status Label
        self.status_label = QLabel()
        self.main_layout.addWidget(self.status_label)

        # Retour au menu principal
        back_btn = QPushButton("Retour au menu principal")
        back_btn.clicked.connect(self.create_main_menu)
        self.main_layout.addWidget(back_btn)

    def import_excel(self):
        """Importer un fichier Excel d'élèves."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Importer un fichier Excel", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    response = requests.post("http://127.0.0.1:8000/api/import_data/", files={"file": f})
                
                if response.status_code == 200:
                    self.status_label.setText("Importation réussie !")
                    QMessageBox.information(self, "Succès", "Les élèves ont été importés avec succès.")
                else:
                    error_msg = response.json().get('error', 'Erreur inconnue')
                    self.status_label.setText(f"Erreur : {error_msg}")
                    QMessageBox.warning(self, "Erreur", error_msg)
            
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Erreur de connexion", str(e))

    def show_saisie_menu(self):
        """Menu de saisie des notes."""
        self.clear_layout()

        # Titre
        title = QLabel("Saisie des notes")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        self.main_layout.addWidget(title)

        # Établissement
        etab_layout = QHBoxLayout()
        etab_label = QLabel("Établissement :")
        self.input_etablissement = QComboBox()
        etab_layout.addWidget(etab_label)
        etab_layout.addWidget(self.input_etablissement)
        self.main_layout.addLayout(etab_layout)

        # Classe
        classe_layout = QHBoxLayout()
        classe_label = QLabel("Classe :")
        self.input_classe = QComboBox()
        classe_layout.addWidget(classe_label)
        classe_layout.addWidget(self.input_classe)
        self.main_layout.addLayout(classe_layout)

        # Bouton de chargement
        load_btn = QPushButton("Charger les élèves")
        load_btn.clicked.connect(self.load_students)
        self.main_layout.addWidget(load_btn)

        # Table pour les notes
        self.table = QTableWidget()
        self.main_layout.addWidget(self.table)

        # Bouton d'enregistrement
        save_btn = QPushButton("Enregistrer les notes")
        save_btn.clicked.connect(self.save_notes)
        self.main_layout.addWidget(save_btn)

        # Bouton de retour
        back_btn = QPushButton("Retour au menu principal")
        back_btn.clicked.connect(self.create_main_menu)
        self.main_layout.addWidget(back_btn)

        # Charger les établissements
        self.load_etablissements()

        # Connecter les signaux
        self.input_etablissement.currentIndexChanged.connect(self.load_classes)



    def load_etablissements(self):
        """Charger la liste des établissements."""
        try:
            response = requests.get("http://127.0.0.1:8000/api/etablissements/")
            if response.status_code == 200:
                etablissements = response.json()
                self.input_etablissement.clear()
                self.etablissement_map = {etab['name']: etab['id'] for etab in etablissements}
                self.input_etablissement.addItems(self.etablissement_map.keys())
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de charger les établissements.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erreur de connexion", str(e))
        

    def load_classes(self):
            
            """Charger les classes pour l'établissement sélectionné."""
            etablissement_name = self.input_etablissement.currentText()
            etablissement_id = self.etablissement_map.get(etablissement_name)

            if etablissement_id:
                try:
                    response = requests.get(f"http://127.0.0.1:8000/api/classes/?etablissement={etablissement_id}")
                    if response.status_code == 200:
                        classes = response.json()
                        self.input_classe.clear()
                        self.input_classe.addItems(classes)
                    else:
                        QMessageBox.warning(self, "Erreur", "Impossible de charger les classes.")
                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self, "Erreur de connexion", str(e))

    def load_students(self):
        """Charger les élèves pour la classe sélectionnée."""
        etablissement_name = self.input_etablissement.currentText()
        etablissement_id = self.etablissement_map.get(etablissement_name)
        classe = self.input_classe.currentText()

        if not classe or not etablissement_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un établissement et une classe.")
            return

        try:
            response = requests.get(f"http://127.0.0.1:8000/api/students/?etablissement={etablissement_id}&classe={classe}")
            if response.status_code == 200:
                students = response.json()
                
                # Configurer la table
                self.table.setRowCount(len(students))
                self.table.setColumnCount(5)
                headers = ["Matricule", "Nom", "Prénoms", "Note Français", "Note Mathématiques"]
                self.table.setHorizontalHeaderLabels(headers)

                for row_idx, student in enumerate(students):
                    # Remplir les informations de base de l'élève
                    self.table.setItem(row_idx, 0, QTableWidgetItem(student['matricule']))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(student['nom']))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(student['prenoms']))

                    # Colonnes modifiables pour les notes
                    french_note_item = QTableWidgetItem(str(student['note_francais']) if student['note_francais'] is not None else '')
                    math_note_item = QTableWidgetItem(str(student['note_mathematiques']) if student['note_mathematiques'] is not None else '')
                    
                    self.table.setItem(row_idx, 3, french_note_item)
                    self.table.setItem(row_idx, 4, math_note_item)

            else:
                QMessageBox.warning(self, "Erreur", "Impossible de charger les élèves.")
        
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erreur de connexion", str(e))

    def save_notes(self):
        """Enregistrer les notes saisies."""
        notes_data = []
        for row in range(self.table.rowCount()):
            matricule = self.table.item(row, 0).text()
            
            # Récupérer les notes Français et Mathématiques
            note_francais = self.table.item(row, 3).text()
            note_mathematiques = self.table.item(row, 4).text()

            # Préparer les données de notes
            student_notes = {}
            if note_francais:
                try:
                    student_notes['Français'] = float(note_francais)
                except ValueError:
                    QMessageBox.warning(self, "Erreur", f"Note Français invalide pour {matricule}")
                    return

            if note_mathematiques:
                try:
                    student_notes['Mathématiques'] = float(note_mathematiques)
                except ValueError:
                    QMessageBox.warning(self, "Erreur", f"Note Mathématiques invalide pour {matricule}")
                    return

            # N'ajouter que si au moins une note est présente
            if student_notes:
                notes_data.append({
                    "matricule": matricule,
                    "notes": student_notes
                })

        # Envoyer les notes au backend
        try:
            response = requests.post("http://127.0.0.1:8000/api/save_notes/", json={"notes": notes_data})
            if response.status_code == 201:
                QMessageBox.information(self, "Succès", "Notes enregistrées avec succès !")
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                QMessageBox.warning(self, "Erreur", error_msg)
        
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erreur de connexion", str(e))

    def show_modif_menu(self):
        """Menu de modification des notes."""
        self.clear_layout()

        # Titre
        title = QLabel("Modifier les notes")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        self.main_layout.addWidget(title)

        # Établissement
        etab_layout = QHBoxLayout()
        etab_label = QLabel("Établissement :")
        self.input_etablissement = QComboBox()
        etab_layout.addWidget(etab_label)
        etab_layout.addWidget(self.input_etablissement)
        self.main_layout.addLayout(etab_layout)

        # Classe
        classe_layout = QHBoxLayout()
        classe_label = QLabel("Classe :")
        self.input_classe = QComboBox()
        classe_layout.addWidget(classe_label)
        classe_layout.addWidget(self.input_classe)
        self.main_layout.addLayout(classe_layout)

        # Bouton de chargement
        load_btn = QPushButton("Charger les notes")
        load_btn.clicked.connect(self.load_students)  # Réutiliser la même méthode que pour la saisie
        self.main_layout.addWidget(load_btn)

        # Table pour les notes
        self.table = QTableWidget()
        self.main_layout.addWidget(self.table)

        # Bouton d'enregistrement des modifications
        save_btn = QPushButton("Enregistrer les modifications")
        save_btn.clicked.connect(self.save_notes)
        self.main_layout.addWidget(save_btn)

        # Bouton de retour
        back_btn = QPushButton("Retour au menu principal")
        back_btn.clicked.connect(self.create_main_menu)
        self.main_layout.addWidget(back_btn)

        # Charger les établissements
        self.load_etablissements()

        # Connecter les signaux
        self.input_etablissement.currentIndexChanged.connect(self.load_classes)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()