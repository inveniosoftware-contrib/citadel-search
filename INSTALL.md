Installing CERNSearch requires the following services to be running:

- Elasticsearch version>=5.4.0
- PostregSQL/Mariadb/SQLite support
- Redis-server
- RabbitMQ/Another ActiveMQ implementation

Configuration is set to default values (e.g. ip:port pairs) if not, change in Config.py.

In order to start the system run the following commands (just the first time):

- invenio db init
- invenio db create
- invenio index init
- invenio index queue init (Not needed, Bulk indexing support is not yet there)

Then simply start the application with:

- invenio run \[--host 0.0.0.0\]

Note: if you do not have a valid certificate to run over SSL, make sure to have the environment variabel "FLASK_DEBUG"
set to 1.
