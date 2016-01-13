from popsapi.resources.base import BaseResource
from popsapi.models import Slack, SlackSchema
from popsapi.components.slackcmd import SlackCommand
from popsapi.components.common import logger
from flask.ext.restful import abort


class SlackCommandResource(BaseResource):
  def __init__(self):
    filters = ['name']

    super(SlackCommandResource, self).__init__(filters)

  def get(self):
    self.parser.add_argument('token', type=str, location='args', required=True)
    self.parser.add_argument('team_id', type=str, location='args')
    self.parser.add_argument('team_domain', type=str, location='args')
    self.parser.add_argument('channel_id', type=str, location='args')
    self.parser.add_argument('channel_name', type=str, location='args')
    self.parser.add_argument('user_id', type=str, location='args')
    self.parser.add_argument('user_name', type=str, location='args')
    self.parser.add_argument('command', type=str, location='args')
    self.parser.add_argument('text', type=str, location='args')
    reqdata = self.parser.parse_args()

    # 
    # validation
    slack = Slack.objects(token=reqdata['token'], 
                          team_id=reqdata['team_id'],
                          channel_id=reqdata['channel_id']).first()
    
    print "token:%s\nteam_id:%s\nchannel_id:%s\ncommand:%s\ntext:%s\n" % (reqdata['token'], reqdata['team_id'], reqdata['channel_id'], reqdata['command'], reqdata['text'])
    if slack:
      try:
        slackcmd = SlackCommand(slack)
        res = slackcmd.run(reqdata['command'], reqdata['text'], 'get')
      except Exception, e:
        logger.error('something went wrong trying to execute slack command: %s' % e)
        return {
          'response' : 'Internal Server Error'
        }, 500


      return res, 200
    else:
      abort(401, message='Unauthorized: insufficient privileges')

  def post(self):
    self.parser.add_argument('token', type=str, required=True)
    self.parser.add_argument('team_id', type=str)
    self.parser.add_argument('team_domain', type=str)
    self.parser.add_argument('channel_id', type=str)
    self.parser.add_argument('channel_name', type=str)
    self.parser.add_argument('user_id', type=str)
    self.parser.add_argument('user_name', type=str)
    self.parser.add_argument('command', type=str)
    self.parser.add_argument('text', type=str)
    reqdata = self.parser.parse_args()

    # 
    # validation
    slack = Slack.objects(token=reqdata['token'], 
                          team_id=reqdata['team_id'],
                          channel_id=reqdata['channel_id']).first()
    
    print "token:%s\nteam_id:%s\nchannel_id:%s\ncommand:%s\ntext:%s\n" % (reqdata['token'], reqdata['team_id'], reqdata['channel_id'], reqdata['command'], reqdata['text'])
    if slack:
      try:
        slackcmd = SlackCommand(slack)
        res = slackcmd.run(reqdata['command'], reqdata['text'], 'post')
      except Exception, e:
        logger.error('something went wrong trying to execute slack command: %s' % e)
        return {
          'response' : 'Internal Server Error'
        }, 500


      return res, 200
    else:
      abort(401, message='Unauthorized: insufficient privileges')

class SlackResource(BaseResource):
  def __init__(self):
    filters = ['name']
    super(SlackResource, self).__init__(filters)

  def get(self):
    self.parser.add_argument('team_id', type=str, location='args')
    self.parser.add_argument('team_domain', type=str, location='args')
    self.parser.add_argument('channel_id', type=str, location='args')
    reqdata = self.parser.parse_args()

    if reqdata['team_id']:
      slack = Slack.objects(team_id = reqdata['team_id'])
    elif reqdata['team_domain']:
      slack = Slack.objects(team_domain = str(reqdata['team_domain']))
    elif reqdata['channel_id']:
      slack = Slack.objects(channel_id = reqdata['channel_id'])

    slack_result = SlackSchema(many=True).dump(slack)

    return {
      'response' : slack_result.data
    }, 200


  def post(self):
    self.parser.add_argument('token', type=str, required=True)
    self.parser.add_argument('team_domain', type=str, required=True)
    self.parser.add_argument('team_id', type=str, required=True)
    self.parser.add_argument('channel_id', type=str, required=True)
    self.parser.add_argument('command', type=str, required=True)
    self.parser.add_argument('environment', type=str, action='append', required=True)
    reqdata = self.parser.parse_args()

    if Slack.objects(team_id = reqdata['team_id'], channel_id = reqdata['channel_id'], token=reqdata['token']):
      abort(400, message='team:[%s] and channel:[%s] already configured. Update it instead.' %
        (reqdata['team_id'], reqdata['channel_id']))

    slack = Slack(
      token = reqdata['token'],
      team_domain = reqdata['team_domain'],
      team_id = reqdata['team_id'],
      channel_id = reqdata['channel_id'],
      command = reqdata['command'],
      environment = reqdata['environment']
    )

    try:
      slack.save()
      return {
        'response': 'credentials sucessfully created for channel:[%s]' % reqdata['channel_id']
      }, 201
    except Exception, e:
      logger.error('could not create channel:[%s] credentials: %s' % (reqdata['channel_id'], e)) 
      abort(500, message='could not create team credentials.')

  def delete(self):
    self.parser.add_argument('team_id', type=str, required=True)
    self.parser.add_argument('channel_id', type=str, required=True)
    
    reqdata = self.parser.parse_args()

    slack = Slack.objects(team_id = reqdata['team_id'], channel_id = reqdata['channel_id'])
    if slack:
      try:
        slack.delete()
        return {
          'response' : 'sucessfully deleted [%s]' % reqdata['team_id']
        }, 204
      except Exception, e:
        logger.error('c')
        abort(501, message='could not delete slack credentials %s.' % reqdata['team_id'])
    else:
        abort(404, message='object not found.')
