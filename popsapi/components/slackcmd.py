import argparse, requests
from popsapi.models import db, Slack, Environment #only required for dev.
from popsapi.components.common import cfg, logger # only required for dev
from popsapi.resources import QueueResource, TaskResource
from flask import Flask # only required for dev.
from flask.ext.restful import abort


    
class SlackCommand(object):
  def __init__(self, slack):
    """ 
    Description:
      Initializes valididating the proper permissions to execute a command.

    Args:
      slack (object): popsapi.models.Slack object. Used to load permissions.
    """
    
    self.is_valid = False
    # check if slack object is exists
    if not slack:
      abort(401, message='Unauthorized')

    # auth ok
    self.is_valid = True
    self.slack = slack

  def _slack_usage(self):
    return "      Supported Custom Slack Commands:\
        getqueue:   Get queues from single/multiple servers or entire environment.\
                  You may use filters throught tags.\
                \
                  slack usage: /getqueue [options]\
                  options:\
                    -environment [environment] : environment name.\
                    -server [environment] : server name.\
                    -tag [tag] : tag name.\
                  \
                  examples:\
                    /getqueue\
                    /getqueue -environment corporation\
                    /getqueue -server mta-in.mailserver.com -server mta-out.mailserver.com\
                    /getqueue -environment corporation -tag inbound\
                    /getqueue -tag outbound -tag inbound\
\
        gettasks:   Get tasks from single/multiple servers or entire environment. You may \
                  apply filters in your search.\
      \
                  slack usage: /gettasks [options]\
                  options:\
                    -environment [environment] : environment name.\
                    -server [environment] : server name.\
                    -status [pending|completed|error] : task status.\
                    -action %s : task action.\
                  examples:\
                    /gettasks\
                    /gettasks -environment corporation -status pending\
                    /gettasks -server mta-in.mailserver.com\
                    /gettasks -action purge\
                    /gettasks -environment -action purge\
  " % cfg['slack']['actions']

  def run(self, cmd, args, method):
    """
    Description:
      This method parse the command and arguments from Slack and use POPS API to retrieve information or create tasks.

    Args:
      cmd (str) : 'command' requested. 'command' payload or url arg.
      args (str)) : command arguments. 'text' payload or url arg.
    """
    if not self.is_valid:
      logger.error('slack object not valid is_valid = %s' % self.is_valid)
      abort(401, message='Unauthorized')
    
    # check if slack object has sufficient permission to run the command.
    logger.info("trying:[%s == %s] token[%s]" % (cmd, self.slack.command, self.slack.token))
    if not cmd == self.slack.command:
      logger.error('Unauthorized: command allowed in slack object: %s' % cmd)
      abort(401, message='Unauthorized')
    

    # Parsing arguments
    reqdata = {}
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    # common arguments
    parser.add_argument('-environment', action='append')
    parser.add_argument('-server', action='append')

    if cmd == '/getqueue':
      parser.add_argument('--tag', action='append')
      resource = QueueResource()
    elif cmd == '/gettasks':
      parser.add_argument('-action', action='append')
      parser.add_argument('-status', action='append')
      resource = TaskResource()
    elif cmd == '/createtask':
      parser.add_argument('-action', required=True)
      parser.add_argument('-user', required=True)
      resource = TaskResource()
    else:
      logger.error('command not supported: %s' % cmd )
      abort(400, message='command not supported %s' % cmd)
    try:
      argument = parser.parse_args(args.split())
    except Exception, e:
      logger.error('something went wrong: %s' % e)
      return self._slack_usage()

    # definie environments to lookup.
    environments = []
    all_rule = False
    # all environments allowed
    if 'all' in self.slack.environment:
      for envobj in Environment.objects.only('name'):
        environments.append(str(envobj.name))
      all_rule = True
    # when not specified takes the ones in slack object.
    if not argument.environment:
      environments = self.slack.environment
    # only lookup the environments specified.
    else:
      environments = argument.environment

    for environment in environments:
      # check if command can be performed in the current environment scope.
      if environment not in self.slack.environment and all_rule == False:
        logger.error('Forbidden. Environment not allowed: %s' % environment)
        abort(403, message='Forbidden: Environment not allowed %s' % environment)

      
      # add server
      try:
        reqdata['server'] = argument.server
      except: pass
      
      # add tag
      try:
        reqdata['tag'] = argument.tag
      except: pass

      # add action
      try:
        reqdata['action'] = argument.action
      except: pass

      # # add status
      try:
        reqdata['status'] = argument.status
      except: pass

      # add destination
      try:
        reqdata['destination'] = argument.user
      except: pass

      if method == 'get':
        response = resource.get(environment, reqdata)
      if method == 'post':
        response = resource.post(environment, reqdata)
      return response