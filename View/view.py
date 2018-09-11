from wtforms import Form, StringField, FileField, IntegerField, SelectField


class AffectForm(Form):
    """

    """
    affectMv = FileField('Affect file')
    opacity = IntegerField('Opacity')
    # media_type = SelectField('Media', choices=media_types)


class LyricForm(Form):
    """
    `id` INT NOT NULL AUTO_INCREMENT,
   `Lyric_1st` MEDIUMBLOB NULL,
   `Lyric_2nd` MEDIUMBLOB NULL,
    """
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


class ScreenConfiguration:
    screen_template_list = []
    screen_template_id = SelectField("select template Id for current screen", choices=screen_template_list)
    screen_list = []
    screen_id = SelectField("Select Screen id for current screen", choices=screen_list)
