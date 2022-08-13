
import mimetypes
import falcon
import aiohttp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Column, create_engine, ForeignKey
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
import json
from storage_config import Config
from video_store import Store
import os
import io
import asyncio
import aiofiles
import boto3

class VideoResource:
    def __init__(self):
        self.config = Config()
        self.store = Store(self.config)
        
    async def on_post(self, req, resp):
        '''
        OK, this is NOT the ideal implementation at all - in the system design
        creating/uploading a new video was a pipeline - with us simply accepting the media
        first, ingesting it, encoding it, generating thumbnails from it etc. We are skipping all of that
        here.
        
        What would be useful to learn here is the complexity involved in uploading large files, performance
        and how it shows up in the UI experience
        '''
        data = await req.stream.read()
        content_id = str(self.config.uuid_generator())
        saved_video = await self.store.save_block_store(content_id, data)

        resp.location = saved_video.uri
        resp.media = saved_video.serialize()
        resp.status = falcon.HTTP_201

    async def on_get(self, req, resp):
        '''
        this api just returns the list of videos
        '''
        video_list = self.store.list_videos()
        ds = {item.content_id: item.size for item in video_list}
        resp.media = ds

