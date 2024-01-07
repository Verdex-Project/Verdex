#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template, json, request, jsonify, redirect, url_for
from main import Universal, DI
import datetime


forumBP = Blueprint("forum", __name__)   


@forumBP.route('/', methods=['GET', 'POST'])
def verdextalks():
    global postsInfoJson

    postsInfoJson = postsInfoJson if 'existing_data' in globals() else {}

    if request.method == 'GET':
        with open('templates/forum/postsInfo.json', 'r') as file:
            postsInfoJson = json.load(file)

    if request.method == 'POST' and 'addNewPost' in request.form:
        if not (request.form.get('post_title') and request.form.get('post_description') and request.form.get('user_names')):
            with open('templates/forum/postsInfo.json', 'w') as file:
                json.dump(postsInfoJson, file, indent=4)
        else:
            post_title = request.form.get('post_title')
            post_description = request.form.get('post_description')
            user_names = request.form.get('user_names')
            # Load existing data
            with open('templates/forum/postsInfo.json', 'r') as json_file:
                postsInfoJson = json.load(json_file)

            new_post = {
                "user_names": user_names,
                "post_title": post_title,
                "post_description": post_description,
                "likes": 0
            }

            post_id = len(postsInfoJson) + 1
            while str(post_id) in postsInfoJson:
                day_number += 1
            postsInfoJson[str(post_id)] = new_post

            with open('templates/forum/postsInfo.json', 'w') as file:
                json.dump(postsInfoJson, file, indent=4)
                
            return redirect(url_for('forum.verdextalks'))

    return render_template("forum/forum.html", postsInfoJson=postsInfoJson)

# postsInfoJson=jsonify(DI.data["forum"])

