import json, ast
from flask.ext.restful import reqparse, request, Resource, abort
from popsapi.resources.base import BaseResource, abort_if_obj_doesnt_exist
from popsapi.components.common import logger
from popsapi.models import Environment, EnvironmentSchema, Servers

class EnvironmentResource(BaseResource):
  def __init__(self):
    filters = ['name', 'server']
    super(EnvironmentResource, self).__init__(filters)
  def get(self, target_environment):
    environment = abort_if_obj_doesnt_exist(self.filter_by, str(target_environment), Environment, blame_for_all=False)
    hasmany = False
    if type(environment) == list:
      hasmany = True
    environment_result = EnvironmentSchema(many=hasmany).dump(environment)

    return {
      'response' : environment_result.data
    }, 200

  def delete(self, target_environment):
    environment = abort_if_obj_doesnt_exist(self.filter_by, target_environment, Environment)
    environment.delete()

    return {
      'response' : 'sucessfully deleted [%s]' % target_environment
    }, 204

  def post(self, target_environment):
    query = { 'name' : str(target_environment) }
    if Environment.objects.filter(name= str(target_environment)):
      abort(400, message='The environment {} already exists'.format(target_environment))

    self.parser.add_argument('company', type=str, required=True)
    self.parser.add_argument('email', type=str, required=True)
    self.parser.add_argument('servers', type=str, action='append')
    reqdata = self.parser.parse_args()

    environment = Environment(
        name=target_environment, 
        company=reqdata['company'],
        email=reqdata['email'])

    if reqdata['servers']:
      for srv_dict in  reqdata['servers']:
        server = ast.literal_eval(srv_dict)
        servers = Servers(
              name=server['name'],
              tags=server['tags'],
              ip=server['ip']
        
         )
        environment.servers.append(servers)

    try:
      environment.save()
      return {
        'response': 'environment sucessfully created [%s]' % target_environment
      }, 201
    except Exception, e:
      abort(500, message='Error trying to create environment {}'.format(target_environment))
