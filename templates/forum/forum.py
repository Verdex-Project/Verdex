#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template, json, request, jsonify, redirect, url_for
from main import Universal, DI
import datetime


forumBP = Blueprint("forum", __name__)   


@forumBP.route('/', methods=['GET', 'POST'])
def verdextalks():
    if request.method == 'POST' and 'addNewPost' in request.form:
        if (request.form.get('post_title') and request.form.get('post_description') and request.form.get('user_names')):
            post_title = request.form.get('post_title')
            post_description = request.form.get('post_description')
            user_names = request.form.get('user_names')

            new_post = {
                "user_names": user_names,
                "post_title": post_title,
                "post_description": post_description,
                "likes": 0
            }

            postDateTime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
            DI.data["forum"][postDateTime] = new_post

            #JUST FOR TESTING, REMOVE ASAP.
            print("-----DI-----") 
            print(DI.data)
            print("-----END-----")
            # REMOVE ASAP.

            DI.save() 
            return redirect(url_for('forum.verdextalks'))

    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"])
