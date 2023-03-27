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
import requests, json

# Get Webex devices
def get_devices(base_url, headers):
    devices_endpoint = "/devices"
    devices_response = requests.get(base_url+devices_endpoint, headers=headers)
    devices = json.loads(devices_response.text)["items"]

    return devices


# Update the configurations of a device
# As written, this function will update the Bookings Protocol Priority to WebRTC, the Video Input Miracast Mode to Manual, the Video Input AirPlay Mode to On, and the Web Engine Feature WebGL to On
# this function uses the Patch request, so you are required to specify a Content-Type header with value application/json-path+json
def update_device_configuration(base_url, headers, device_id):
    configurations_endpoint = "/deviceConfigurations?deviceId={}".format(device_id)
    configurations_body = [
        {
            "op": "replace",
            "path": "Bookings.ProtocolPriority/sources/configured/value",
            "value": "WebRTC"
        },
        {
            "op": "replace",
            "path": "Video.Input.Miracast.Mode/sources/configured/value",
            "value": "Manual"
        },
        {
            "op": "replace",
            "path": "Video.Input.AirPlay.Mode/sources/configured/value",
            "value": "On"
        },
        {
            "op": "replace",
            "path": "WebEngine.Features.WebGL/sources/configured/value",
            "value": "On"
        }
    ]
    data_json = json.dumps(configurations_body)
    update_configurations_response = requests.patch(base_url+configurations_endpoint, headers=headers, data=data_json)
    updated_configurations = json.loads(update_configurations_response.text)

    return updated_configurations
