from werkzeug.datastructures import CombinedMultiDict
from werkzeug.local import LocalProxy
from wtforms import Form

from View.view import MvInput


def handle_input_video(request: LocalProxy):
    mvinput = MvInput(CombinedMultiDict((request.files, request.form)))
    url = mvinput.get_url()
    bg_img = mvinput.get_bg()
    if bg_img is not None:
        bg_img.save('/tmp/{}'.format(bg_img.filename))
        print("get bg image {}".format(bg_img))
