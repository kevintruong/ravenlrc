import os

from flask_uploads import UploadSet, IMAGES, AUDIO
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from werkzeug.datastructures import FileStorage
from wtforms import *
from wtforms.fields.html5 import URLField

from backend.subcraw.ass_customizor import create_ass_sub
from backend.ffmpeg.ffmpegcli import FfmpegCli, Coordinate
from backend.subcraw.subcrawler import download_mp3_file

UPLOAD_FOLDER = '/tmp/'

photos = UploadSet('photos', IMAGES)


class AffectForm(FlaskForm):
    """

    """
    affectMv = FileField('Affect file')
    opacity = IntegerField('Opacity')
    # media_type = SelectField('Media', choices=media_types)


class LyricForm(FlaskForm):
    """
    `id` INT NOT NULL AUTO_INCREMENT,
   `Lyric_1st` MEDIUMBLOB NULL,
   `Lyric_2nd` MEDIUMBLOB NULL,
    """
    url_nct = URLField('input nhaccuatui url ')
    lyric_1st = FileField('Lyric 1st:')
    lyric_2st = FileField('Lyric 2st:')


class TitleForm(Form):
    """
    `id` INT NOT NULL AUTO_INCREMENT,
    `TitleFile` MEDIUMBLOB NULL,
    """
    title_preset_list = []
    title_file = FileField('Title: ')
    title_str = StringField('Title String: ')
    preset_id = SelectField('Title Preset Id', choices=title_preset_list)


class SongForm(Form):
    """
      `id` INT NOT NULL AUTO_INCREMENT,
      `SongName` VARCHAR(45) NULL,
      `Lyric_id` INT NOT NULL,
      `Title_id` INT NOT NULL,
      `SongFile` MEDIUMBLOB NULL,
    """
    Idlist = []
    TitileId = []
    song_name = StringField('Name of song:')
    lyric_id = SelectField('lyric Id:', choices=Idlist)
    title_id = SelectField('Title Id:', choices=TitileId)
    song_file = FileField('Song file')


class ScreenTemplateForm(Form):
    """
    `id` INT NOT NULL AUTO_INCREMENT,
      `Title_pos` BINARY(16) NULL,
      `Sub1st_pos` BINARY(16) NULL,
      `Sub1sh_color` INT NULL,
      `Sub2nd_pos` BINARY(16) NULL,
      `Sub2nd_color` INT NULL,
      `FontName` VARCHAR(45) NULL,
      `FontSize` INT NULL,
    """
    title_pos = StringField("Title Post <x,y>")
    sub1st_pos = StringField("Subtitle 1st position <x,y>")
    sub1st_color = StringField("Subtitle 1st color code")
    font_1st_name = StringField("Font for title 1:")
    font_1st_size = IntegerField("Font size for subtitle 1:")
    sub2nd_pos = StringField("Subtitle 2nd position <x,y>")
    sub2nd_color = StringField("Subtitle 2nd color code")
    font_2nd_name = StringField("Font for title 2:")
    font_2nd_size = IntegerField("Font size for subtitle 2:")


class ScreenForm(Form):
    """
      `id` INT NOT NULL AUTO_INCREMENT,
      `ScreenFile` LONGBLOB NULL,
      `Affect_id` INT NOT NULL,
    """
    affectlist = []
    screen_file = FileField("Screen file upload:")
    affect_id = SelectField("select affect id for the screen:", choices=affectlist)


class ScreenConfiguration(Form):
    """
    `id` INT NOT NULL AUTO_INCREMENT,
    `ScreenTemplate_id` INT NOT NULL,
    `Screen_id` INT NOT NULL,
    """
    screen_template_list = []
    screen_template_id = SelectField("select template Id for current screen", choices=screen_template_list)
    screen_list = []
    screen_id = SelectField("Select Screen id for current screen", choices=screen_list)


class YoutubeMV(Form):
    """
    `id` INT NOT NULL AUTO_INCREMENT,
    `ScreenConfiguration_id` INT NOT NULL,
    `Song_id` INT NOT NULL,
    `Song_Title_id` INT NOT NULL,
    """
    screen_conf_list = []
    song_list = []
    song_title_list = []
    screen_conf_id = SelectField("Select Screen configuration Id:", choices=screen_conf_list)
    song_id = SelectField("Select song Id:", choices=song_list)


class MvInput(FlaskForm):
    """
    sound_url: <nhaccuatui> URL
    background_img: <background image>
    title_img <title image>
    title_pos <title position>
    affect_mv : <affect video>
    affect_opacity: <int: affect opacity>
    sub1st_pos : <position of subtitle 1>
    sub1st_color: <color code of subtitle 1>
    sub1st_font : <sub1st_font>
    sub1st_fontsize: < font size of subtitle 1>
    """
    audio = UploadSet("audio", AUDIO)
    sound_nct_url = URLField("Nhaccuatui Url <included lyric>:")
    mp3_file = FileField("Mp3 file",
                         validators=[FileRequired("file must upload"),
                                     FileAllowed(['mp3'], "audio file only")]
                         )
    bg_img = FileField("Background image")
    title_img = FileField("Title image")
    title_pos_x = IntegerField("Title Position x : ")
    title_pos_y = IntegerField("Title Position y : ")
    affect_mv = FileField("Affect: ")
    affect_opacity = IntegerField("Affect opacity:")
    sub1st_pos_x = IntegerField("Subtitle 1 position x : ")
    sub1st_pos_y = IntegerField("Subtitle 1 position y : ")
    sub1st_color = StringField("subtitle color code:")
    sub1st_font = StringField("Subtitle 1 Font name")
    sub1st_fontsize = IntegerField("Subtitle font size")

    def file_return(self, filedata: FileStorage):
        filesave = os.path.join(UPLOAD_FOLDER, filedata.filename)
        filedata.save(filesave)
        return filesave

    def get_nct_url(self):
        return self.sound_nct_url.data

    def get_bg_img(self) -> FileStorage:
        return self.bg_img.data

    def get_title(self) -> FileStorage:
        return self.title_img.data

    def get_title_pos(self):
        return [self.title_pos_x.data, self.title_pos_y.data]

    def get_sub_pos(self):
        return [self.sub1st_pos_x.data, self.sub1st_pos_y.data]

    def get_sub_font(self):
        return self.sub1st_font.data

    def handle_new_mv(self):
        create_ass_sub(self.get_nct_url(), "D:\\Project\\ytcreatorservice\\backend\\Content\\Ass\\test.ass")
        bg_img_file = self.file_return(self.get_bg_img())
        title_img_file = self.file_return(self.get_title())
        download_mp3_file(self.get_nct_url())
        ffmpeg_cli = FfmpegCli()
        ffmpeg_cli.add_logo_to_bg_img(bg_img_file,
                                      title_img_file,
                                      "/tmp/test.png",
                                      Coordinate(100, 100))
