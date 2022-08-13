'''
The set of classes here are essentially our abstraction over the data store. The Video class is a simple
data structure to keep some meta data handy
'''
import asyncio
from asyncio.log import logger
import datetime
import io
import os.path

import aiofiles
import falcon
from PIL import Image
import boto3
import logging
import boto3
from botocore.exceptions import ClientError

class Video:
    def __init__(self, config, content_id, size):
        self.config = config
        self.content_id = content_id
        self.size = size
        self.modified = datetime.datetime.utcnow()

    @property
    def path(self):
        return os.path.join(self.config.storage_path, self.content_id+".MOV")

    @property
    def uri(self):
        return f'/content/{self.content_id}.MOV'

    def serialize(self):
        return {
            'id': self.content_id,
            'video': self.uri,
            'modified': falcon.dt_to_http(self.modified),
            'size': self.size,
        }

'''
This is an abstraction over the underlying storage. Again for the sake of this exercise, it is not
necessary to figure how to store this data in some kind of block storage. For now, we will treat the
file system as such.

There is also a mini, hacked up caching layer here - as new videos get added we store the metadata in a
dictionary. When a request to list videos comes through we can just return the dictionary. Obviously if
we ever have to restart the app it won't "remember" any of that :-( and will suggest there are no video files.
'''
class Store:
    def __init__(self, config):
        self.config = config
        self._videos = {}
        self.botoClient = boto3.client('s3')
        self.s3Bucket = 'fresh-plots'
        for root, dirs, files in os.walk(self.config.storage_path):
            for name in files:
                if name.endswith((".MOV")):
                    # whatever
                    id = name.split('.MOV')[0]
                    video = Video(self.config, id, os.path.getsize(self.config.storage_path+'/'+ name))
                    self._videos[id] = video

    def get(self, content_id):
        return self._videos.get(content_id)

    def get_uri(self, content_id):
        return str(os.path.join(self.config.storage_path, content_id+".MOV"))

    def list_videos(self):
        return sorted(self._videos.values(), key=lambda item: item.modified)

    async def save_block_store(self, content_id, data):
        await self.save(content_id, data)
        try:
            #self.botoClient.put_object(Body=data, Bucket=self.s3Bucket, Key=content_id+'.mp4')
            self.botoClient.upload_file(self.config.storage_path+'/'+content_id+'.mp4', 'fresh-plots',content_id+'.mp4')
            
        except Exception as ex:
            logging.error(ex)
        
        stored = Video(self.config, content_id, len(data))
        self._videos[content_id] = stored
        return stored

    async def save(self, content_id, data):
        path = os.path.join(self.config.storage_path, content_id)
        async with aiofiles.open(path+".mp4", 'wb') as output:
            await output.write(data)

        stored = Video(self.config, content_id, len(data))
        self._videos[content_id] = stored
        return stored