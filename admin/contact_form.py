from flask import  render_template, request, redirect, url_for, Blueprint
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

@contactBP.route('/form', endpoint='contact_form', methods=['GET', 'POST'])
def contact_form():
    form_id = str(uuid.uuid4().hex)[:4]
    time = str(datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat))
    return render_template('misc/contact.html', form_id=form_id, time = time)

@contactBP.route('/success', methods=['GET'], endpoint='contact_success')
def success():
    return render_template('misc/success.html')