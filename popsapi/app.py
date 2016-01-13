import os, sys
from traceback import format_exc
from flask import Flask
from flask.ext import restful
from werkzeug.contrib.fixers import ProxyFix
from popsapi.models.pops import *
from popsapi.components.common import logger, cfg
from popsapi.resources import ( EnvironmentResource, QueueResource, TaskResource, 
  SlackResource, SlackCommandResource )

try:
  app = Flask(__name__)
  
  app.config['MONGODB_SETTINGS'] = { 
      'db': cfg['mongo']['name'],
      'host': cfg['mongo']['host'],
      'port': cfg['mongo']['port']
      }

  app.config['BUNDLE_ERRORS'] = True

  db.init_app(app)

  api = restful.Api(app)
  # load endpoints
  # Environment
  environment_endpoints = ['/%s/environment/<target_environment>' % os.environ['POPS_VERSION']]
  api.add_resource(EnvironmentResource,
    *environment_endpoints
  )

  # Queue
  queue_endpoints = ['/%s/queue/<target_environment>' % os.environ['POPS_VERSION']]
  api.add_resource(QueueResource,
    *queue_endpoints
  )

  # Tasks
  task_endpoints = ['/%s/task/<target_environment>' % os.environ['POPS_VERSION']]
  api.add_resource(TaskResource,
    *task_endpoints
  )

  # Slack
  slack_endpoints = ['/%s/slack' % os.environ['POPS_VERSION']]
  api.add_resource(SlackResource,
    *slack_endpoints)

  slackcmd_endpoints = ['/%s/slackcmd' % os.environ['POPS_VERSION']]
  api.add_resource(SlackCommandResource,
    *slackcmd_endpoints)
  
except KeyError, e:
  print 'Could not find environment variable', e
  sys.exit(1)
except Exception, e:
  print 'Error doing the initial config: %s\n%s' % (e, format_exc())
  sys.exit(1)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
  try:
    app.run(host='0.0.0.0', port=80, debug=True)
  except Exception, e:
    print 'Error starting web app: %s' % e