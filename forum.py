#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template


verdextalks_page = Blueprint("forum", __name__)

#Main forum page
@verdextalks_page.route('/')
def verdextalks():
    return render_template('forum/forum.html')
