# -*- coding: utf-8 -*-
'''
Created on 2017年5月25日

@author: chenyitao
'''

from . import app
from flask import render_template
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import Form
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap

# 新建一个set用于设置文件类型、过滤等
set_mypic = UploadSet('mypic')  # mypic

# 用于wtf.quick_form()模版渲染
bootstrap = Bootstrap(app)

# mypic 的存储位置,
# UPLOADED_xxxxx_DEST, xxxxx部分就是定义的set的名称, mypi, 下同
app.config['UPLOADED_MYPIC_DEST'] = './app/static/img'

# mypic 允许存储的类型, IMAGES为预设的 tuple('jpg jpe jpeg png gif svg bmp'.split())
app.config['UPLOADED_MYPIC_ALLOW'] = IMAGES

# 把刚刚app设置的config注册到set_mypic
configure_uploads(app, set_mypic)

app.config['SECRET_KEY'] = 'xxxxx'

# 此处WTF的SCRF密码默认为和flask的SECRET_KEY一样
# app.config['WTF_CSRF_SECRET_KEY'] = 'wtf csrf secret key'


class UploadForm(Form):
    '''
        一个简单的上传表单
    '''

    # 文件field设置为‘必须的’，过滤规则设置为‘set_mypic’
    upload = FileField('image', validators=[
                       FileRequired(), FileAllowed(set_mypic, 'you can upload images only!')])
    submit = SubmitField('ok')


@app.route('/', methods=('GET', 'POST'))
def index():
    form = UploadForm()
    url = None
    if form.validate_on_submit():
        filename = form.upload.data.filename
        url = set_mypic.save(form.upload.data, name=filename)
    return render_template('index.html', form=form, url=url)
