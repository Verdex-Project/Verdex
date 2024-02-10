<img src="/assets/logos/transparentLogoColour.png" height="150px" alt="Verdex Project Logo">


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Jinja](https://img.shields.io/badge/jinja-white.svg?style=for-the-badge&logo=jinja&logoColor=black)
![Firebase](https://img.shields.io/badge/Firebase-039BE5?style=for-the-badge&logo=Firebase&logoColor=white)
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)
![ChatGPT](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)


# Verdex

<img src="/assets/docs/img/homepage.png" alt="Verdex Homepage">

Verdex is a tool to generate sustainable itineraries for trips to Singapore and to share your sustainable itinerary and experiences with others in a community excited about sustainable tourism.

Verdex is an ambitious project envisioned and developed by the Verdex Team for the App Development Project module in Year 1 Semester 2 of the Diploma in Information Technology course at Nanyang Polytechnic.

The app has a 50% chance of being live at [verdex.app](https://verdex.app). Try your luck lol.

Members of the Verdex Team include:
- [Prakhar Trivedi (@Prakhar896)](https://github.com/Prakhar896) - Verdex Itinerary Generation & Overall Lead
- [Joon Jun Han (@JunHammy)](https://github.com/JunHammy) - Head of Identity & Accounts
- [Lincoln Lim Ken Yang (@lincoln0623)](https://github.com/lincoln0623) - Head of Itinerary Experience
- [Joshua Long Yu Xuan (@Sadliquid)](https://github.com/Sadliquid) - Head of VerdexTalks (Community Forum)
- [Nicholas Chew Xun Cheng (@nicholascheww)](https://github.com/nicholascheww) - Head of Admin & Managerial Experience

# Table of Contents
- [About Verdex](#about-verdex)
- [Integrations in Verdex](#integrations-in-verdex)
- [Internal Services](#internal-services)
- [Usage & Requirements](usage.md)

# About Verdex

Verdex is a state of mind. Just kidding.

<img src="/assets/docs/img/itineraryGeneration.png" alt="Generating Itineraries">

Verdex has a unique algorithm that generates sustainable activities and itineraries for tourists visiting Singapore. The algorithm takes into account the user's preferences and the environmental impact of the activities. The app also has a community forum, neatly called VerdexTalks, where users can share their experiences and tips on sustainable tourism.

---

<img src="/assets/docs/img/verdextalks.png" alt="VerdexTalks Community Forum">

Another aim of the forum was for tourists with similar interests to connect and explore Singapore as a group. This would reduce the carbon footprint of the tourists and also make the trip more enjoyable, especially for solo travellers.

---

<img src="/assets/docs/img/signup.png" alt="Creating an account on Verdex">

Our easy-to-get-started flow allows users to sign up and start using the app in no time. The app has features like **Sign in with Google**, **VerdexGPT** and more to make the user experience as smooth as possible.

The UI of the app is designed to be simple and intuitive, with a focus on the user's experience. Designs across all webpages are the result of hundreds of hours of meticulous and iterative refinements with the user in mind.

---

<img src="/assets/docs/img/editor.png" alt="Editing an Itinerary">

The itinerary editor, especially, organises a large variety of granular features, including real-time directions from Google Maps between activities in a day, to personalise user itineraries in a beautiful and intuitive manner.

---

<img src="/assets/docs/img/admin.png" alt="Verdex Admin Dashboard">

Behind the scenes, Verdex is powered by a robust backend that is designed to be scalable and secure. The backend is also stacked with various administerial features and dials to control the app's operation and features. Verdex is backed by Firebase and Google Cloud Platform, which ensures disaster recovery, data synchronisation and excellent identity management.

# Integrations in Verdex

Verdex is integrated with several external services and APIs to provide a seamless and feature-rich experience to the user. These integrations are designed to be secure and reliable, and are used to enhance the user experience and the app's functionality.

The integrations include:
- **Firebase Authentication**: Used to handle user authentication and identity management.
- **Firebase Realtime Database**: Used to store and synchronise user data and itineraries across devices and the cloud.
- **Google Maps Directions & Embed APIs**: Used to fetch and display maps, routes and other location-based data. This data is used in itineraries to guide the user from point-to-point.
- **Google Identity Platform - OAuth**: Used to allow users to sign in with Google.
- **Google SMTP Servers**: Used to dispatch emails from the system directly to the user.
- **OpenAI GPT-3.5**: Used to allow users to get suggestions and tips for their sustainable itineraries. This feature is called VerdexGPT.

# Internal Services

Verdex has a few internal services that power the app and it's various operations. These services were designed to be highly available and safe to use and operate. They mainly handle the granular interactions of Verdex's core codebase with various external services and APIs.

The services include:
- **DatabaseInterface**: A critical central interface for Verdex code to interact with the database. All database operations are simplified through this service, which automatically handles the updating, synchronisation (especially with cloud) and schema enforcement of the database.
- **FireAuth**: A service that allows Verdex code to quickly, simply and securely interact with Firebase Authentication APIs. This service is used to handle user authentication and identity management.
- **GoogleOAuth**: Simplifies interaction with Google Identity Platform APIs to allow users to sign in with Google. Works closely with `FireAuth` to ensure a seamless and secure experience.
- **GoogleMapsService**: A service that allows Verdex code to interact with Google Maps APIs. This service is used to fetch and display maps, routes and other location-based data. This data is used in itineraries to guide the user from point-to-point.
- **Emailer**: An SMTP-based service using Google SMTP servers that allows the quick and simplified dispatch of emails from the system directly to the user.
- **AdminConsole**: Interactive service to create and manage admin accounts with special privileges on Verdex. This service can be used to scale the admin team and manage their access to the app's backend.
- **Analytics**: A service that allows Verdex to collect and analyse user data to improve the app's performance and user experience. This service is designed to be GDPR-compliant and respects user privacy.

There are several other micro-services as well that help with system efficiency, auditing and debugging.

---

Looking for how to set-up and try out Verdex? Check out the [Usage & Requirements](usage.md) documentation.

Thank you for checking out Verdex, and we hope you look to travelling sustainably! 🌿

© 2023-2024 The Verdex Team. All rights reserved.
