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

            postDateTimeId = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)

            new_post = {
                "user_names": user_names,
                "post_title": post_title,
                "post_description": post_description,
                "likes": "0",
                "postDateTimeId": postDateTimeId,
                # "comments": []
            }

            DI.data["forum"][postDateTimeId] = new_post

            DI.save() 
            return redirect(url_for('forum.verdextalks'))

    return render_template("forum/forum.html", postsInfoJson=DI.data["forum"])


# @forumBP.route('/comment-post', methods=['GET', 'POST'])
# def comment_on_post():
#     try:
#         data = request.get_json()

#         post_id = data.get('postId')
#         print(f"Post ID: {post_id}")
#         comment = data.get('comment_description')

#         if post_id in DI.data["forum"]:
#             DI.data["forum"][post_id]["comments"].append(comment)
#             DI.save()

#             return jsonify({'comments': DI.data["forum"][post_id]["comments"]})
        
#     except Exception as e:
#         print(f"Error: {e}")
    
#     return render_template("forum/forum.html", postsInfoJson=DI.data["forum"])
