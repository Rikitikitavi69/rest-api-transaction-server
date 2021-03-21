from wsgiref import simple_server

import falcon
import falcon_auth

import middlewares
import resources


user_loader = lambda username, password: {'username': username, 'password': password}
auth_backend = falcon_auth.BasicAuthBackend(user_loader)
auth_middleware= falcon_auth.FalconAuthMiddleware(auth_backend)


app = falcon.API(middleware=[
    auth_middleware,
    middlewares.DatabaseSessionManager(),
])

app.add_route('/client', resources.Client())
app.add_route('/transaction', resources.Transaction())


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
