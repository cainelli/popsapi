import json, ast
from flask.ext.restful import reqparse, request, Resource, abort
from popsapi.resources.base import BaseResource, abort_if_obj_doesnt_exist
from popsapi.models import Environment, EventSchema, Event, EventTopSender
from popsapi.components.common import cfg, logger

class QueueResource(BaseResource):
  def __init__(self):
    filters = ['name', 'server', 'tag']
    super(QueueResource, self).__init__(filters)
  def get(self, target_environment, reqdata=None):

    environment = abort_if_obj_doesnt_exist(self.filter_by, str(target_environment), Environment, blame_for_all=False)
    
    ret_data = {
      'topsenders': {},
      'queue' : {
        'active' : 0,
        'bounce' : 0,
        'hold' : 0,
        'deferred' : 0
      },
      'no_events': [],
      'servers' : []
    }

    buffer_tops = {}

    if not reqdata:
      self.parser.add_argument('tag', type=str, action='append', location='args')
      self.parser.add_argument('server', type=str, action='append', location='args')
      reqdata = self.parser.parse_args()
    
    
    data = []
    for server in environment.servers:
      # filter by server
      if reqdata['server'] and server.name not in reqdata['server']:
        continue
      # filter by tag
      if reqdata['tag'] and server.tags  not in reqdata['tag']:
        continue

      try:
        events = Event.objects(server = server.name, environment = environment.name)

        # let me know when an server doesn't have any event stored.
        if not events:
          ret_data['no_events'].append(server.name)
        else:
          ret_data['servers'].append(server.name)
        for event in events:
          # sum queues
          ret_data['queue']['deferred'] += event.queue.deferred
          ret_data['queue']['active'] += event.queue.active
          ret_data['queue']['hold'] += event.queue.hold
          ret_data['queue']['bounce'] += event.queue.bounce
          
          # buffer for sorting top senders latter.
          for sender in event.topsenders:
            try:
              buffer_tops[sender.email] += sender.quantity
            except:
              buffer_tops[sender.email] = sender.quantity
      except Exception, e:
        logger.error('Error trying to retrieve event %s' %  e)
        ret_data['no_events'].append(server.name)
        continue


    # sort dictionary
    topsenders = {}
    for sender, qtd in sorted(buffer_tops.iteritems(),key=lambda (k,v): (v,k), reverse=True)[:3]:
      topsenders[sender] = qtd
    ret_data['topsenders'] = topsenders

    return {
      'response' : ret_data
    }, 200

  def post(self, target_environment):
    self.parser.add_argument('topsenders', type=str, action='append', required=True)
    self.parser.add_argument('queue', type=str, required=True)
    self.parser.add_argument('server', type=str , required=True)
    reqdata = self.parser.parse_args()
    

    event = Event(
      queue = ast.literal_eval(reqdata['queue']),
      server = reqdata['server'],
      environment = target_environment
    )


    for sender_dict in reqdata['topsenders']:
      sender = ast.literal_eval(sender_dict)
      topsender = EventTopSender(email = sender['email'], quantity = sender['quantity'])
      event.topsenders.append(topsender)

    try:
      # if an event exist for that server it will remove first and then create a new one.
      self.delete(target_environment, reqdata['server'])
      event.save()

      return {
        'response': 'event sucessfully created [%s]' % reqdata['server']
      }, 201
    except Exception, e:
      logger.error('Error trying to create event %s: %s' % (reqdata['server'], e))
      abort(500, message='Error trying to create event {}'.format(reqdata['server']))

  def delete(self, target_environment, server=''):
    environment = abort_if_obj_doesnt_exist(self.filter_by, str(target_environment), Environment, blame_for_all=False)

    self.parser.add_argument('server', type=str, required=True)
    reqdata = self.parser.parse_args()

    if reqdata['server']:
      server = reqdata['server']

    if server:
      events = Event.objects(server=str(server), environment=str(environment.name))
    else:
      events = Event.objects(environment=str(environment.name))

    for event in events:
      event.delete()

    return {
      'response' : 'sucessfully deleted [%s]' % target_environment
    }, 204