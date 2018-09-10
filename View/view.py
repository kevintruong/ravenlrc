from wtforms import Form, StringField, FileField


class AffectForm(Form):
    media_types = [('Digital', 'Digital'),
                   ('CD', 'CD'),
                   ('Cassette Tape', 'Cassette Tape')
                   ]
    artist = StringField('Artist')
    title = StringField('Title')
    release_date = StringField('Release Date')
    publisher = StringField('Publisher')
    affectMv = FileField('Affect file')
    # media_type = SelectField('Media', choices=media_types)
