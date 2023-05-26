import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QDialog, QVBoxLayout, \
    QLabel, QLineEdit, QCheckBox, QRadioButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


dark_theme_style, light_theme_style = "", "" 


class MyWidget(QWidget):
    # my_ip , my_port, peer_ip, peer_port, SERVER_ADDRESS, SERVER_PORT 

    def __init__(self, register, receive_image,
                receive_doc, get_users_id, get_user_ip, 
                my_ip, my_port, peer_ip, peer_port):
        super().__init__()
        self.init_ui()
        self.register = register
        self.receive_image = receive_image
        self.receive_doc = receive_doc
        self.get_users_id = get_users_id
        self.get_user_ip = get_user_ip 
        self.my_ip = my_ip
        self.my_port = my_port
        self.peer_ip = peer_ip
        self.peer_port = peer_port

    def init_ui(self):
        # Set up the main layout
        layout = QVBoxLayout()

        # Create
        self.username_edit_text = QLineEdit()
        self.username_edit_text.setObjectName("EditText")
        self.username_edit_text.setPlaceholderText("Username")

        # Create the label and register button
        self.label = QLabel()
        self.label.setObjectName("Label")
        register_button = QPushButton("Register")
        register_button.setObjectName("Button")
        register_button.clicked.connect(self._register)

        # Create the list button
        list_button = QPushButton("List")
        list_button.setObjectName("Button")
        list_button.clicked.connect(self.list)

        # Create the dropdown list
        self.dropdown = QComboBox()
        self.dropdown.setObjectName("Dropdown")
        update_button = QPushButton("Update")
        update_button.setObjectName("Button")
        update_button.clicked.connect(self.resolve)

        # Create the download buttons
        download_button = QPushButton("Download")
        download_button.setObjectName("DownloadButton")
        download_button.clicked.connect(self.open_download_dialog)

        # Create the theme toggle checkbox
        self.theme_checkbox = QCheckBox("Dark Theme")
        self.theme_checkbox.setObjectName("ThemeCheckbox")
        self.theme_checkbox.stateChanged.connect(self.toggle_theme)

        # Add the widgets to the layout
        layout.addWidget(self.username_edit_text)
        # layout.addWidget(self.label)
        layout.addWidget(register_button)
        layout.addWidget(list_button)
        layout.addWidget(self.dropdown)
        layout.addWidget(update_button)
        layout.addWidget(download_button)
        layout.addWidget(self.theme_checkbox)

        # Set the layout for the main window
        self.setLayout(layout)
        # Set the fixed size for the main window
        self.setFixedSize(300, 400)

    def _register(self):
        self.register(self.username_edit_text.text(), self.my_ip, str(self.my_port))

    def list(self):
        user_ids = self.get_users_id()
        self.dropdown.clear()
        self.dropdown.addItems(user_ids)

    def resolve(self):
        # Update the dropdown list
        self.peer_ip, self.peer_port = self.get_user_ip(self.dropdown.currentText(),
                                        peer_port=self.peer_port, peer_ip=self.peer_ip)

    def open_download_dialog(self):
        dialog = DownloadDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            source_file = dialog.source_file.text()
            destination_file = dialog.destination_file.text()
            self.download(source_file, destination_file)

    def toggle_theme(self, state):
        if state == Qt.Checked:
            self.setStyleSheet(dark_theme_style)
        else:
            self.setStyleSheet(light_theme_style)


class DownloadDialog(QDialog):
    def __init__(self, parent=None):#, receive_doc, receive_image):
        super().__init__(parent)
        self.setWindowTitle("Download")
        self.parent = parent
        #self.receive_doc = receive_doc
        #self.receive_image = receive_image

        # Create the text inputs
        self.source_file = QLineEdit()
        self.destination_file = QLineEdit()

        # Create the radio buttons
        self.radio_image = QRadioButton("Image")
        self.radio_document = QRadioButton("Document")

        # Create the button
        button = QPushButton("Download")
        button.clicked.connect(self.handle_download)

        # Create the layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Source File:"))
        layout.addWidget(self.source_file)
        layout.addWidget(QLabel("Destination File:"))
        layout.addWidget(self.destination_file)
        layout.addWidget(QLabel("File Type:"))
        layout.addWidget(self.radio_image)
        layout.addWidget(self.radio_document)
        layout.addWidget(button)

        # Set the layout for the popup window
        self.setLayout(layout)

    def handle_download(self):
        source_file = self.source_file.text()
        destination_file = self.destination_file.text()
        if self.radio_image.isChecked():
            print('downloading image')
            self.parent.receive_image(source_file, destination_file, (self.parent.peer_ip, self.parent.peer_port+1))
        else:
            print('downloading document')
            self.parent.receive_doc(source_file, destination_file,
                                (self.parent.peer_ip, self.parent.peer_port+3))
        self.accept()


#def main():
#    global dark_theme_style, light_theme_style 
#    app = QApplication(sys.argv)
#    # Set the font
#    font = QFont("Times", 12, QFont.Bold)
#    app.setFont(font)
#    widget = MyWidget()
#    widget.setStyleSheet(light_theme_style)
#    widget.show()
#    sys.exit(app.exec_())


#if __name__ == "__main__":
#    main()



# Set up the dark and light theme styles
dark_theme_style = """
    QWidget {
        background-color: #2C3E50;
        color: #FFF;
    }
    QLabel#Label {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    QPushButton#Button, QPushButton#DownloadButton {
        padding: 10px;
        font-size: 16px;
        background-color: #3498DB;
        color: #FFF;
        border: none;
    }
    QPushButton#Button:hover, QPushButton#DownloadButton:hover {
        background-color: #58A4D0;
    }
    QComboBox#Dropdown {
        padding: 10px;
        font-size: 16px;
        background-color: #34495E;
        color: #FFF;
        border: none;
    }
    QCheckBox#ThemeCheckbox {
        font-size: 16px;
        color: #FFF;
    }
"""

light_theme_style = """
    QWidget {
        background-color: #ECF0F1;
    }
    QLabel#Label {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    QPushButton#Button, QPushButton#DownloadButton {
        padding: 10px;
        font-size: 16px;
        background-color: #3498DB;
        color: #FFF;
        border: none;
    }
    QPushButton#Button:hover, QPushButton#DownloadButton:hover {
        background-color: #58A4D0;
    }
    QComboBox#Dropdown {
        padding: 10px;
        font-size: 16px;
        background-color: #34495E;
        color: #FFF;
        border: none;
    }
    QCheckBox#ThemeCheckbox {
        font-size: 16px;
        color: #000;
    }
"""

