'''
This is the main entry point for FreshPlots - the name of our social video sharing app!

This app is built using Python (3.7+ compatible) app built with Falcon web framework to power the
underlying RESTful notations. 

The purpose of building this app is just to get a sense of what the unknown, difficult estimate aspects
are of building a social video sharing app. This is NOT intended to be production quality (and it's NOT).
The other factor I wanted to explore was the time complexity involved - I am a python novice and wanted
to use this exercise to see how big the ramp time would be. I spent 3.5 hours building this plus an additional
couple of hours of research work that started and finished before I went down this path.

A few reasons why I chose Falcon for this demo:

1. Given the resource intensive nature of this app performance and efficiency are critical as called
out in the system design doc. 

2. Falcon is lightweight and super fast. You can see more details here: https://falconframework.org/#sectionBenchmarks

'''

import json
import logging
import uuid

import falcon
import falcon.asgi
import httpx
from auth_middleware import AuthMiddleware
from flask_sqlalchemy import SQLAlchemy
from user import UserResource
from video_resource import VideoResource
from app_session import AppSession


class JSONTranslator:
    # NOTE: Normally you would simply use req.get_media() and resp.media for
    # this particular use case; this example serves only to illustrate
    # what is possible.

    async def process_request(self, req, resp):
        # NOTE: Test explicitly for 0, since this property could be None in
        # the case that the Content-Length header is missing (in which case we
        # can't know if there is a body without actually attempting to read
        # it from the request stream.)
        if req.content_length == 0:
            # Nothing to do
            return

        body = await req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest(title='Empty request body',
                                        description='A valid JSON document is required.')

        try:
            req.context.doc = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            description = ('Could not decode the request body. The '
                           'JSON was incorrect or not encoded as '
                           'UTF-8.')

            raise falcon.HTTPBadRequest(title='Malformed JSON',
                                        description=description)

    async def process_response(self, req, resp, resource, req_succeeded):
        if not hasattr(resp.context, 'result'):
            return

        resp.text = json.dumps(resp.context.result)


# The app instance is an ASGI callable
app = falcon.asgi.App(middleware=[
    AuthMiddleware(),
])

# Add the routes in the app. In our case, we have the following:
#1. Create user, get a specific user's data such as name, email
#2. upload a new video
#3. Get a list of available videos
#4. The video playback is going to be served from a different app - more details on that separately
user = UserResource()
app.add_route('/user', user)
app.add_route('/user/{user_id}', user, suffix='user')
app.add_route('/video', VideoResource())
app.add_route('/login', AppSession())

