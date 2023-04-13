from PySide2 import QtWidgets, QtGui, QtCore
import logging

from constants import DB_PATH
from api import ShoppingList

logging.basicConfig(level=logging.DEBUG)

""""""
from PySide2 import QtWidgets, QtGui, QtCore
import logging


logging.basicConfig(level=logging.DEBUG)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()


    def setup_ui(self):
        logging.debug("setup_ui()")
        self.create_widgets()
        self.create_layout()
        self.modify_widgets()
        self.add_widgets_to_layouts()
        self.setup_connections()
        logging.debug("END setup_ui")

    def create_widgets(self):
        logging.debug("create_widgets()")
        self.lbl_welcome = QtWidgets.QLabel("Bienvenu sur PyShopping")
        self.lbl_recipes_from_db = QtWidgets.QLabel("Recettes de la base de donnée")
        self.lw_recipes_from_db = QtWidgets.QListWidget()
        self.lbl_recipes_from_shopping_list = QtWidgets.QLabel("Recettes de la base de donnée")
        self.lw_recipes_from_shopping_list = QtWidgets.QListWidget()
        self.btn_add_to_db = QtWidgets.QPushButton("Créer une recette")
        self.btn_add_to_shopping_list = QtWidgets.QPushButton("Ajouter a la liste de courses ")
        self.btn_generate_shopping_list = QtWidgets.QPushButton("Générer la liste de courses")

    def create_layout(self):
        logging.debug("create_layout()")
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout(self.central_widget)

    def modify_widgets(self):
        logging.debug("modify_widgets()")

    def add_widgets_to_layouts(self):
        logging.debug("add_widgets_to_layouts()")
        self.layout.addWidget(self.lbl_welcome, 0, 0, 1, 5)  # Ajouter le label lbl_welcome
        self.layout.addWidget(self.lbl_recipes_from_db, 1, 0, 1, 2)  # Ajouter le label lbl_recipes_from_db
        self.layout.addWidget(self.lbl_recipes_from_shopping_list, 1, 2, 1, 2)  # Ajouter le label lbl_recipes_from_shopping_list
        self.layout.addWidget(self.lw_recipes_from_db, 2, 0, 8, 2)  # Modifier les valeurs des rangées et colonnes selon vos besoins
        self.layout.addWidget(self.lw_recipes_from_shopping_list, 2, 2, 8, 2)  # Modifier les valeurs des rangées et colonnes selon vos besoins
        self.layout.addWidget(self.btn_add_to_db, 10, 0, 2, 1)
        self.layout.addWidget(self.btn_add_to_shopping_list, 10, 1, 1, 1)
        self.layout.addWidget(self.btn_generate_shopping_list, 10, 2, 1, 2)

    def setup_connections(self):
        logging.debug("setup_connections()")
        self.btn_add_to_db.clicked.connect(self.on_btn_add_to_db)
        self.btn_add_to_shopping_list.clicked.connect(self.on_btn_add_to_shopping_list)
        self.btn_generate_shopping_list.clicked.connect(self.on_btn_generate_shopping_list)

    # END SETUP_UI

    def on_btn_add_to_db(self):
        logging.debug("btn_add_to_db clicked")
        dialog = AddRecipeToDbDialog()
        dialog.exec_()

    def on_btn_add_to_shopping_list(self):
        logging.debug("btn_add_to_shopping_list clicked")

    def on_btn_generate_shopping_list(self):
        logging.debug("btn_generate_shopping_list clicked")


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    win = MainWindow()

    win.show()
    app.exec_()
