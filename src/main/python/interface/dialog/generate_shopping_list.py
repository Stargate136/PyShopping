import logging

from PySide2 import QtWidgets

from constants import TEMP_SHOPPING_LIST_PATH, USER_DIR

LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.DEBUG)


class GenerateShoppingListDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Liste de courses")

        self.temp_file_path = TEMP_SHOPPING_LIST_PATH

        self.read_temp_file()

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
        self.lbl_title = QtWidgets.QLabel(f"Votre liste de courses")

        # Shopping list
        self.te_shopping_list = QtWidgets.QTextEdit()

        # Save / cancel
        self.btn_save = QtWidgets.QPushButton("Enregistrer")
        self.btn_cancel = QtWidgets.QPushButton("Annuler")

    def create_layout(self):
        LOGGER.debug("create_layout()")

        self.layout = QtWidgets.QGridLayout(self)

    def modify_widgets(self):
        LOGGER.debug("modify_widgets()")

        self.te_shopping_list.setReadOnly(True)
        self.te_shopping_list.setPlainText(self.temp_file_content)

    def add_widgets_to_layouts(self):
        LOGGER.debug("add_widgets_to_layouts()")

        # Title
        self.layout.addWidget(self.lbl_title, 0, 0, 1, 2)

        # Shopping list
        self.layout.addWidget(self.te_shopping_list, 1, 0, 1, 2)

        # Save / cancel
        self.layout.addWidget(self.btn_save, 2, 0)
        self.layout.addWidget(self.btn_cancel, 2, 1)

    def setup_connections(self):
        LOGGER.debug("setup_connections()")

        # Save / Cancel
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    # SLOTS

    def accept(self):
        LOGGER.debug("btn_save clicked")

        save_path = self.ask_user_save_path()
        if save_path:
            self.write_in_file(save_path)

        self.delete_temp_file()

        super().accept()

    def reject(self):
        LOGGER.debug("btn_cancel clicked")

        self.delete_temp_file()

        super().reject()

    # END SETUP_UI

    # FILES MANAGEMENT
    def read_temp_file(self):
        """Method to read temp file and initialize self.temp_file_content with content"""
        with open(self.temp_file_path, 'r') as file:
            self.temp_file_content = file.read()

    @staticmethod
    def delete_temp_file():
        """Method to delete temp file"""
        TEMP_SHOPPING_LIST_PATH.unlink()

    def ask_user_save_path(self):
        """Method to open a FileDialog to save temp content in"""
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setDirectory(str(USER_DIR))
        file_path, _ = file_dialog.getSaveFileName(parent=self,
                                                   caption='Enregistrer la liste de courses',
                                                   filter='Fichiers texte (*.txt)')
        return file_path

    def write_in_file(self, file_path):
        """Method to write temp content in file"""
        with open(file_path, "w") as f:
            f.write(self.temp_file_content)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    win = GenerateShoppingListDialog()
    win.show()
    app.exec_()