from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel


class SubtitleListView:
    def __init__(self, sublistview: QtWidgets.QListView, loadbutton: QtWidgets.QPushButton):
        self.sublistview = sublistview
        self.loadbutton = loadbutton
        self.sublist_model = QStandardItemModel()
        self.sublistview.setModel(self.sublist_model)
        self.sublistview.selectionModel().selectionChanged.connect(self.sub_list_select_changed)

    def sub_list_select_changed(self):
        curentindex = self.sublistview.currentIndex()
        curentindex: QModelIndex
        data: str = curentindex.data(Qt.DisplayRole)
        subtitle_uri = data.split("===")[1].strip()

        # self.curvidMask: VideoMask
        # self.curvidMask.set_subtitle_uri(subtitle_uri)
        print('subtitle list {}'.format(subtitle_uri))
        pass
        pass
