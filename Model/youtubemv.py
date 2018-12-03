from werkzeug.datastructures import CombinedMultiDict
from werkzeug.local import LocalProxy

from View.view import MvInput, LyricForm
from backend.subcraw.asseditor import create_ass_subtitile
from backend.subcraw.subcrawler import get_sub_from_url


def handle_input_video(request: LocalProxy):
    mvinput = MvInput(CombinedMultiDict((request.files, request.form)))
    url = mvinput.get_nct_url()
    bg_img = mvinput.get_bg()
    if bg_img is not None:
        bg_img.save('/tmp/{}'.format(bg_img.filename))
        print("get bg image {}".format(bg_img))


def handle_new_lyric(form: LyricForm):
    if form.lyric_1st.data is not None:
        print("handle for lyric 1st")
    if form.lyric_2st.data is not None:
        print("handle for lyric 2nd")
    if form.url_nct.data is not None:
        print("handle for process nct url")
        lyric_content = get_sub_from_url(form.url_nct.data)
        create_ass_subtitile(lyric_content, "/tmp/newtest.ass")
        pass
