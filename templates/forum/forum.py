#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template


forumBP = Blueprint("forum", __name__)

#Main forum page
@forumBP.route('/')
def verdextalks():
    return render_template('forum/forum.html')
