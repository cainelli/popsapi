from marshmallow import Schema, fields

class ServersSchema(Schema):
  name = fields.String(required=True)
  tags = fields.String(required=True)
  ip = fields.String(required=True)
  


class EnvironmentSchema(Schema):
  name = fields.String(required=True)
  company = fields.String(required=True)
  email = fields.String(required=True)
  servers = fields.Nested(ServersSchema, many=True)
  create_time = fields.DateTime()

class SlackSchema(Schema):
  team_id = fields.String(required=True)
  team_domain = fields.String(required=True)
  command = fields.String(required=True)
  environment = fields.String(required=True)
  channel_id = fields.String(required=True)


class EventQueueSchema(Schema):
  active = fields.Integer(required=True)
  deferred = fields.Integer(required=True)
  hold = fields.Integer(required=True)
  bounce = fields.Integer(required=True)

class EventTopSendersSchema(Schema):
  email = fields.String(required=True)
  quantity = fields.Integer(required=True)

class EventSchema(Schema):
  #create_time = fields.DateTime()
  queue = fields.Nested(EventQueueSchema, many=False, required=True, strict=True)
  topsenders = fields.Nested(EventTopSendersSchema, many=True, required=True, strict=True)
  no_event = fields.String(many=True)
  #server = fields.String()
  #environment = fields.String()

class TaskSchema(Schema):
  taskid = fields.String(required=True)
  server = fields.String(required=True)
  action = fields.String(required=True)
  destination = fields.String(required=True)
  status = fields.String(required=True)
  response = fields.String()
  environment = fields.String()
