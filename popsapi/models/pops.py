from flask.ext.mongoengine import MongoEngine
from datetime import datetime
from popsapi.components.common import cfg

db = MongoEngine()

class Servers(db.EmbeddedDocument):
  name = db.StringField(max_length=255, unique=True)
  tags = db.StringField(max_length=255)
  ip = db.StringField(max_length=255)



class Environment(db.Document):
  name = db.StringField(max_length=100, required=True, unique=True)
  company = db.StringField(max_length=100)
  email = db.StringField(max_length=100)
  servers = db.ListField(db.EmbeddedDocumentField(Servers))
  create_time = db.DateTimeField(default=datetime.utcnow)

  meta = {
    'allow_inheritance': True,
  }

class Slack(db.Document):
  token = db.StringField(max_length=255, required=True)
  team_id = db.StringField(max_length=100, required=True)
  team_domain = db.StringField(max_length=100, required=True)
  channel_id = db.StringField(max_length=100, required=True)

  command = db.StringField()
  environment = db.ListField()

class Task(db.Document):
  create_time = db.DateTimeField(default=datetime.utcnow)
  taskid = db.StringField(required=True)
  action = db.StringField(max_length=100, choices=cfg['slack']['actions'], required=True)
  destination = db.StringField(max_length=100, required=True)
  status = db.StringField(max_length=100, choices=cfg['slack']['status'],  required=True)
  response = db.StringField()
  environment = db.StringField()
  server = db.StringField()

  meta = {
  'indexes': [
    {'fields': ['create_time'], 'expireAfterSeconds': cfg['mongo']['tasks']['expires']}
  ]
  }

class EventQueue(db.EmbeddedDocument):
  active = db.IntField()
  deferred = db.IntField()
  hold = db.IntField()
  bounce = db.IntField()

class EventTopSender(db.EmbeddedDocument):
  email = db.EmailField()
  quantity = db.IntField()

class Event(db.Document):
  create_time = db.DateTimeField(required=True, default=datetime.utcnow)
  queue = db.EmbeddedDocumentField(EventQueue, required=True)
  topsenders = db.ListField(db.EmbeddedDocumentField(EventTopSender))
  environment = db.StringField()
  server = db.StringField(unique=True, required=True)

  meta = {
    'indexes': [
      {'fields': ['create_time'], 'expireAfterSeconds': cfg['mongo']['events']['expires']}
    ]
  }
