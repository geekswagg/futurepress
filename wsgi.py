import os

from application import app, create_app
from test.db_bootstrap import bootstrapTestDB

create_app('core.DevConfig')
application = app

if __name__ == '__main__':
    application.run()