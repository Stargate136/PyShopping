import logging

from PySide2 import QtWidgets, QtGui

from api import Ingredient
from interface.custom_widgets import CustomListWidget

LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.DEBUG)


class AddIngredientToRecipeDialog(QtWidgets.QDialog):
    """Custom dialog for add ingredient in recipe"""
    def __init__(self, recipe_title):
        super().__init__()

        self.setWindowTitle(recipe_title)
        self.setup_ui()

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
        self.lbl_title = QtWidgets.QLabel("Ajouter un ingredient")

        # Ingredient name
        self.lbl_name = QtWidgets.QLabel("Nom de l'ingrédient :")
        self.le_name = QtWidgets.QLineEdit()

        # Ingredient quantity
        self.lbl_quantity = QtWidgets.QLabel("Quantité :")
        self.le_quantity = QtWidgets.QLineEdit()

        # Ingredient unit
        self.lbl_unit = QtWidgets.QLabel("Unité :")
        self.le_unit = QtWidgets.QLineEdit()

        # Save / Cancel
        self.btn_save = QtWidgets.QPushButton("Ajouter")
        self.btn_cancel = QtWidgets.QPushButton("Annuler")

    def create_layout(self):
        LOGGER.debug("create_layout()")
        self.layout = QtWidgets.QGridLayout(self)

    def modify_widgets(self):
        LOGGER.debug("modify_widgets()")
        # Int Validator for le_quantity
        validator = QtGui.QIntValidator()
        self.le_quantity.setValidator(validator)
        # Disable btn_save initially
        self.btn_save.setEnabled(False)

    def add_widgets_to_layouts(self):
        LOGGER.debug("add_widgets_to_layouts()")

        # Title
        self.layout.addWidget(self.lbl_title, 0, 0, 1, 2)

        # Ingredient name
        self.layout.addWidget(self.lbl_name, 1, 0)
        self.layout.addWidget(self.le_name, 1, 1)

        # Ingredient quantity
        self.layout.addWidget(self.lbl_quantity, 2, 0)
        self.layout.addWidget(self.le_quantity, 2, 1)

        # Ingredient unit
        self.layout.addWidget(self.lbl_unit, 3, 0)
        self.layout.addWidget(self.le_unit, 3, 1)

        # Save / Cancel
        self.layout.addWidget(self.btn_save, 4, 0)
        self.layout.addWidget(self.btn_cancel, 4, 1)

    def setup_connections(self):
        LOGGER.debug("setup_connections()")

        # Check QLineEdit inputs
        self.le_name.textChanged.connect(self.check_all_lineedits_filled)
        self.le_quantity.textChanged.connect(self.check_all_lineedits_filled)
        self.le_unit.textChanged.connect(self.check_all_lineedits_filled)

        # Buttons
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # SLOTS
    def check_all_lineedits_filled(self):
        LOGGER.debug("LineEdit text changed")
        # Check if all QLineEdit inputs are filled
        name_filled = bool(self.le_name.text())
        quantity_filled = bool(self.le_quantity.text())
        unit_filled = bool(self.le_unit.text())

        # Enable/Disable the btn_save button based on the fill state
        self.btn_save.setEnabled(name_filled and quantity_filled and unit_filled)

    def accept(self):
        LOGGER.debug("btn_save clicked")
        self.name = self.le_name.text()
        self.quantity = int(self.le_quantity.text())
        self.unit = self.le_unit.text()

        super().accept()

    def reject(self):
        LOGGER.debug("btn_cancel clicked")
        super().reject()

    # END SLOTS


