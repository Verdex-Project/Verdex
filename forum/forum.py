#Blueprint for VerdexTalks main forum page
from flask import Blueprint, render_template, json, request, jsonify, redirect, url_for
from main import Universal, DI
import datetime

forumBP = Blueprint("forum", __name__)

@forumBP.route('/verdextalks', methods=['GET', 'POST'])
def verdextalks():
    if request.method == 'POST' and 'addNewPost' in request.form:
        if (request.form.get('post_title') and request.form.get('post_description') and request.form.get('user_names')):
            post_title = request.form.get('post_title')
            post_description = request.form.get('post_description')
            user_names = request.form.get('user_names')
            post_tag = request.form.get('post_tag')

            postDateTimeId = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)

            new_post = {
                "user_names": user_names,
                "post_title": post_title,
                "post_description": post_description,
                "likes": "0",
                "postDateTimeId": postDateTimeId,
                "liked_status": False,
                "tag": post_tag,
                "comments": {}
            }

            DI.data["forum"][postDateTimeId] = new_post

            DI.save() 
            return redirect(url_for('forum.verdextalks'))

    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"])


@forumBP.route('/comment_post', methods=['POST'])
def comment_on_post():
    try:
        if request.is_json:
            json_data = request.get_json()
            post_id = json_data.get('postId')
            comment_description = json_data.get('comment_description')
            if post_id and comment_description:
                if post_id in DI.data["forum"]:
                    if 'comments' not in DI.data["forum"][post_id]:
                        DI.data["forum"][post_id]['comments'] = []
                    postDateTime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
                    DI.data["forum"][post_id]['comments'][postDateTime] = comment_description
                    DI.save()
    except Exception as e:
        print(f"Error: {e}")
        return "ERROR: An error has occured."

    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"])

@forumBP.route('/edit_post', methods=['GET', 'POST'])
def edit_post():
    try:
        if request.is_json:
            post_id = request.get_json().get('postId')
            edit_user_names = request.get_json().get('edit_user_names')
            edit_post_title = request.get_json().get('edit_post_title')
            edit_post_description = request.get_json().get('edit_post_description')
            edit_post_tag = request.get_json().get('edit_post_tag')

            if post_id and edit_user_names and edit_post_title and edit_post_description:
                if post_id in DI.data["forum"]:
                    DI.data["forum"][post_id]["user_names"] = edit_user_names
                    DI.data["forum"][post_id]["post_title"] = edit_post_title
                    DI.data["forum"][post_id]["post_description"] = edit_post_description
                    if edit_post_tag:
                        DI.data["forum"][post_id]["tag"] = edit_post_tag
                    DI.save()
    except Exception as e:
        print(f"Error: {e}")
        return "ERROR: An error has occured."

    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"])
    


