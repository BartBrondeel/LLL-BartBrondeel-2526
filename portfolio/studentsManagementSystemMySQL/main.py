import sys
import os

from PyQt6.sip import setdeleted
from dotenv import load_dotenv
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QLineEdit, QPushButton, QMainWindow, QTableWidget,
    QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar,
    QStatusBar, QLabel, QGridLayout, QMessageBox
)
import sqlite3
import mysql.connector

load_dotenv()
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")


# ─────────────────────────────────────────────
# DATABASE LAAG
# ─────────────────────────────────────────────

class DatabaseConnection:
    """
    Beheert de verbinding met de MySQL-database.
    Door dit in een aparte klasse te zetten, kan je later makkelijk
    van database wisselen zonder de rest van de code aan te passen.
    Dit heet het Single Responsibility Principle.
    """

    def __init__(self, host=HOST,
                 user=USER,
                 password=PASSWORD,
                 database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        """Geeft een nieuwe databaseverbinding terug."""
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return connection


# ─────────────────────────────────────────────
# HOOFDVENSTER
# ─────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    Het hoofdvenster van de applicatie.
    Bevat de menubalk, toolbar, tabel en statusbalk.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Management System')
        self.setMinimumSize(800, 600)

        self._setup_menu()
        self._setup_table()
        self._setup_toolbar()
        self._setup_statusbar()

    def _setup_menu(self):
        """Maakt de menubalk aan met File, Edit en Help."""
        file_menu = self.menuBar().addMenu("&File")
        help_menu = self.menuBar().addMenu("&Help")
        edit_menu = self.menuBar().addMenu("&Edit")

        # Acties aanmaken
        self.add_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        self.add_action.triggered.connect(self.insert)

        self.search_action = QAction(QIcon("icons/search.png"), "Search", self)
        self.search_action.triggered.connect(self.search)

        about_action = QAction("About", self)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        # Acties toevoegen aan menu's
        file_menu.addAction(self.add_action)
        edit_menu.addAction(self.search_action)
        help_menu.addAction(about_action)

    def _setup_table(self):
        """Maakt de tabel aan en stelt die in als centraal widget."""
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Verbind klikken op een cel met de cell_clicked-methode
        self.table.cellClicked.connect(self.cell_clicked)

    def _setup_toolbar(self):
        """Voegt een verplaatsbare toolbar toe met de belangrijkste acties."""
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.search_action)

    def _setup_statusbar(self):
        """Maakt de statusbalk aan onderaan het venster."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def cell_clicked(self):
        """
        Toont Edit- en Delete-knoppen in de statusbalk wanneer
        de gebruiker op een rij klikt.
        Verwijdert eerst eventuele bestaande knoppen om duplicaten te vermijden.
        """
        # Verwijder bestaande knoppen uit de statusbalk
        # Gebruik findChildren (meervoud!) — findChild geeft maar één widget terug
        for child in self.findChildren(QPushButton):
            self.status_bar.removeWidget(child)

        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        """
        Laadt alle studenten uit de database en vult de tabel.
        Wist eerst de bestaande rijen om dubbele data te vermijden.
        """
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()
        cursor.close()

    def insert(self):
        """Opent het dialoogvenster om een nieuwe student toe te voegen."""
        dialog = InsertDialog(self)
        dialog.exec()

    def search(self):
        """Opent het dialoogvenster om op naam te zoeken."""
        dialog = SearchDialog(self)
        dialog.exec()

    def edit(self):
        """Opent het dialoogvenster om de geselecteerde student te bewerken."""
        dialog = EditDialog(self)
        dialog.exec()

    def delete(self):
        """Opent het dialoogvenster om de geselecteerde student te verwijderen."""
        dialog = DeleteDialog(self)
        dialog.exec()

    def about(self):
        """Toont een informatiedialoog over de applicatie."""
        dialog = AboutDialog()
        dialog.exec()


# ─────────────────────────────────────────────
# DIALOOGVENSTERS
# ─────────────────────────────────────────────

class AboutDialog(QMessageBox):
    """Eenvoudige 'Over'-dialoog met info over de app."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setText(
            "This app was created during the course 'The Python Mega Course'.\n"
            "Feel free to modify and reuse this app."
        )


class BaseDialog(QDialog):
    """
    Abstracte basisklasse voor alle dialogen die toegang nodig hebben
    tot het hoofdvenster.

    Door main_window als parameter mee te geven in plaats van als globale
    variabele te gebruiken, zijn de dialogen los gekoppeld van de rest
    van de app. Dit heet Dependency Injection en maakt de code beter
    testbaar en herbruikbaar.
    """

    # Vaste lijst van beschikbare cursussen — zo staat die maar op één plaats
    COURSES = ["Biology", "Math", "Astronomy", "Physics"]

    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window  # Bewaar referentie naar hoofdvenster


class InsertDialog(BaseDialog):
    """Dialoog om een nieuwe student in te voeren."""

    def __init__(self, main_window: MainWindow):
        super().__init__(main_window)
        self.setWindowTitle("Insert Student Data")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        self.course_name.addItems(self.COURSES)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        """Voegt de ingevulde student toe aan de database."""
        name = self.student_name.text()
        course = self.course_name.currentText()
        mobile = self.mobile.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
            (name, course, mobile)
        )
        connection.commit()
        cursor.close()
        connection.close()

        # Ververs de tabel in het hoofdvenster
        self.main_window.load_data()
        self.close()


class EditDialog(BaseDialog):
    """Dialoog om de gegevens van een bestaande student te wijzigen."""

    def __init__(self, main_window: MainWindow):
        super().__init__(main_window)
        self.setWindowTitle("Update Student Data")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        # Haal de huidige waarden op uit de geselecteerde rij
        index = self.main_window.table.currentRow()
        self.student_id = self.main_window.table.item(index, 0).text()
        student_name = self.main_window.table.item(index, 1).text()
        course_name = self.main_window.table.item(index, 2).text()
        mobile = self.main_window.table.item(index, 3).text()

        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        self.course_name.addItems(self.COURSES)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        """Slaat de gewijzigde gegevens op in de database."""
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
            (self.student_name.text(), self.course_name.currentText(),
             self.mobile.text(), self.student_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

        self.main_window.load_data()
        self.close()


class DeleteDialog(BaseDialog):
    """Dialoog om een student te verwijderen, met bevestigingsvraag."""

    def __init__(self, main_window: MainWindow):
        super().__init__(main_window)
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete this data?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close)  # Sluit het venster bij "No"

    def delete_student(self):
        """Verwijdert de geselecteerde student uit de database."""
        index = self.main_window.table.currentRow()
        student_id = self.main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        self.main_window.load_data()
        self.close()

        # Bevestigingsbericht na verwijdering
        # Opmerking: "Succes" was een typfout in het origineel, nu gecorrigeerd
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText("The record was successfully deleted!")
        msg.exec()


class SearchDialog(BaseDialog):
    """Dialoog om studenten op naam te zoeken en te markeren in de tabel."""

    def __init__(self, main_window: MainWindow):
        super().__init__(main_window)
        self.setWindowTitle("Search Student")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        """
        Zoekt naar de ingevoerde naam in de tabel en selecteert
        de overeenkomende rijen.
        """
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        rows = list(result)
        print(rows)

        # Zoek naar overeenkomsten in de tabel (kolom 1 = naam)
        items = self.main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            self.main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


# ─────────────────────────────────────────────
# APPLICATIE STARTEN
# ─────────────────────────────────────────────

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())