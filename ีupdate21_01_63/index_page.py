from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL.ImageQt import ImageQt
import sys,image_create,export_file,file_database,time

class Button(QPushButton):

    def __init__(self,parent,text):
        super().__init__(parent)
        self.text = text
        
    
class TreeView(QTreeView): #update

    def __init__(self,parent):
        super().__init__(parent)
        super().setHeaderHidden(True)
        self.set_structure()

    def set_structure(self):

        self.data_all = []
        self.tree_view = super()

        self.tree_model = QStandardItemModel()
        self.root_node = self.tree_model.invisibleRootItem()

        self.tree_view.setModel(self.tree_model)
        self.tree_view.expandAll()

    def add_item(self,item):
        title = Item(item[0])
        author = Item("Author : "+item[1])
        file_name = Item("File : "+item[2])
        title.appendRow(author)
        title.appendRow(file_name)
        self.root_node.appendRow(title)
        self.data_all.append(item)

    def clear(self):
        self.tree_model.clear()
        self.data_all = []
        self.set_structure()




class Item(QStandardItem):

    def __init__(self,text = "",color = QColor(Qt.black),fontSize = 20):
        super().__init__()
        font = QFont("Times New Roman",fontSize)
        self.setEditable(False)
        self.setFont(font)
        self.setText(text)

class Header :

    def __init__(self,user_name):
        self.user_image = ImageQt(image_create.user_image(user_name,"darkblue"))

class AutoDetect(QThread):

    signal = pyqtSignal()

    def __init__(self):
        super().__init__()       
    def run(self):
        while True :
            self.signal.emit()
            time.sleep(1)
            

    
class PublicPage(QWidget):

    switch_window = pyqtSignal()

    def __init__(self,user_name):
        self.my_database = file_database.File_database()
        super().__init__()
        self.user_name = user_name
        self.type_widget = "public"
        self.search_name = None
        self.run_out = True
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File transfer system")
        self.center()
        self.set_gui()
        
        

    def center(self):
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def set_gui(self):

        self.line = 0

        content_button = ["Public", "Inbox", "Send", "Export", "Import","Log out"]
        self.global_object = []
        self.header_image = self.image(Header(self.user_name).user_image)
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.header_image)

        self.main_zone = QGridLayout()
        for num in range(len(content_button)):
            item = Button(self,content_button[num])
            item.setStyleSheet("background-color : rgb(0,255,0);")
            item.setText(item.text)
            if item.text == "Log out" :
                self.global_object.append(item)
            self.check_item(item)
            self.main_zone.addWidget(item,num*2,0,2,2)
            self.line += num

        self.treeView = TreeView(self) #update
        self.main_zone.addWidget(self.treeView,0,3,2*len(content_button),2*len(content_button))
        
        find_label = QLabel()
        find_label.setText("find : ")
        find_label.setAlignment(Qt.AlignCenter)
        self.search_lineedit = QLineEdit(self) # update
        self.main_zone.addWidget(find_label,self.line+1,0,2,2)
        self.main_zone.addWidget(self.search_lineedit,self.line+1,3,2,2*(len(content_button)-1))

        self.search_button_function_name = ["----->","Reset"]
        
        for num in range(len(self.search_button_function_name)):
            item = Button(self,self.search_button_function_name[num])
            item.setStyleSheet("background-color : rgb(0,255,100);")
            item.setText(item.text)
            self.check_item(item)
            self.main_zone.addWidget(item,self.line+1,3+2*(len(content_button)-1)+num,1,1)
        
        
        self.vertical_layout.addLayout(self.main_zone)
        self.setLayout(self.vertical_layout)
        
        self.background_thread = AutoDetect()
        self.background_thread.signal.connect(self.update_treeview)
        
        self.background_thread.start()

        print("Start")

    

    def image(self,picture):
        self.new_image = QLabel("",self)
        new_image = QPixmap.fromImage(picture)
        self.new_image.setPixmap(new_image.scaled(new_image.width()//2,new_image.height()//2))
        self.new_image.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        self.new_image.setAlignment(Qt.AlignCenter)
        return self.new_image

    def check_item(self,item):
        if item.text == "Export" :
            item.clicked.connect(self.export)
        elif item.text == "Log out":
            item.clicked.connect(self.logout)
        elif item.text == "Public":
            item.clicked.connect(self.public_active)
        elif item.text == "Inbox" :
            item.clicked.connect(self.inbox_active)
        elif item.text == "Send" :
            item.clicked.connect(self.send_history_active)
        elif item.text == "----->" :
            item.clicked.connect(self.set_search_text)
        else :
            item.clicked.connect(self.reset_search_text)

    def export(self):
        self.dialog = export_file.ExportForm(self.user_name)
        self.dialog.my_database = self.my_database

    def public_active(self):
        self.type_widget = "public"
        self.search_name = None
        self.treeView.clear()
        self.search_lineedit.clear()

    def inbox_active(self):
        self.type_widget = "inbox"
        self.search_name = None
        self.treeView.clear()
        self.search_lineedit.clear()

    def send_history_active(self):
        self.type_widget = "send"
        self.search_name = None
        self.treeView.clear()
        self.search_lineedit.clear()

    def set_search_text(self):
        self.search_name = self.search_lineedit.text()

    def reset_search_text(self):
        self.search_name = None
        self.search_lineedit.clear()

    def update_treeview(self):
        if self.type_widget == "public" :
            self.fetch_data = self.my_database.get_public(self.search_name)
        elif self.type_widget == "inbox" :
            self.fetch_data = self.my_database.get_inbox(self.search_name)
        else : 
            self.fetch_data = self.my_database.get_send_history(self.search_name)
        print(self.fetch_data)

        if len(self.treeView.data_all) != len(self.fetch_data) :
            if len(self.fetch_data) > len(self.treeView.data_all) :
                for item in self.fetch_data :
                    if item not in self.treeView.data_all :
                        self.treeView.add_item(item)
            else:
                self.treeView.clear()
                for item in self.fetch_data :
                    self.treeView.add_item(item)

        

        

    def logout(self):
        self.run_out = False
        self.switch_window.emit()
        print("LogOut Complete")

    def closeEvent(self,event):

        if self.run_out :
            sys.exit()

    
        
    
