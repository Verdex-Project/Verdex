<img src="/assets/logos/transparentLogoColour.png" height="150px" alt="Verdex Project Logo">


# Verdex

Verdex is a tool to generate sustainable itineraries for trips to Singapore and to share your sustainable itinerary and experiences with others in a community excited about sustainable tourism.

Verdex is an ambitious project envisioned and developed by the Verdex Team for the App Development Project module in Year 1 Semester 2 of the Diploma in Information Technology course at Nanyang Polytechnic.

The app has a 50% chance of being live at [verdex.app](https://verdex.app). Try your luck.

Members of the Verdex Team include:
- [Prakhar Trivedi (@Prakhar896)](https://github.com/Prakhar896) - Verdex Itinerary Generation & Overall Lead
- [Joon Jun Han (@JunHammy)](https://github.com/JunHammy) - Head of Identity & Accounts
- [Lincoln Lim Ken Yang (@lincoln0623)](https://github.com/lincoln0623) - Head of Itinerary Experience
- [Joshua Long Yu Xuan (@Sadliquid)](https://github.com/Sadliquid) - Head of VerdexTalks (Community Forum)
- [Nicholas Chew Xun Cheng (@nicholascheww)](https://github.com/nicholascheww) - Head of Admin & Managerial Experience

# Table of Contents
- [About Verdex](#about-verdex)
- [Internal Services](#internal-services)
- [Integrations in Verdex](#integrations-in-verdex)
- [Usage & Requirements](#usage--requirements)

# About Verdex

Verdex is a state of mind. Just kidding.

Verdex has a unique algorithm that generates sustainable activities and itineraries for tourists visiting Singapore. The algorithm takes into account the user's preferences and the environmental impact of the activities. The app also has a community forum, neatly called VerdexTalks, where users can share their experiences and tips on sustainable tourism.

Another aim of the forum was for tourists with similar interests to connect and explore Singpaore as a group. This would reduce the carbon footprint of the tourists and also make the trip more enjoyable, especially for solo travellers.

Our easy-to-get-started flow allows users to sign up and start using the app in no time. The app has features like **Sign in with Google**, **VerdexGPT** and more to make the user experience as smooth as possible.

The UI of the app is designed to be simple and intuitive, with a focus on the user's experience. Designs across all webpages are the result of hundreds of hours of meticulous and iterative refinements with the user in mind.

The itinerary editor, especially, organises a large variety of granular features to personalise user itineraries in a beautiful and intuitive manner.

Behind the scenes, Verdex is powered by a robust backend that is designed to be scalable and secure. The backend is also stacked with various administerial feature and dials to control the app's operation and features. Verdex is backed by Firebase and Google Cloud Platform, which ensures disaster recovery, data synchronisation and excellent identity management.

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

# Integrations in Verdex

Verdex is integrated with several external services and APIs to provide a seamless and feature-rich experience to the user. These integrations are designed to be secure and reliable, and are used to enhance the user experience and the app's functionality.

The integrations include:
- **Firebase Authentication**: Used to handle user authentication and identity management.
- **Firebase Realtime Database**: Used to store and synchronise user data and itineraries across devices and the cloud.
- **Google Maps Directions & Embed APIs**: Used to fetch and display maps, routes and other location-based data. This data is used in itineraries to guide the user from point-to-point.
- **Google Identity Platform - OAuth**: Used to allow users to sign in with Google.
- **Google SMTP Servers**: Used to dispatch emails from the system directly to the user.
- **OpenAI GPT-3.5**: Used to allow users to get suggestions and tips for their sustainable itineraries. This feature is called VerdexGPT.

# Usage & Requirements

Verdex is a Flask-based web application with several dependencies. The app relies on Firebase Authentication for user and identity management and cannot operate without a successful connection. Firebase Realtime Database can be optionally turned off to make the system use a local database only.

Verdex requires the following minimum system requirements:
- Python 3.10 or higher ([download here](https://python.org/downloads))
- Installation of the following modules: `requests flask flask-cors python-dotenv googlemaps google google-auth google-auth-oauthlib firebase-admin pyrebase4 passlib openai`
- Firebase Project (`serviceAccountKey.json` file required)
- Google Cloud Platform Project (`clientSecrets.json` file required)
- `.env` file with several variables configuring the system

## Setting up online resources for integrations

Note that most integrations and services used in Verdex are optional to enable, so you can skip some of these steps accordingly. Refer to the [configuring environment variables](#configuring-environment-variables) section for more information on what services can be toggled.

**Firebase**
Verdex uses the Firebase Admin SDK and the Firebase Web Client API to interact with Firebase services. A `serviceAccountKey.json` (credentials) file and web app API key are needed.

Follow these steps:

1. Create a new Firebase project on [the Firebase console.](https://console.firebase.google.com)
2. Go to Project > Settings > Service Accounts and generate a new private key. Save this key as `serviceAccountKey.json` in the root directory of the Verdex codebase.
3. Go to Project Overview > Add app and create a web app. Follow the steps on the console to create the web app in the project.
4. Copy the web API key, auth domain, database URL, and storage bucket URL from the app configuration presented to you. These will be used in the `.env` file.

**Google Cloud Platform**
Verdex uses the Google Maps Embed API and the Google Maps Directions API (requires a GCP API key) to fetch and display maps, routes and other location-based data. A `clientSecrets.json` file is needed (if Google OAuth Login is to be enabled) that can be downloaded from the Google Cloud Console.

Follow these steps:

1. Create a new project on [the Google Cloud Console.](https://console.cloud.google.com)
2. Go to APIs & Services > Credentials and create a new API key. Follow the insturctions and ensure that the key is unrestricted. This key will be used in the `.env` file.
3. If you want to enable Google OAuth Login, you will need to create a new OAuth 2.0 client ID. Select Web Application and fill in the details as required. Download the `clientSecrets.json` file and save it in the root directory of the Verdex codebase.
    - For the redirect URI, please add to `http://localhost:8000/auth/google/callback` for local development and `https://yourdomainhere.com/account/oauthCallback` for production environments.
    - Note: The OAuth consent screen must be configured with the necessary scopes (Verdex only uses requires the email and profile scopes, which do not require further project verification from Google) and details.

**OpenAI GPT-3.5**
Verdex uses the OpenAI GPT-3.5 Chat Completion API to allow users to get suggestions and tips for their sustainable itineraries. An API key is needed should you wish to enable this integration.

Create an account on [OpenAI's website](https://openai.com) and follow the instructions to get an API key. This key will be used in the `.env` file.

**Google SMTP Emailing Services**
Verdex uses Google's SMTP servers to dispatch emails from the system directly to the user. This is used for email verification and password reset. You will need to enable less secure apps (requires 2FA to be on) on a Google account you want Verdex to use to send emails and generate an app password for Verdex to use. This Google account email and app password will be used in the `.env` file later.

## Configuring environment variables
Verdex allows you to control which services and integrations are enabled or disabled through environment variables. These variables are stored in a `.env` file in the root directory of the Verdex codebase.

The `.env` file should contain the following variables:

```env
# Verdex System Configuration (Required)
API_KEY= # Used for frontend API requests
AppSecretKey= # Used to sign cookies and sessions
LoggingEnabled= # Set to True/False (Manages the Logger service that makes log messages in a logs.txt file)
AnalyticsEnabled= # Set to True/False (Manages the Analytics service to collect and analyse client requests)
DebugMode= # Set to True/False (Manages the availability of debug endpoints (see debug.py) that can be used for debugging)

# Emailing Services (Required, set EmailingServicesEnabled to False to disable)
AppEmail= # Email address of the Google account to send emails from
EmailAppPassword= # App password of the Google account to use
EmailingServicesEnabled= # Set to True/False

# Firebase Services (Required)
FireConnEnabled=True # Must be set to True as usage of Firebase Authentication is required

## Firebase Realtime Database
FireRTDBEnabled= # Set to True/False
RTDB_URL= # URL of the Firebase Realtime Database

## Firebase Storage
FireStorageEnabled= # Set to True/False
STORAGE_URL= # URL of the Firebase Storage bucket

## Firebase Authentication
FireAPIKey=
FireAuthDomain=

# Google Maps Service (Optional)
GoogleMapsEnabled= # Set to True/False
GoogleMapsAPIKey= # API key obtained from the Google Cloud Console

# Google OAuth Service (Optional)
GoogleAuthEnabled= # Set to True/False
GoogleClientID= # Client ID obtained from the Google Cloud Console
GoogleAuthRedirectURI= # Redirect URI for Google OAuth

# OpenAI GPT-3.5 Service (Optional)
VerdexGPTEnabled= # Set to True/False
VerdexGPTSecretKey= # API key obtained from OpenAI
```

## Running Verdex

To run Verdex, simply execute `python main.py`. You should see all services coming online and Verdex booting up on port `8000` by default (you can change the port by changing the line of code in `main.py`). You can then access Verdex by visiting `http://localhost:8000` in your web browser or otherwise.

© 2023-2024 The Verdex Team. All rights reserved.
