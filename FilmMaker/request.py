from FilmMaker.QuickMask import VideoMask, FilmRenderReqMaker


class FilmRequest:
    def __init__(self, mainapp):
        self.mainapp = mainapp
        from FilmMaker.mediaplayer import MainWindow
        self.mainapp: MainWindow
        self.ytchannel = self.mainapp.ytpagelistview.cur_channel_name
        self.fbpage = self.mainapp.fbpagelistview.cur_page_name

    def generate_films_attribute(self):
        film_mask = []
        for each_vidmask in self.mainapp.videomask:
            each_vidmask: VideoMask
            object = each_vidmask.generate_filmrecap_obj()
            film_mask.append(object)

        return {
            'films': film_mask
        }

    def generate_header_attribute(self):
        if len(self.mainapp.text_header.text()):
            header = {
                'text': self.mainapp.text_header.text(),
                'font': {
                    'color': self.mainapp.color_hex.text(),
                    'size': self.mainapp.fontsize.value(),
                    'name': self.mainapp.fontname.currentFont().family()
                }
            }
            return {'header': header}
        else:
            return None

    def generate_footer_attribute(self):
        if len(self.mainapp.text_footer.text()):
            footer = {
                'text': self.mainapp.text_footer.text(),
                'font': {
                    'color': self.mainapp.color_hex.text(),
                    'size': self.mainapp.fontsize.value(),
                    'name': self.mainapp.fontname.currentFont().family()
                }
            }
            return {'footer': footer}
        else:
            return None

    def generate_pulisher_attribute(self):
        publish = {}
        if self.ytchannel:
            youtube = {'youtube': {'channel':self.ytchannel}}
            publish.update(youtube)
        if self.fbpage:
            fb_att = {'page': self.fbpage}
            header_att = self.generate_header_attribute()
            if header_att:
                fb_att.update(header_att)
            footer_att = self.generate_footer_attribute()
            if footer_att:
                fb_att.update(footer_att)
            facebook = {'facebook': fb_att}
            publish.update(facebook)
        publish_att = {'publish': publish}
        return publish_att

    def make_request(self):
        from FilmMaker.mediaplayer import MainWindow
        self.mainapp: MainWindow
        render_req = self.generate_films_attribute()
        publish_att = self.generate_pulisher_attribute()
        if len(publish_att):
            render_req.update(publish_att)
        filmmaker = FilmRenderReqMaker(render_req)
        filmmaker.start()
