import unittest, sys, requests, json, uuid
from datetime import datetime


ENVIRONMENT_NAME = 'corporation'
SERVER1 = 'mta-in.mailserver.com'
SERVER2 = 'mta-out.mailserver.com'
SERVER3 = 'mail-gateway.mailserver.com'
DOMAIN_NAME = 'corporation.com'
BASE_URL = 'http://localhost/v1'
HEADERS = {
  'Content-Type' : 'application/json'
}

class EnvironmentTestCase(unittest.TestCase):
    def test_environment_crud_operations(self):
      env_url = BASE_URL + '/environment/%s' % ENVIRONMENT_NAME
      request_data = {
        'name' : ENVIRONMENT_NAME,
        'company' : 'Corporation',
        'email' : 'fernando.cainelli@acme.com',
        'servers' : [{
          'name' : SERVER1,
          'tags' : 'inbound',
          'ip' : '192.168.0.100'
        },
        {
          'name' : SERVER2,
          'tags' : 'outbound',
          'ip' : '192.168.0.99'
        },
        {
          'name' : SERVER3,
          'tags' : 'both',
          'ip' : '192.168.2.133'
        }]
      }

      request_data = json.dumps(request_data)

      print 'DELETE:', env_url
      response = requests.delete(env_url)
      print response.status_code
      print response.text

      print 'POST:', env_url
      response = requests.post(env_url, headers=HEADERS, data=request_data)
      print response.status_code
      print response.text

      print 'GET:', env_url
      response = requests.get(env_url, headers=HEADERS)
      print response
      print response.text

      self.assertTrue(response.status_code == 200)

class QueueTestCase(unittest.TestCase):
    def test_queue_crud_operations(self):
      env_url = BASE_URL + '/queue/%s' % ENVIRONMENT_NAME


      request_data1 = {
        'server' : SERVER1,
        'topsenders' : [{
            'email': 'fernando.cainelli@acme.com',
            'quantity' : 2120
          },
          {
            'email': 'fernando@cainelli.me',
            'quantity' : 255
          },
          {
            'email': 'fernando@cainelli.ninja',
            'quantity' : 434
        }],
        'queue' : {
            'active' : 20,
            'bounce' : 500,
            'hold' : 1,
            'deferred' : 300
        }
      }


      request_data2 = {
        'server' : SERVER2,
        'topsenders' : [{
            'email': 'diverse@domain.com',
            'quantity' : 113
          },
          {
            'email': 'anothermail@cainelli.me',
            'quantity' : 344
          },
          {
            'email': 'hellyeah@cainelli.ninja',
            'quantity' : 5400
        }],
        'queue' : {
            'active' : 1,
            'bounce' : 14,
            'hold' : 0,
            'deferred' : 1344
        }
      }


      request_data3 = {
        'server' : SERVER3,
        'topsenders' : [{
            'email': 'whatever@apple.com',
            'quantity' : 1223
          },
          {
            'email': 'cuca@ninja.ninja',
            'quantity' : 3344
          },
          {
            'email': 'c3@mydomain.com.br',
            'quantity' : 133
        }],
        'queue' : {
            'active' : 33,
            'bounce' : 23,
            'hold' : 22,
            'deferred' : 134
        }
      }



      print 'POST1:', env_url
      response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_data1))
      print response.status_code
      print response.text

      print 'POST2:', env_url
      response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_data2))
      print response.status_code
      print response.text

      print 'POST3:', env_url
      response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_data3))
      print response.status_code
      print response.text


      args = '?server=%s' % (SERVER2)
      print 'DELETE2:', env_url + args
      response = requests.delete(env_url + args)
      print response.status_code
      print response.text


      args = '?server=%s&tag=inbound&server=%s' % (SERVER1, SERVER2)
      args = ''
      print 'GET:' , env_url + args
      response = requests.get(env_url + args , headers=HEADERS)

      print response
      print response.text

      self.assertTrue(response.status_code == 200)

class TaskTestCase(unittest.TestCase):
    def test_task_crud_operations(self):
      env_url = BASE_URL + '/task/%s' % ENVIRONMENT_NAME

      request_create_data1 = {
        'server' : SERVER1,
        'action' : 'getmessage',
        'destination' : 'fernando.cainelli@cainelli.ninja',
        'status' : 'pending',
        'response' : ''
      }

      request_create_data2 = {
        'server' : SERVER2,
        'action' : 'hold',
        'destination' : 'user@domain.com',
        'status' : 'pending',
        'response' : ''
      }

      print 'POST:', env_url
      response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_create_data1))
      print response.status_code
      print response.text

      print 'POST:', env_url
      response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_create_data2))
      print response.status_code
      print response.text


      args = '?server=%s&status=%s&action=%s' % (SERVER2, 'pending', 'hold')
      print 'GET Filtered:' , env_url + args
      response = requests.get(env_url + args, headers=HEADERS)
      data = json.loads(response.text)
      print response.status_code
      print json.dumps(data[0], indent=2)

      request_update_data2 = {
        'taskid' : data[0]['taskid'],
        'server' : SERVER2,
        'status' : 'closed',
        'response' : 'holded successfully.'
      }

      print 'PUT UPDATE:', env_url
      response = requests.put(env_url, headers=HEADERS, data=json.dumps(request_update_data2))
      print response.status_code
      print response.text


      print 'GET:' , env_url
      response = requests.get(env_url , headers=HEADERS)

      print response
      print response.text

      self.assertTrue(response.status_code == 200)

