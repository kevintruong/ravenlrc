import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from FilmMaker.MainWindow import Ui_MainWindow
from FilmMaker.QuickMask import VideoMask, FilmRenderReqMaker
from FilmMaker.facebook import FacebookListView
from FilmMaker.youtube import YoutubeDiaLog, YoutubeListView
from backend.utility.Utility import FileInfo, only_latin_string


def hhmmss(ms):
    # s = 1000
    # m = 60000
    # h = 360000
    h, r = divmod(ms, 36000)
    m, r = divmod(r, 60000)
    s, _ = divmod(r, 1000)
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))


class ViewerWindow(QMainWindow):
    state = pyqtSignal(bool)

    def closeEvent(self, e):
        # Emit the window state, to update the viewer toggle button.
        self.state.emit(False)


class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.playlist = playlist

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index):
        return self.playlist.mediaCount()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.player = QMediaPlayer()
        self.player.error.connect(self.erroralert)
        self.player.play()

        # Setup the playlist.
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        # Add viewer for video playback, separate floating window.
        self.viewer = ViewerWindow(self)
        self.viewer.setWindowFlags(self.viewer.windowFlags() | Qt.WindowStaysOnTopHint)
        self.viewer.setMinimumSize(QSize(480, 360))

        videoWidget = QVideoWidget()
        self.viewer.setCentralWidget(videoWidget)
        self.player.setVideoOutput(videoWidget)

        # Connect control buttons/slides for media player.
        self.playButton.setShortcut(' ')
        self.playButton.pressed.connect(self.toggle_player)
        self.pauseButton.pressed.connect(self.player.pause)
        self.stopButton.pressed.connect(self.player.stop)
        self.volumeSlider.valueChanged.connect(self.player.setVolume)

        self.viewButton.toggled.connect(self.toggle_viewer)
        self.viewer.state.connect(self.viewButton.setChecked)

        self.previousButton.pressed.connect(self.playlist.previous)
        self.nextButton.pressed.connect(self.playlist.next)

        self.model = PlaylistModel(self.playlist)
        self.playlistView.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)

        selection_model = self.playlistView.selectionModel()
        selection_model.selectionChanged.connect(self.playlist_selection_changed)

        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.timeSlider.valueChanged.connect(self.player.setPosition)

        self.audiolist_model = QStandardItemModel()
        self.audio_list.setModel(self.audiolist_model)
        self.audio_list.selectionModel().selectionChanged.connect(self.audio_list_select_changed)

        self.sub_list_model = QStandardItemModel()
        self.sub_list.setModel(self.sub_list_model)
        self.sub_list.selectionModel().selectionChanged.connect(self.sub_list_select_changed)

        self.open_file_action.triggered.connect(self.open_file)
        self.open_file_action.setShortcut('Ctrl+O')

        self.actionmask_in.setShortcut('Ctrl+[')
        self.actionMask_Out.setShortcut('Ctrl+]')
        self.actionAdd_Masks.setShortcut('Ctrl+p')

        self.next1s.setShortcut('Ctrl++')
        self.back1s.setShortcut('Ctrl+-')

        self.back1s.pressed.connect(self.move_back_1s)
        self.next1s.pressed.connect(self.move_next_1s)
        self.finalizeButton.pressed.connect(self.send_render_film_req)
        self.resetButton.pressed.connect(self.reset_all)
        self.clearButton.pressed.connect(self.clear_all)

        self.button_loadsub.pressed.connect(self.manual_load_sub)

        self.button_add_acc_yt.pressed.connect(self.button_add_acc_yt_show)

        self.action_back5s.setShortcut('[')
        self.action_next5s.setShortcut(']')
        self.action_next5s.triggered.connect(self.move_next_5s)
        self.action_back5s.triggered.connect(self.move_back_5s)

        self.actionRemove_selected.setShortcut('d')
        self.actionRemove_selected.triggered.connect(self.remove_selected_in_playlist)

        self.actionAdd_Masks.triggered.connect(self.push_mask_vid)
        self.actionMask_Out.triggered.connect(self.set_mask_out)
        self.actionmask_in.triggered.connect(self.set_mask_in)
        self.setAcceptDrops(True)
        self.videomask = []
        self.curvidMask = None
        self.defaut_config()

        self.ytpagelistview = YoutubeListView(self.list_youtube)
        self.ytpagelistview.display_all_channel()
        self.fbpagelistview = FacebookListView(self.list_facebookpage)
        self.fbpagelistview.display_all()
        self.yt_add_dialog = YoutubeDiaLog()
        self.show()

    def defaut_config(self):
        default_font = QFont('Source Sans Pro')
        self.fontname.setCurrentFont(default_font)
        self.fontsize.setValue(80)
        self.color_hex.setText('0xffffff')

    def button_add_acc_yt_show(self):
        value = self.yt_add_dialog.exec_()
        if value == QDialog.Accepted:
            print('add new add => refresh acc list')
            self.ytpagelistview.display_all_channel()
        else:
            print('cancel')

    def remove_selected_in_playlist(self):
        curindex = self.playlist.currentIndex()
        self.playlist.removeMedia(curindex)
        self.audio_list.model().clear()
        self.sub_list.model().clear()
        self.videomask.remove(self.curvidMask)
        print('remove the selection {}'.format(curindex))

    def audio_list_select_changed(self):
        curentindex = self.audio_list.currentIndex()
        curentindex: QModelIndex
        data: str = curentindex.data(Qt.DisplayRole)
        lang = data.split(",")[1]
        self.curvidMask: VideoMask
        self.curvidMask.audio_lang = lang
        print('audio list ')
        pass

    def sub_list_select_changed(self):
        curentindex = self.sub_list.currentIndex()
        curentindex: QModelIndex
        data: str = curentindex.data(Qt.DisplayRole)
        subtitle_uri = data.split("===")[1].strip()
        self.curvidMask: VideoMask
        self.curvidMask.set_subtitle_uri(subtitle_uri)
        print('subtitle list {}'.format(subtitle_uri))
        pass

    def toggle_player(self):
        curstatus = self.player.state()
        if curstatus == QMediaPlayer.StoppedState or curstatus == QMediaPlayer.PausedState:
            self.player.play()
            if self.viewer.isHidden():
                self.viewer.show()
        elif curstatus == QMediaPlayer.PlayingState:
            self.player.pause()

    def move_back_5s(self):
        mask_in = self.player.position()
        mask_in = mask_in - 5000
        self.player.setPosition(mask_in)

    def move_next_5s(self):
        mask_in = self.player.position()
        mask_in = mask_in + 5000
        self.player.setPosition(mask_in)

    def move_back_1s(self):
        mask_in = self.player.position()
        mask_in = mask_in - 1000
        self.player.setPosition(mask_in)

    def clear_all(self):
        for video_mask in self.videomask:
            video_mask: VideoMask
            video_mask.timing.clear()
        self.curvidMask.timing.clear()

    def reset_all(self):
        self.videomask.clear()
        self.playlist.clear()
        self.audio_list.model().clear()
        self.sub_list.model().clear()
        self.videomask.clear()
        self.player.stop()

    def send_render_film_req(self):
        from FilmMaker.request import FilmRequest
        print('send render request')
        request = FilmRequest(self)
        request.make_request()

    def move_next_1s(self):
        print('move next 1s')
        mask_in = self.player.position()
        mask_in = mask_in + 1000
        self.player.setPosition(mask_in)

    def set_mask_in(self):
        curvid = self.playlist.currentIndex()
        maskvideo: VideoMask = self.videomask[curvid]
        # maskvideo = self.curvidMask
        mask_in = self.player.position()
        self.mask_in_value.setText(f"{mask_in}")
        maskvideo.mask_in(mask_in)

    def set_mask_out(self):
        curvid = self.playlist.currentIndex()
        maskvideo: VideoMask = self.videomask[curvid]
        # maskvideo = self.curvidMask
        mask_out = self.player.position()
        self.mask_out_value.setText(f"P{mask_out}")
        maskvideo.mask_out(mask_out)

    def push_mask_vid(self):
        curvid = self.playlist.currentIndex()
        maskvideo: VideoMask = self.videomask[curvid]
        # maskvideo = self.curvidMask
        maskvideo.add_mask()
        footer = self.text_footer.text()
        print(footer)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.playlist.addMedia(
                QMediaContent(url)
            )
        self.model.layoutChanged.emit()
        # If not playing, seeking to first of newly added + play.
        if self.player.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(e.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.player.play()

    def update_audio_stream(self):
        self.curvidMask: VideoMask

        substreams = self.curvidMask.get_audiostreams()
        if len(substreams):
            model = self.audio_list.model()
            model.clear()
            for f in substreams:
                f = ",".join(f)
                model.appendRow(QStandardItem(f))
        if self.curvidMask.audio_lang:
            model: QStandardItemModel
            for i in range(model.rowCount()):
                value = model.item(i).text()
                if self.curvidMask.audio_lang in value:
                    index = model.index(i, 0)
                    self.audio_list.setCurrentIndex(index)
                    break
            self.curvidMask.audio_lang = None  # reset the audio_lang

    def update_subtitle_stream(self):
        self.curvidMask: VideoMask
        substreams = self.curvidMask.get_substreams()
        view = self.sub_list
        model: QStandardItemModel = view.model()
        model.clear()
        for f in substreams:
            f = "===".join(f)
            model.appendRow(QStandardItem(f))
        if self.curvidMask.subtitle:
            model: QStandardItemModel
            for i in range(model.rowCount()):
                value = model.item(i).text()
                if self.curvidMask.subtitle in value:
                    index = model.index(i, 0)
                    self.sub_list.setCurrentIndex(index)
                    break
        pass

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "mp3 Audio (*.mp3);mp4 Video (*.mp4);Movie files (*.mov);All files (*.*)")
        if path:
            videomask = VideoMask()
            self.curvidMask = videomask
            videomask.set_video(path)
            self.update_subtitle_stream()
            self.update_audio_stream()
            # lang_index = videomask.get_substream_index_by_lang('vie')
            # if lang_index:
            #     videomask.get_subtitle_from_movie('vie')
            self.videomask.append(videomask)
            self.playlist.addMedia(
                QMediaContent(
                    QUrl.fromLocalFile(path)
                )
            )
        self.model.layoutChanged.emit()

    def manual_load_sub(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "subtitle (*.srt);advandce sub(*.ass);All files (*.*)")
        if os.path.exists(path):
            fileinfo = FileInfo(path)
            subfile = only_latin_string(fileinfo.name)
            newsubfile = os.path.join(fileinfo.dir, "{}.ass".format(subfile))
            VideoMask.format_subtitle(path, newsubfile)
            path = newsubfile

        self.curvidMask.subtitle = path
        subtitle = "Null==={}".format(path)
        subitem = QStandardItem(subtitle)
        self.sub_list_model.appendRow(subitem)

    def update_duration(self, mc):
        self.timeSlider.setMaximum(self.player.duration())
        duration = self.player.duration()

        if duration >= 0:
            self.totalTimeLabel.setText(hhmmss(duration))

    def update_position(self, *args):
        position = self.player.position()
        if position >= 0:
            self.currentTimeLabel.setText(hhmmss(position))

        # Disable the events to prevent updating triggering a setPosition event (can cause stuttering).
        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(position)
        self.timeSlider.blockSignals(False)

    def playlist_selection_changed(self, ix):
        # We receive a QItemSelection from selectionChanged.
        i = ix.indexes()[0].row()
        self.playlist.setCurrentIndex(i)

    def playlist_position_changed(self, i):
        if i > -1:
            ix = self.model.index(i)
            self.playlistView.setCurrentIndex(ix)
            self.curvidMask = self.videomask[i]
            self.curvidMask: VideoMask
            self.update_audio_stream()
            self.update_subtitle_stream()
            self.update_res()

    def update_res(self):
        curvid = self.curvidMask
        curvid: VideoMask
        res = curvid.get_video_resolution()
        self.resolution_value.setText(res)
        print(res)
        pass

    def toggle_viewer(self, state):
        if state:
            self.viewer.show()
        else:
            self.viewer.hide()

    def erroralert(self, *args):
        print(args)


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Film Recap Maker")
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    window = MainWindow()
    app.exec_()
