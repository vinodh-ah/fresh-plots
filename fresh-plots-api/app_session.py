'''
For our purposes we need the client to submit a user name/password and swap it out for a session/access token
of some sort. The client is expected to pass this access token in subsequent calls.
In real life no one will implement auth this way (PLEASE DON'T!) but this is good enough for the purposes
of our demo
'''
import falcon
import json
import uuid
from sqlalchemy import Integer, Column, create_engine, ForeignKey
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session

class TokenGenerator:
    DEFAULT_UUID_GENERATOR = uuid.uuid4
    def __init__(self):
        self.uuid_generator = TokenGenerator.DEFAULT_UUID_GENERATOR

class Credentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class AppSession:
    CONNECTION_URL = 'mysql://scale-app:scale-123*!@etcher.cwomkqy1rxjg.us-west-1.rds.amazonaws.com/scale-app'
    def __init__(self):
        self.engine = create_engine(AppSession.CONNECTION_URL)
        self.session = Session(self.engine)

    async def on_post(self, req, resp):
        payload = json.loads(req.bounded_stream._buffer)
        credentials = Credentials(payload['username'], payload['password'])
        query = f'select * from user where user_handle = "{credentials.username}"'
        token = ''
        try:
            with self.engine.connect() as con:
                rs = con.execute(query)

            result = rs.__dict__
            for row in rs:
                result = row._mapping
            
            tokenGenerator = TokenGenerator()
            if result.password.__eq__(credentials.password):
                token = str(tokenGenerator.uuid_generator())
            
            responseJson = {'token':f'{token}'}
            resp.content_type = falcon.MEDIA_JSON
            resp.text = json.dumps(responseJson)
            resp.context.result = responseJson
            resp.status = falcon.HTTP_200

        except Exception as ex:
            self.logger.error(ex)
            raise falcon.HTTPServiceUnavailable(
                title='Service Outage',
                description='Unable to create new user',
                retry_after=30)