class SlackTestCase(unittest.TestCase):
  def test_slack_crud_operations(self):
    env_url = BASE_URL + '/slack'

    token1 = '6YskRUkNoRhh28RNTuTRem13'
    token2 = 'Tj8i88nVaqbjxkG2ZgpGYbAj'
    token3 = 'h5feAKJ3ssDryskwZwOi9jsn'
    team_domain = 'slackdom'
    team_id = 'T0J7BPQJC'
    channel_id = 'C9J07K50'


    request_data = {
      'token' : token1,
      'team_domain' : team_domain,
      'team_id' : team_id,
      'channel_id' : channel_id, # ops
      'command' : '/getqueue',
      'environment' : ['corporation']
    }
    
    request_data2 = {
      'token' : token2,
      'team_domain' : team_domain,
      'team_id' : team_id,
      'channel_id' : channel_id, # ops
      'command' : '/gettasks',
      'environment' : ['corporation']
    }

    request_data3 = {
      'token' : token3,
      'team_domain' : team_domain,
      'team_id' : team_id,
      'channel_id' : channel_id, # ops
      'command' : '/createtask',
      'environment' : ['corporation']
    }
    


    print 'DELETE:', env_url
    response = requests.delete(env_url, headers=HEADERS, data=json.dumps(request_data))
    print response.status_code
    print response.text

    print 'DELETE:', env_url
    response = requests.delete(env_url, headers=HEADERS, data=json.dumps(request_data2))
    print response.status_code
    print response.text

    print 'DELETE:', env_url
    response = requests.delete(env_url, headers=HEADERS, data=json.dumps(request_data3))
    print response.status_code
    print response.text


    print 'POST:', env_url
    response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_data))
    print response.status_code
    print response.text


    print 'POST:', env_url
    response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_data2))
    print response.status_code
    print response.text

    print 'POST:', env_url
    response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_data3))
    print response.status_code
    print response.text

    args = '?team_domain=%s' % ('slackdom')
    print 'GET:' , env_url + args
    response = requests.get(env_url + args, headers=HEADERS)
    print response.status_code
    print response.text

    self.assertTrue(response.status_code == 200)

  def test_slackcmd_crud_operations(self):
    env_url = BASE_URL + '/slackcmd'


    token1 = '6YskRUkNoRhh28RNTuTRem13'
    token3 = 'h5feAKJ3ssDryskwZwOi9jsn'

    team_domain = 'slackdom'
    team_id = 'T0J7BPQJC'
    channel_id = 'C9J07K50'
    channel_name = 'ops'
    user_id = 'U07QK8J8K'
    user_name = 'cainelli'

    request_data = {
      'token' : token3,
      'team_domain' : team_domain,
      'team_id' : team_id,
      'channel_id' : channel_id, # ops
      'channel_name' : channel_name,
      'user_id' : user_id,
      'user_name' : user_name,
      'command' : '/createtask',
      'text' : '-environment corporation -user fernando.cainelli@acme.com -action getmessage'
    }

    command = '/getqueue'
    text = '-environment corporation -server mta-in.mailserver.com'
    args = "?token=%s&\
team_domain=%s&\
team_id=%s&\
channel_id=%s&\
channel_name=%s&\
user_id=%s&\
user_name=%s&\
command=%s&\
text=%s" % (token1, team_domain, team_id, channel_id, channel_name, user_id, user_name, command, text)



    print 'POST:', env_url
    response = requests.post(env_url, headers=HEADERS, data=json.dumps(request_data))
    print response.status_code
    print response.text

    print 'GET:' , env_url + args
    response = requests.get(env_url + args, headers=HEADERS, timeout=5)
    print response.status_code
    print response.text


    self.assertTrue(response.status_code == 200)

if __name__ == '__main__':
  suite = unittest.TestSuite()
  suite.addTest(EnvironmentTestCase('test_environment_crud_operations'))
  suite.addTest(QueueTestCase('test_queue_crud_operations'))
  suite.addTest(TaskTestCase('test_task_crud_operations'))
  suite.addTest(SlackTestCase('test_slack_crud_operations'))
  suite.addTest(SlackTestCase('test_slackcmd_crud_operations'))
  unittest.TextTestRunner().run(suite)
