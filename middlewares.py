import models


class DatabaseSessionManager(object):

    def __init__(self):
        self.db_session = models.Session

    def process_resource(self, req, resp, resource, params):
        req.context['db_session'] = self.db_session()

    def process_response(self, req, resp, resource, req_succeeded):
        if req.context.get('db_session'):
            if not req_succeeded:
                req.context['db_session'].rollback()
            req.context['db_session'].close()
