import quixote
from quixote.directory import Directory, export, subdir

from . import html, image

class RootDirectory(Directory):
    _q_exports = []

    @export(name='')                    # this makes it public.
    def index(self):
        return html.render('index.html')

    @export(name='upload')
    def upload(self):
        return html.render('upload.html')

    @export(name='upload_receive')
    def upload_receive(self):
        request = quixote.get_request()
        print request.form.keys()

        the_file = request.form['file']
        filetype = the_file.orig_filename.split('.')[1]
        if(filetype == 'tif' or filetype == 'tiff'):
            filetype = 'tiff'
        elif(filetype == 'jepg' or filetype == 'jpg'):
            filetype == 'jpg'
        else:
            filetype == 'png'
        print 'received file of type: ' + filetype
        print dir(the_file)
        print 'received file with name:', the_file.base_filename
        data = the_file.read(int(1e9))

        image.add_image(data, filetype)

        return quixote.redirect('./')

    @export(name='image')
    def image(self):
        return html.render('image.html')

    @export(name='image_raw')
    def image_raw(self):
        response = quixote.get_response()
        request = quixote.get_request()
        try:
            img = image.get_image(int(request.form['num']))
        except KeyError:
            img = image.get_latest_image()
        response.set_content_type('image/%s' % img[1])
        return img[0]

    @export(name = 'image_list')
    def image_list(self):
        return html.render('image_list.html')

    @export(name = 'image_count')
    def image_count(self):
        return len(image.images)
    
    @export(name='jquery')
    def jquery(self):
        return open('jquery-1.11.0.min.js').read()


