from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from FilmMaker.yt_auth_ui import Ui_Dialog
from publisher.youtube.channel import YoutubeChannelHandler, YtChannelDb, ChannelInfo


class YoutubeListView:
    def __init__(self, ytlistview: QtWidgets.QListView):
        self.ytlistview = ytlistview
        self.model = QStandardItemModel()
        self.ytlistview.setModel(self.model)
        self.ytlistview.selectionModel().selectionChanged.connect(self.yt_pages_select_changed)
        self.cur_channel_name = None

    def display_all_channel(self):
        listchannel = YtChannelDb().list_all_page_info()
        self.model.clear()
        if listchannel:
            for each_channel in listchannel:
                each_channel: ChannelInfo
                channel_name = str(each_channel.channel)
                self.model.appendRow(QStandardItem(channel_name))

    def yt_pages_select_changed(self):
        curentindex = self.ytlistview.currentIndex()
        curentindex: QModelIndex
        data: str = curentindex.data(Qt.DisplayRole)
        self.cur_channel_name = data
        print('audio list {}'.format(data))
        pass


class YoutubeDiaLog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.button_ok.pressed.connect(self.ok_to_add_acc)
        self.button_cancel.pressed.connect(self.cancel_add_acc)
        self.button_verify.pressed.connect(self.verify_yt_channel)
        self.wait_token = QWaitCondition()
        self.mutex = QMutex()

    def youtube_authenticate(self, link):
        print(link)
        token = input('input self token')
        return token

    def verify_yt_channel(self):
        YoutubeChannelHandler().add_new_channel(self.youtube_authenticate)
        self.wait_token.wakeAll()

    def ok_to_add_acc(self):
        self.accept()

    def cancel_add_acc(self):
        self.reject()


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Film Recap Maker")
    app.setStyle("Fusion")
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    window = YoutubeDiaLog()
    app.exec_()
