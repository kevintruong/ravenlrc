import hug


@hug.post('/crawl')
def upload_file(body):
    """accepts file uploads"""
    # <body> is a simple dictionary of {filename: b'content'}
    print('body: ', body)
    return {'filename': list(body.keys()).pop(), 'filesize': len(list(body.values()).pop())}


@hug.post('/build_mv')
def build_mv(body):
    """accepts file uploads"""
    # <body> is a simple dictionary of {filename: b'content'}
    return {'post_message': body}


@hug.post('/build_template')
def build_template(body):
    """accepts file uploads"""
    # <body> is a simple dictionary of {filename: b'content'}

    return {'post_message': body}
