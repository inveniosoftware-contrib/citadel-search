Installing CERNSearch requires the following services to be running:

- Elasticsearch version>=5.4.0
- Mariadb/SQLite support
- Redis-server
- RabbitMQ/Another ActiveMQ implementation

Configuration is set to default values (e.g. ip:port pairs) if not, change in Config.py.

In order to start the system run the following commands (just the first time):

- invenio db init
- invenio db create
- invenio index init
- invenio index queue init

Then simply start the application with:

- invenio run

Note: if you do not have a valid certificate to run over SSL, make sure to have the environment variabel "FLASK_DEBUG"
set to 1.