class AddRecipeToDbDialog(QtWidgets.QDialog):
    """Custom dialog box for add recipe in database"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ajout d'une recette")
        self.setup_ui()

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
        self.lbl_title = QtWidgets.QLabel("Ajouter une recette")

        # Recipe title
        self.lbl_recipe_name = QtWidgets.QLabel("Nom de la recette :")
        self.le_recipe_name = QtWidgets.QLineEdit()

        # Add / Delete ingredient buttons
        self.btn_add_ingredient = QtWidgets.QPushButton("Ajouter un ingrédient")
        self.btn_delete_ingredient = QtWidgets.QPushButton("Supprimer un ingrédient")

        # Ingredients list
        self.lbl_ingredients = QtWidgets.QLabel("Liste des ingrédients")
        self.lw_ingredients = CustomListWidget()

        # Save / Cancel
        self.btn_save_recipe = QtWidgets.QPushButton("Enregistrer")
        self.btn_cancel = QtWidgets.QPushButton("Annuler")

    def create_layout(self):
        LOGGER.debug("create_layout()")
        self.layout = QtWidgets.QGridLayout(self)

    def modify_widgets(self):
        LOGGER.debug("modify_widgets()")
        # Disable btn_save initially
        self.btn_save_recipe.setEnabled(False)

        # Disable btn_add_ingredient initially
        self.btn_add_ingredient.setEnabled(False)

    def add_widgets_to_layouts(self):
        LOGGER.debug("add_widgets_to_layouts()")
        # Title
        self.layout.addWidget(self.lbl_title, 0, 0, 1, 2)

        # Recipe title
        self.layout.addWidget(self.lbl_recipe_name, 1, 0, 1, 1)
        self.layout.addWidget(self.le_recipe_name, 1, 1, 1, 1)

        # Add / Delete ingredient buttons
        self.layout.addWidget(self.btn_add_ingredient, 2, 0, 1, 2)
        self.layout.addWidget(self.btn_delete_ingredient, 3, 0, 1, 2)

        # Ingredients list
        self.layout.addWidget(self.lbl_ingredients, 4, 0, 1, 2)
        self.layout.addWidget(self.lw_ingredients, 5, 0, 1, 2)

        # Save / Cancel buttons
        self.layout.addWidget(self.btn_save_recipe, 6, 0, 1, 1)
        self.layout.addWidget(self.btn_cancel, 6, 1, 1, 1)

    def setup_connections(self):
        LOGGER.debug("setup_connections()")
        self.btn_add_ingredient.clicked.connect(self.on_btn_add_ingredient)
        self.btn_delete_ingredient.clicked.connect(self.on_btn_delete_ingredient)
        self.btn_save_recipe.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        self.le_recipe_name.textChanged.connect(self.check_inputs_filled)
        self.lw_ingredients.count_changed.connect(self.check_inputs_filled)

    # END SETUP_UI

    # SLOTS

    def on_btn_add_ingredient(self):
        LOGGER.debug("btn_add_ingredient clicked")
        recipe_title = self.le_recipe_name.text()
        dialog = AddIngredientToRecipeDialog(recipe_title=recipe_title)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            self.add_ingredient(dialog)

    def on_btn_delete_ingredient(self):
        LOGGER.debug("btn_delete_ingredient clicked")
        item = self.lw_ingredients.currentItem()
        row = self.lw_ingredients.row(item)
        self.lw_ingredients.takeItem(row)

    def accept(self):
        LOGGER.debug("accept emitted")
        self.title = self.le_recipe_name.text()
        self.ingredients = []
        for i in range(self.lw_ingredients.count()):
            self.ingredients.append(self.lw_ingredients.item(i).ingredient)

        super().accept()

    def reject(self):
        LOGGER.debug("reject emitted")
        super().reject()

    def check_inputs_filled(self):
        LOGGER.debug("check_input_filled emmited")
        recipe_name_filled = bool(self.le_recipe_name.text())
        ingredients_filled = self.lw_ingredients.count() > 0

        self.btn_save_recipe.setEnabled(recipe_name_filled and ingredients_filled)
        self.btn_add_ingredient.setEnabled(recipe_name_filled)

    # END SLOTS

    def add_ingredient(self, dialog):
        """Method to add ingredient to the lw_ingredients"""
        name = dialog.name
        quantity = dialog.quantity
        unit = dialog.unit
        ingredient = Ingredient(name=name, quantity=quantity, unit=unit)

        LOGGER.debug(f"Ingredient {ingredient} added")

        item = QtWidgets.QListWidgetItem(str(ingredient))
        item.ingredient = ingredient
        self.lw_ingredients.addItem(item)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    win = AddRecipeToDbDialog()

    win.show()
    app.exec_()
