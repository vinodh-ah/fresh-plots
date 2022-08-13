from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Column, create_engine, ForeignKey
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from sqlalchemy.ext.declarative import declarative_base
import falcon
import json



class UserDao:
    def __init__(self, first, last, handle, password, phone, email):
        self.first_name = first
        self.last_name = last
        self.phone = phone
        self.email = email
        self.handle = handle
        self.password = password

class UserResource:
    config = {
        "connection_string":'mysql://scale-app:scale-123*!@etcher.cwomkqy1rxjg.us-west-1.rds.amazonaws.com/scale-app'
    }
    CONNECTION_URL = 'mysql://scale-app:scale-123*!@etcher.cwomkqy1rxjg.us-west-1.rds.amazonaws.com/scale-app'
    def __init__(self):
        self.engine = create_engine(UserResource.CONNECTION_URL)
        self.session = Session(self.engine)

    async def on_get(self, req, resp):
        try:
            with self.engine.connect() as con:
                rs = con.execute('SELECT * FROM user')

            result = rs.__dict__
            for row in rs:
                result = row._mapping

            #row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            userDao = UserDao(result.user_id, result.first_name, result.last_name, result.phone, result.email)
            

        except Exception as ex:
            self.logger.error(ex)

            description = ('Aliens have attacked our base! We will '
                           'be back as soon as we fight them off. '
                           'We appreciate your patience.')

            raise falcon.HTTPServiceUnavailable(
                title='Service Outage',
                description=description,
                retry_after=30)
        
        resp.content_type = falcon.MEDIA_JSON
        resp.text = json.dumps(userDao.__dict__)
        resp.context.result = result
        resp.status = falcon.HTTP_200

    async def validate_new_user_request(first, last, phone,email):
        if first is None or last is None or phone is None or email is  None:
            msg = ('New user request does not have all the required fields.')
        else:
            raise falcon.HTTPPayloadTooLarge(
                title='Incomplete new usr request', description=msg)
    
    async def on_post(self, req, resp):
        try:
            userPayload = json.loads(req.bounded_stream._buffer)
        except json.decoder.JSONDecodeError:
            raise falcon.HTTPBadRequest(
                title="Bad request", description="Bad input, must be valid json."
            )

        userDao = UserDao(userPayload['first_name'], userPayload['last_name'], 
                          userPayload['handle'],userPayload['password'],
                          userPayload['phone'], userPayload['email'])
        query = f'insert into user (first_name, last_name, user_handle, password, phone, email) values("{userDao.first_name}", "{userDao.last_name}","{userDao.handle}","{userDao.password}", "{userDao.phone}", "{userDao.email}")'
        #validate_new_user_request(userDao)

        try:
            with self.engine.connect() as con:
                rs = con.execute(query)
        except Exception as ex:
            self.logger.error(ex)
            raise falcon.HTTPServiceUnavailable(
                title='Service Outage',
                description='Unable to create new user',
                retry_after=30)
    
    async def on_get_user(self, req, resp, user_id):
        query = f'select * from user where user_id = {user_id}'
        try:
            with self.engine.connect() as con:
                rs = con.execute(query)

            result = rs.__dict__
            for row in rs:
                result = row._mapping

            userDao = UserDao(result.user_id, result.first_name, result.last_name, result.phone, result.email)
            

        except Exception as ex:
            self.logger.error(ex)

            description = ('Aliens have attacked our base! We will '
                           'be back as soon as we fight them off. '
                           'We appreciate your patience.')

            raise falcon.HTTPServiceUnavailable(
                title='Service Outage',
                description=description,
                retry_after=30)
        
        resp.content_type = falcon.MEDIA_JSON
        resp.text = json.dumps(userDao.__dict__)
        resp.context.result = result
        resp.status = falcon.HTTP_200
