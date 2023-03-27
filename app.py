#!/usr/bin/env python3
""" Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# Import Section
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, make_response
from requests_oauthlib import OAuth2Session
import json
import os
import requests
import datetime
import time
from webexteamssdk import WebexTeamsAPI
from dotenv import load_dotenv

import webex_api

# load all environment variables
load_dotenv()

AUTHORIZATION_BASE_URL = 'https://api.ciscospark.com/v1/authorize'
TOKEN_URL = 'https://api.ciscospark.com/v1/access_token'
SCOPE = "spark-admin:devices_read spark-admin:devices_write"

#initialize variabes for URLs
#REDIRECT_URL must match what is in the integration, but we will construct it below in __main__
# so no need to hard code it here
PUBLIC_URL='http://localhost:5000'
#REDIRECT_URI will be set in configure() if it needs to trigger the oAuth flow
REDIRECT_URI=""

BASE_URL = os.getenv("BASE_URL")

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.secret_key = '123456789012345678901234'

AppAdminID=''

#Methods
#Returns location and time of accessing device
def getSystemTime():
    #request user ip
    userIPRequest = requests.get('https://get.geojs.io/v1/ip.json')
    userIP = userIPRequest.json()['ip']

    #request geo information based on ip
    geoRequestURL = 'https://get.geojs.io/v1/ip/geo/' + userIP + '.json'
    geoRequest = requests.get(geoRequestURL)
    geoData = geoRequest.json()

    #create info string
    location = geoData['country']
    timezone = geoData['timezone']
    current_time=datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    time = "{} {}".format(current_time, timezone)

    return time

##Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route("/callback", methods=["GET"])
def callback():
    """
    Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    global REDIRECT_URI

    print(session)
    print("oauth_state: {}".format(session['oauth_state']))
    print("Came back to the redirect URI, trying to fetch token....")
    print("redirect URI should still be: ",REDIRECT_URI)
    print("Calling OAuth2SEssion with CLIENT_ID ",os.getenv('CLIENT_ID')," state ",session['oauth_state']," and REDIRECT_URI as above...")
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    print("Obtained auth_code: ",auth_code)
    print("fetching token with TOKEN_URL ",TOKEN_URL," and client secret ",os.getenv('CLIENT_SECRET')," and auth response ",request.url)
    token = auth_code.fetch_token(token_url=TOKEN_URL, client_secret=os.getenv('CLIENT_SECRET'),
                                  authorization_response=request.url)

    print("Token: ",token)
    print("should have grabbed the token by now!")
    session['oauth_token'] = token
    with open('tokens.json', 'w') as json_file:
        json.dump(token, json_file)
    return redirect(url_for('.configure'))


#manual refresh of the token
@app.route('/refresh', methods=['GET'])
def webex_teams_webhook_refresh():

    r_api=None

    teams_token = session['oauth_token']

    # use the refresh token to
    # generate and store a new one
    access_token_expires_at=teams_token['expires_at']

    print("Manual refresh invoked!")
    print("Current time: ",time.time()," Token expires at: ",access_token_expires_at)
    refresh_token=teams_token['refresh_token']
    #make the calls to get new token
    extra = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': refresh_token,
    }
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=teams_token)
    new_teams_token=auth_code.refresh_token(TOKEN_URL, **extra)
    print("Obtained new_teams_token: ", new_teams_token)
    #store new token

    teams_token=new_teams_token
    session['oauth_token'] = teams_token
    #store away the new token
    with open('tokens.json', 'w') as json_file:
        json.dump(teams_token, json_file)

    #test that we have a valid access token
    r_api = WebexTeamsAPI(access_token=teams_token['access_token'])

    return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Webex Teams Bot served via Flask</title>
                       </head>
                   <body>
                   <p>
                   <strong>The token has been refreshed!!</strong>
                   </p>
                   </body>
                   </html>
                """)



@app.route('/configure')
def configure():

    global REDIRECT_URI
    global PUBLIC_URL
    global ACCESS_TOKEN

    if os.path.exists('tokens.json'):
        with open('tokens.json') as f:
            tokens = json.load(f)
    else:
        tokens = None

    if tokens == None or time.time()>(tokens['expires_at']+(tokens['refresh_token_expires_in']-tokens['expires_in'])):
        # We could not read the token from file or it is so old that even the refresh token is invalid, so we have to
        # trigger a full oAuth flow with user intervention
        REDIRECT_URI = PUBLIC_URL + '/callback'  # Copy your active  URI + /callback
        print("Using PUBLIC_URL: ",PUBLIC_URL)
        print("Using redirect URI: ",REDIRECT_URI)
        teams = OAuth2Session(os.getenv('CLIENT_ID'), scope=SCOPE, redirect_uri=REDIRECT_URI)
        authorization_url, state = teams.authorization_url(AUTHORIZATION_BASE_URL)

        # State is used to prevent CSRF, keep this for later.
        print("Storing state: ",state)
        session['oauth_state'] = state
        print("root route is re-directing to ",authorization_url," and had sent redirect uri: ",REDIRECT_URI)

        return redirect(authorization_url)
    else:
        # We read a token from file that is at least younger than the expiration of the refresh token, so let's
        # check and see if it is still current or needs refreshing without user intervention
        print("Existing token on file, checking if expired....")
        access_token_expires_at = tokens['expires_at']
        if time.time() > access_token_expires_at:
            print("expired!")
            refresh_token = tokens['refresh_token']
            # make the calls to get new token
            extra = {
                'client_id': os.getenv('CLIENT_ID'),
                'client_secret': os.getenv('CLIENT_SECRET'),
                'refresh_token': refresh_token,
            }
            auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=tokens)
            new_teams_token = auth_code.refresh_token(TOKEN_URL, **extra)
            print("Obtained new_teams_token: ", new_teams_token)
            # assign new token
            tokens = new_teams_token
            # store away the new token
            with open('tokens.json', 'w') as json_file:
                json.dump(tokens, json_file)


        session['oauth_token'] = tokens
        print("Using stored or refreshed token....")
        ACCESS_TOKEN=tokens['access_token']

    # now we have a valid access token and can configure the devices
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json; charset=utf-8"
    }

    # retrieve the devices in the org
    devices = webex_api.get_devices(BASE_URL, headers)

    headers["Content-Type"] = "application/json-patch+json"
    updated_devices = [] # saved the updated devices and their new configurations to pass to the front end
    for device in devices:
        # only configure Desk Pros
        if device["product"] == "Cisco Webex Desk Pro":
            update_config = webex_api.update_device_configuration(BASE_URL,
                                                                  headers,
                                                                  device["id"])
            # update_config holds the new configuration values of the device
            # if you add different configurations to the device, you will need to update the config values to display on the web page here
            new_device_config = {}
            config = []
            config.append("Bookings.ProtocolPriority: {}".format(update_config["items"]["Bookings.ProtocolPriority"]["value"]))
            config.append("Video.Input.Miracast.Mode: {}".format(update_config["items"]["Video.Input.Miracast.Mode"]["value"]))
            config.append("Video.Input.AirPlay.Mode: {}".format(update_config["items"]["Video.Input.AirPlay.Mode"]["value"]))
            config.append("WebEngine.Features.WebGL: {}".format(update_config["items"]["WebEngine.Features.WebGL"]["value"]))
            new_device_config["config"] = config
            new_device_config["name"] = device["displayName"]
            updated_devices.append(new_device_config)

    current_time = getSystemTime()

    return render_template("deviceconfigs.html", devices=updated_devices,
                           update_time=current_time)

#Main Function
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
