from flask import url_for
import requests
import json
from config import Config


def calendly_request(method, url, data=None):
    headers = {'X-TOKEN': Config.CALENDLY_KEY}
    r = None
    if method == 'GET':
        r = requests.get(url, headers=headers, data=data)
    elif method == 'POST':
        r = requests.post(url, headers=headers, data=data)
    return r

def calendly_create_webhook(events=['invitee.created', 'invitee.canceled']):
    data = {'url': url_for('main.calendly', _external=True), 'events[]': events}
    r = calendly_request('POST', 'https://calendly.com/api/v1/hooks', data=data)
    return r.json()

def calendly_check_webhook():
    r = calendly_request('GET', 'https://calendly.com/api/v1/hooks')
    return r