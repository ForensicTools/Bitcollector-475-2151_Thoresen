from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from . import main
from .forms import GenerateConfiguration

@main.route('/', methods=['GET', 'POST'])
def index():
    form = GenerateConfiguration()
    if form.validate_on_submit():
        print("Hey look at that!")
    return render_template('index.html', form=form)
