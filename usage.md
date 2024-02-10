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

---

Have fun exploring Verdex! We hope you like it. 🌿

© 2023-2024 The Verdex Team. All rights reserved.