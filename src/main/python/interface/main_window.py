from PySide2 import QtWidgets, QtCore
import logging

from constants import DB_PATH, TEMP_SHOPPING_LIST_PATH
from api import ShoppingList, RecipesManager

from .custom_widgets import CustomListWidget
from .dialog import AddRecipeToDbDialog, AddToShoppingListDialog, GenerateShoppingListDialog


LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.DEBUG)


class MainWindow(QtWidgets.QMainWindow):
    # Signal emit when database change
    sig_db_changed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.load_db()

    def setup_ui(self):
        LOGGER.debug("setup_ui()")
        self.create_widgets()
        self.create_layout()
        self.modify_widgets()
        self.add_widgets_to_layouts()
        self.setup_connections()
        LOGGER.debug("END setup_ui")

    def create_widgets(self):
        LOGGER.debug("create_widgets()")

        # Title
        self.lbl_welcome = QtWidgets.QLabel("Bienvenu sur PyShopping")

        # Recipes from database
        self.lbl_recipes_from_db = QtWidgets.QLabel("Recettes de la base de donnée")
        self.lw_recipes_from_db = CustomListWidget()

        # Recipes from shopping list
        self.lbl_recipes_from_shopping_list = QtWidgets.QLabel("Recettes de la liste de courses")
        self.lw_recipes_from_shopping_list = CustomListWidget()

        # Buttons
        self.btn_add_to_db = QtWidgets.QPushButton("Créer une recette")
        self.btn_add_to_shopping_list = QtWidgets.QPushButton("Ajouter a la liste de courses ")
        self.btn_delete_from_shopping_list = QtWidgets.QPushButton("Supprimer de la liste de courses")
        self.btn_generate_shopping_list = QtWidgets.QPushButton("Générer la liste de courses")

    def create_layout(self):
        LOGGER.debug("create_layout()")

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QGridLayout(self.central_widget)

    def modify_widgets(self):
        LOGGER.debug("modify_widgets()")

        # Disable btn_add_to_shopping_list and btn generate_shopping_list initially
        self.btn_add_to_shopping_list.setEnabled(False)
        self.btn_generate_shopping_list.setEnabled(False)

    def add_widgets_to_layouts(self):
        LOGGER.debug("add_widgets_to_layouts()")

        # Title
        self.layout.addWidget(self.lbl_welcome, 0, 0, 1, 4)

        # Recipes from database
        self.layout.addWidget(self.lbl_recipes_from_db, 1, 0, 1, 2)
        self.layout.addWidget(self.lw_recipes_from_db, 2, 0, 8, 2)

        # Recipes from shopping list
        self.layout.addWidget(self.lbl_recipes_from_shopping_list, 1, 2, 1, 2)
        self.layout.addWidget(self.lw_recipes_from_shopping_list, 2, 2, 8, 2)

        # Buttons
        self.layout.addWidget(self.btn_add_to_db, 10, 0)
        self.layout.addWidget(self.btn_add_to_shopping_list, 10, 1)
        self.layout.addWidget(self.btn_delete_from_shopping_list, 10, 2)
        self.layout.addWidget(self.btn_generate_shopping_list, 10, 3)

    def setup_connections(self):
        LOGGER.debug("setup_connections()")

        # Buttons
        self.btn_add_to_db.clicked.connect(self.on_btn_add_to_db)
        self.btn_add_to_shopping_list.clicked.connect(self.on_btn_add_to_shopping_list)
        self.btn_delete_from_shopping_list.clicked.connect(self.on_btn_delete_from_shopping_list)
        self.btn_generate_shopping_list.clicked.connect(self.on_btn_generate_shopping_list)

        # ListWidgets changed
        self.lw_recipes_from_db.count_changed.connect(self.check_db_list)
        self.lw_recipes_from_shopping_list.count_changed.connect(self.check_shopping_list)

        # Others events
        self.sig_db_changed.connect(self.update_lists_widgets)
        self.closeEvent = self.on_close_event

    # END SETUP_UI

    # LOAD_DB

    def load_db(self):
        """Method to load database"""
        LOGGER.debug("load_db()")

        self.shopping_list = ShoppingList(DB_PATH)
        self.recipes_manager: RecipesManager = self.shopping_list.recipes_manager
        self.sig_db_changed.emit()

    # SLOTS
    def on_btn_add_to_db(self):
        LOGGER.debug("btn_add_to_db clicked")

        dialog = AddRecipeToDbDialog()
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            title = dialog.title
            ingredients = dialog.ingredients
            LOGGER.debug(f"{title} => {ingredients}")
            self.recipes_manager.add_recipe(title=title, ingredients=ingredients)
            self.sig_db_changed.emit()

    def on_btn_add_to_shopping_list(self):
        LOGGER.debug("btn_add_to_shopping_list clicked")

        selected_item = self.lw_recipes_from_db.currentItem()
        if selected_item:
            recipe = selected_item.recipe
            dialog = AddToShoppingListDialog(recipe["title"])
            result = dialog.exec_()
            if result == QtWidgets.QDialog.Accepted:
                quantity = dialog.quantity
                self.shopping_list.add_recipe_by_id(id=recipe["id"], quantity=quantity)
                self.sig_db_changed.emit()

    def on_btn_delete_from_shopping_list(self):
        LOGGER.debug("btn_delete_from_shopping_list clicked")

        selected_item = self.lw_recipes_from_shopping_list.currentItem()
        if selected_item:
            recipe = selected_item.recipe
            self.shopping_list.delete_recipe_by_id(recipe["id"])
            self.sig_db_changed.emit()

    def on_btn_generate_shopping_list(self):
        LOGGER.debug("btn_generate_shopping_list clicked")

        self.shopping_list.generate(TEMP_SHOPPING_LIST_PATH)
        dialog = GenerateShoppingListDialog()
        result = dialog.exec_()
        if result:
            self.shopping_list.clear()
            self.sig_db_changed.emit()

    def update_lists_widgets(self):
        LOGGER.debug("sig_db_changed emit")
        # Recipes from db
        self.lw_recipes_from_db.clear()
        for recipe in self.recipes_manager.get_all_recipes():
            self.add_item_to_db_list(recipe)

        # Recipes from shopping_list
        self.lw_recipes_from_shopping_list.clear()
        for recipe in self.shopping_list.get_all_recipes():
            self.add_item_to_shopping_list(recipe)

    def check_db_list(self):
        LOGGER.debug("Signal count_changed on lw_recipes_from_db emit")

        db_list_filled = self.lw_recipes_from_db.count() > 0
        self.btn_add_to_shopping_list.setEnabled(db_list_filled)

    def check_shopping_list(self):
        LOGGER.debug("Signal count_changed on lw_recipes_from_shopping_list emit")

        shopping_list_filled = self.lw_recipes_from_shopping_list.count() > 0
        self.btn_generate_shopping_list.setEnabled(shopping_list_filled)

    def on_close_event(self, event):
        LOGGER.debug("Close window")

        reply = QtWidgets.QMessageBox.question(self,
                                               'Confirmation',
                                               'Voulez-vous vraiment quitter ?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.Yes)
        if reply:
            self.shopping_list.close_db()
            LOGGER.debug("Database closed")
            event.accept()
        else:
            event.ignore()

    # END SLOTS

    def add_item_to_db_list(self, recipe):
        item = QtWidgets.QListWidgetItem(recipe['title'])
        item.recipe = recipe
        self.lw_recipes_from_db.addItem(item)

    def add_item_to_shopping_list(self, recipe):
        title = recipe["recipe"]["title"]
        item = QtWidgets.QListWidgetItem(f"{title} ({recipe['quantity']} parts)")
        item.recipe = recipe
        self.lw_recipes_from_shopping_list.addItem(item)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    win = MainWindow()

    win.show()
    app.exec_()
