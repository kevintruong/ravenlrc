from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from publisher.facebook.account import *


class FacebookListView:

    def __init__(self, ytlistview: QtWidgets.QListView):
        self.fblistview = ytlistview
        self.model = QStandardItemModel()
        self.fblistview.setModel(self.model)
        self.fblistview.selectionModel().selectionChanged.connect(self.fbpage_select_changed)
        self.cur_page_name = None

    def fbpage_select_changed(self):
        curentindex = self.fblistview.currentIndex()
        curentindex: QModelIndex
        data: str = curentindex.data(Qt.DisplayRole)
        self.cur_page_name = data
        print('audio list {}'.format(data))

    def display_all(self):
        listchannel = FbPageInfoDb().list_all_page_info()
        self.model.clear()
        if listchannel:
            for each_channel in listchannel:
                each_channel: PageInfo
                channel_name = str(each_channel.page_name)
                self.model.appendRow(QStandardItem(channel_name))
