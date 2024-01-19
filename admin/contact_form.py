from flask import  render_template, request, redirect, url_for, Blueprint, flash
from main import Universal, DI
import uuid, os, json, datetime
contactBP = Blueprint("faq", __name__)

@contactBP.route('/faq')
def faq():
    faq_data = [
        {"question": "How does your sustainable itinerary planner app contribute to eco-friendly tourism in Singapore?", 
         "answer": "Our app prioritizes sustainable attractions, accommodations, and activities, helping tourists create eco-conscious itineraries that minimize environmental impact and support local sustainability efforts."
         },
        {
        "question": "How does the itinerary generator in your app help users discover popular sustainable tourist attractions in Singapore?",
        "answer": "Our itinerary generator suggests popular tourist attractions in Singapore and helps users find a route by bus or train to the location they are interested in so that they do not need to take a cab, which is not very environmentally friendly."
        },
        {
        "question": "How does your app encourage users to explore off-the-beaten-path sustainable attractions in Singapore?",
        "answer": "Our app provides recommendations for hidden gems and lesser-known sustainable attractions, allowing users to discover unique experiences beyond the typical tourist spots."
        },      
        {
        "question": "Tell us more about VerdexTalks, your community forum. How does it enhance the user experience?",
        "answer": "VerdexTalks is our community forum where users can share their sustainable travel experiences, exchange tips, and connect with like-minded individuals. It enhances the overall user experience by fostering a community dedicated to responsible tourism."
        },
        {
        "question": "How does user interaction on VerdexTalks contribute to the overall sustainability mission of your app?",
        "answer": "User interactions on VerdexTalks create a community-driven platform where individuals share insights and tips for sustainable travel. This collaborative effort supports the broader mission of promoting responsible tourism in Singapore."
        },
         {
        "question": "Can users use VerdexTalks to organize meetups or join eco-friendly group activities during their stay in Singapore?",
        "answer": "Absolutely! VerdexTalks facilitates connections between users who share similar interests in sustainable travel. Users can organize meetups or join group activities to explore eco-friendly attractions together."
      }
    ]
    return render_template('misc/faq.html', faq_data=faq_data)

@contactBP.route('/contactUs', endpoint='contact_form', methods=['GET', 'POST'])
def contact_form():
    if request.method == "GET":
        return render_template('misc/contact.html')
    if request.method == "POST":
    ## Check if correct form fields are provided
        if 'name' not in request.form:
            flash("Please provide your name.")
            return redirect(url_for('faq.contact_form'))
        if 'email' not in request.form:
            flash("Please provide your email.")
            return redirect(url_for('faq.contact_form'))
        if 'message' not in request.form:
            flash("Please provide your message.")
            return redirect(url_for('faq.contact_form'))

        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if name.strip() == "" or email.strip() == "" or message.strip() == "":
            flash("Please provide all information necessary.")
            return redirect(url_for('faq.contact_form'))
        
        ## Generate ID and timestamp
        supportQueryID = uuid.uuid4().hex
        time_stamp = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
        
        if "supportQueries" not in DI.data["admin"]:
            DI.data["admin"]["supportQueries"] = {}
        DI.data["admin"]["supportQueries"][supportQueryID] = {
            "name": name,
            "email": email,
            "message": message,
            "supportQueryID": supportQueryID,
            "timestamp": time_stamp
        }
        ## Save to DI
        DI.save()
        ## Redirect to success page
        return redirect(url_for('faq.contact_success', supportQueryID= supportQueryID))


@contactBP.route('/contactUs/success', methods=['GET'], endpoint='contact_success')
def success():
    if 'supportQueryID' not in request.args:
        return redirect(url_for('faq.contact_form'))
    elif request.args['supportQueryID'] not in DI.data["admin"]["supportQueries"]:
        return redirect(url_for('faq.contact_form'))
    else:
        return render_template('misc/success.html')