import json, ast, uuid
from flask.ext.restful import reqparse, request, Resource, abort
from popsapi.resources.base import BaseResource, abort_if_obj_doesnt_exist
from popsapi.models import TaskSchema, Environment, Task
from popsapi.components.common import cfg, logger

class TaskResource(BaseResource):
  def __init__(self):
    filters = ['name']
    super(TaskResource, self).__init__(filters)

  def get(self, target_environment, reqdata=None):
    environment = abort_if_obj_doesnt_exist(self.filter_by, str(target_environment), Environment, blame_for_all=False)

    if not reqdata:
      self.parser.add_argument('server', type=str, action='append', location='args')
      self.parser.add_argument('status', type=str, action='append', location='args')
      self.parser.add_argument('action', type=str, action='append', location='args')
      reqdata = self.parser.parse_args()

    data = []
    for server in environment.servers:
      # filter by server
      if reqdata['server'] and server.name not in reqdata['server']:
        continue
      try:
        tasks = Task.objects(server = server.name, environment = environment.name)

        for task in tasks:
          # filter status
          if reqdata['status'] and task.status not in reqdata['status']:
            continue
          # filter action
          if reqdata['action'] and task.action not in reqdata['action']:
            continue

          data.append(TaskSchema().dump(task).data)
      except Exception, e:
        logger.warn('Error trying to retrieve task %s' %  e)
    
    return data, 200

  def put(self, target_environment):
    environment = abort_if_obj_doesnt_exist(self.filter_by, str(target_environment), Environment, blame_for_all=False)

    self.parser.add_argument('taskid', type=str, required=True)
    self.parser.add_argument('status', type=str)
    self.parser.add_argument('response', type=str)

    reqdata = self.parser.parse_args()
  
    try:
      task = Task.objects(taskid=str(reqdata['taskid'])).first()
      if reqdata['status']:
        task.update(status = str(reqdata['status']))

      if reqdata['response']:
        task.update(response = str(reqdata['response']))

      return {
       'response': 'task sucessfully updated taskid:[%s]' % reqdata['taskid']
      }, 201
    except Exception, e:
      logger.error('Error trying to update task %s' %  e)
      abort(404, message='Error trying to update task %s' % reqdata['taskid'])

  def post(self, target_environment, reqdata=None):

    environment = abort_if_obj_doesnt_exist(self.filter_by, str(target_environment), Environment, blame_for_all=False)

    
    if not reqdata:
      self.parser.add_argument('server', type=str)
      self.parser.add_argument('action', type=str, required=True)
      self.parser.add_argument('destination', type=str, required=True)
      self.parser.add_argument('status', type=str, default='pending')
      self.parser.add_argument('response', type=str, default='')
      reqdata = self.parser.parse_args()

    # when called from inside reqdata is already filled so the above if block 
    # is skipped and cannot set default value of pending if not defined. 
    # The code bellow check and set it.
    if 'status' not in reqdata:
      reqdata['status'] = 'pending'
    if 'response' not in reqdata:
      reqdata['response'] = ''


    # if server not null it will create only one task itself. Otherwise
    # will create one task for each environment's server.
    servers = []
    if reqdata['server']:
      servers = [reqdata['server']]
    else:
      for server in environment.servers:
        print 'server:%s\n\n\n\n\n\n\n\n\n' % server.name
        servers.append(server.name)

    for server in servers:

      taskid = str(uuid.uuid4())
      task = Task(
        taskid = taskid,
        action = reqdata['action'],
        destination = reqdata['destination'],
        status = reqdata['status'] or 'pending',
        response = reqdata['response'] or '',
        environment = environment.name,
        server = server
      )

      # it will try sava or update task.  
      try:
        task.save()
        
      except Exception, e:
        logger.error('Error trying to create task %s' %  e)
        abort(500, message='Error trying to create task')

      return {
        'response': 'task sucessfully created taskid:[%s]' % taskid
      }, 201
