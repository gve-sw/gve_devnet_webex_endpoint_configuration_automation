# GVE DevNet Webex Endpoint Configuration Automation
This repository contains the code for a Python Flask app that pulls the Webex DeskPros associated with an organization and then deploys a common configuration to those devices periodically.

## Contacts
* Danielle Stacy

## Solution Components
* Python 3.11
* Flask
* Webex APIs

## Prerequisites
- **OAuth Integrations**: Integrations are how you request permission to invoke the Webex REST API on behalf of another Webex Teams user. To do this in a secure way, the API supports the OAuth2 standard which allows third-party integrations to get a temporary access token for authenticating API calls instead of asking users for their password. To register an integration with Webex Teams:
1. Log in to `developer.webex.com`
2. Click on your avatar at the top of the page and then select `My Webex Apps`
3. Click `Create a New App`
4. Click `Create an Integration` to start the wizard
5. Follow the instructions of the wizard and provide your integration's name, description, and logo
6. After successful registration, you'll be taken to a different screen containing your integration's newly created Client ID and Client Secret
7. Copy the secret and store it safely. Please note that the Client Secret will only be shown once for security purposes
8. Note that access token may not include all the scopes necessary for this prototype by default. To include the necessary scopes, select `My Webex Apps` under your avatar once again. Then click on the name of the integration you just created. Scroll down to the `Scopes` section. From there, select all the scopes needed for this integration. The scopes needed for this integration are spark-admin:devices_read and spark-admin:devices_write.

> To read more about Webex Integrations & Authorization and to find information about the different scopes, you can find information [here](https://developer.webex.com/docs/integrations)

## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_webex_endpoint_configuration_automation.git`
2. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
3. Install the requirements with the command `pip3 install -r requirements.txt`.
4. Provide the Client ID and Client Secret that you retrieved in the Prerequisites section in the .env file.
```python
CLIENT_ID = "ID goes here"
CLIENT_SECRET = "secret goes here"
```

## Usage
To start the web app that is written in the file `app.py` use the command:
```
$ flask run
```
Then access the app in your browser of choice at the address `http://localhost:5000`. From here, you will be asked to login to the web app with your Webex account. Login with the Webex account that you created the Webex integration with.

![/IMAGES/login_prompt.png](/IMAGES/login_prompt.png)

![/IMAGES/webex_login.png](/IMAGES/webex_login.png)

Once you have gone through the login process, the backend will retrieve the devices and modify their configurations and you will be redirected to the page where the configured devices are displayed.

![/IMAGES/devices_configured.png](/IMAGES/devices_configured.png)

While this web page is open, it will update periodically, triggering the configuration changes. Currently, the web page will update every hour. To change how frequently the web page updates, look at the `setTimeout` function in the `deviceconfigs.html` template.

As written, the script will only update the Bookings Protocol Priority to WebRTC, the Video Input Miracast Mode to Manual, the Video Input Air Play Mode to On, and the Web Enging Feature WebGL to On. To change these configurations or add more configuratins, update the function `update_device_configurations` defined at line 28 in `webex_api.py` and to reflect those changes in the front end, make sure to update the code in the function `configure` in `app.py`, specifically the code in lines 235-238. 
Additionally, the code will configure only the Webex Desk Pros in the environment. To change this feature, update or remove the if statement in the `configure` function in `app.py` at line 227.

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
