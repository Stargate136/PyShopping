import logging

from PySide2 import QtWidgets, QtGui

LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.DEBUG)


class AddToShoppingListDialog(QtWidgets.QDialog):
    """Custom Dialog for add recipe to shopping list"""
    def __init__(self, recipe_name):
        super().__init__()

        self.recipe_name = recipe_name
        self.setWindowTitle(f"Ajouter {self.recipe_name}")

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
        self.lbl_title = QtWidgets.QLabel(f"Ajouter {self.recipe_name} a la liste de courses")

        # Quantity
        self.lbl_quantity = QtWidgets.QLabel("Pour combien de personnes ?")
        self.le_quantity = QtWidgets.QLineEdit()

        # Add / Cancel
        self.btn_add = QtWidgets.QPushButton("Ajouter")
        self.btn_cancel = QtWidgets.QPushButton("Annuler")

    def create_layout(self):
        LOGGER.debug("create_layout()")

        self.layout = QtWidgets.QGridLayout(self)

    def modify_widgets(self):
        LOGGER.debug("modify_widgets()")

        # Int Validator for le_quantity
        validator = QtGui.QIntValidator()
        self.le_quantity.setValidator(validator)

        # Disable add button initially
        self.btn_add.setEnabled(False)

    def add_widgets_to_layouts(self):
        LOGGER.debug("add_widgets_to_layouts()")

        # Title
        self.layout.addWidget(self.lbl_title, 0, 0, 1, 2)  # widget, row, col, rowSpan, colSpan

        # Quantity
        self.layout.addWidget(self.lbl_quantity, 1, 0)
        self.layout.addWidget(self.le_quantity, 1, 1)

        # Add / Cancel
        self.layout.addWidget(self.btn_add, 2, 0)
        self.layout.addWidget(self.btn_cancel, 2, 1)

    def setup_connections(self):
        LOGGER.debug("setup_connections()")

        # Add / Cancel
        self.btn_add.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        # Quantity text changed
        self.le_quantity.textChanged.connect(self.check_inputs_filled)

    # SLOTS

    def accept(self):
        LOGGER.debug("btn_add clicked")

        self.quantity = int(self.le_quantity.text())

        super().accept()

    def reject(self):
        LOGGER.debug("btn_cancel clicked")

        super().reject()

    def check_inputs_filled(self):
        LOGGER.debug("le_quantity text changed")

        inputs_filled = bool(self.le_quantity.text())
        self.btn_add.setEnabled(inputs_filled)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    win = AddToShoppingListDialog("test")

    win.show()
    app.exec_()
