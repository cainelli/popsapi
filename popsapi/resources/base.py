from flask.ext.restful import reqparse, request, Resource, abort


def abort_if_obj_doesnt_exist(filter_by, target, document_object, blame_for_all=True):
  if target == 'all' and not blame_for_all:
    objects = document_object.objects.get()
    if not objects:
      abort(404, message='Objects Not Found')
    return objects
  elif target == 'all' and blame_for_all:
    abort(400, message="Keyword 'all' not accepted in this context!")

  query = { filter_by : target }
  result = document_object.objects.get(__raw__=query)
  
  if not result:
    abort(404, message='Could not find object: %s' % target)
  return result


class BaseResource(Resource):
  def __init__(self, filters, default_filter='name', **kwargs):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('filter_by', type=str, location='args')
    self.filter_by = parser.parse_args().get('filter_by') or default_filter
    if self.filter_by not in filters:
      err_message = 'Wrong query filter specified %s. Accept only: %s' % (self.filter_by, ', '.join(filters))
      abort(400, message=err_message)
    self.parser = reqparse.RequestParser()