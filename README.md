# CERN Search as a Service

CERN Search provides enterprise search capabilities on demand. You can set up your own search instance, submit your 
documents and search among them when needed!

## RESTful API

CERN Search as a Service provides a RESTful API through which you interact with your instance.

Lets assume the following JSON schema and Elasticsearch mapping for our demo documents:

- JSON schema:
```json
{
  "title": "Custom record schema v0.0.1",
  "id": "http://localhost:5000/schemas/cernsearch-test-doc_v0.0.1.json",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Record title."
    },
    "description": {
      "type": "string",
      "description": "Description for record."
    },
    "custom_pid": {
      "type": "string"
    },
    "$schema": {
      "type": "string"
    }
  }
}
```

- Elasticsearch mapping: 
```json
{
  "settings": {
    "index.percolator.map_unmapped_fields_as_string": true,
    "index.mapping.total_fields.limit": 3000
  },
  "mappings": {
    "doc-v0.0.1": {
      "numeric_detection": true,
      "_all": {
        "analyzer": "english"
      },
      "properties": {
        "title": {
          "type": "string",
          "analyzer": "english"
        },
        "description": {
          "type": "string",
          "analyzer": "english"
        },
        "custom_pid": {
          "type": "string",
          "index": "not_analyzed"
        },
        "$schema": {
          "type": "string",
          "index": "not_analyzed"
        }
      }
    }
  }
}
```

### Insert documents

In order to upload a document we need to perform a *POST* operation. For example using curl:

```bash
curl -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' \
    -i 'http://<host:port>/api/records/' --data '
       {
        "description": "This is an awesome description for our first uploaded document",
        "title": "Demo document"
       }
       '
```

The response should be a code 200 with a selflink to the new inserted document. 
It should look something similar to the url of the next query. With it we can obtain the document:

```bash
curl -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' \
  'http://<host:port>/api/record/1'

```

### Query documents

In order to query documents we need to perform a *GET* operation. We can specify the amount of 
documents to be returned (in total and per page), among other options. For a full list check
[here](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html).

An example query for the terms _awesome_ and _document_ looks like this:

```bash
curl -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' \
  'http://<host:port>/records/?q=awesome+document'
```

We can use pagination to restrict the amount of results. for example we are going to obtain the second page of a query
that get one element per page:
```bash
curl -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' \
  'http://<host:port>/api/records/?page=2&size=1'
```

The answer would look something similar to:
```json
{
  "aggregations": {}, 
  "hits": {
    "hits": [
      {
        "created": "2018-03-19T08:16:53.218017+00:00", 
        "id": 5, 
        "links": {
          "self": "http://<host:port>/api/record/5"
        }, 
        "metadata": {
          "control_number": "5", 
          "description": "This is an awesome description for our first uploaded document", 
          "title": "Demo document"
        }, 
        "updated": "2018-03-19T08:16:53.218042+00:00"
      }
    ], 
    "total": 2
  }, 
  "links": {
    "prev": "http://<host:port>/api/records/?page=1&size=1", 
    "self": "http://<host:port>/api/records/?page=2&size=1"
  }
}
```

Note the *links* field, which is very useful to process the results. Allowing us to get the current, next and previous
pages (only the _next_ for the first page, and only the _previous_ for the last page).

### Update documents

To update a document we need to perform a *PUT* operation over the _record_ endpoint. Therefore, the _ID_ or ETag of the
record is part of the URL. Nonetheless, due to workflow issues the data of the request *must* also contain this _ID_ in
the _control_number_ field.

```bash
curl -X PUT -H 'Content-Type: application/json' -H 'Accept: application/json' \
    -i 'http://<host:port>/api/record/5' --data '
        {   
            "control_number": "5",
            "description": "This is an awesome updated description",
            "title": "Update Test 1"
        }
        '
```

### Delete documents

To delete a document we need to perform a *DELETE* operation. For this we simply need to specify the document _ID_ by
querying the _record_ endpoint:

```bash
curl -XDELETE -H 'Content-Type: application/json' -H 'Accept: application/json' \
  'http://<host:port>/api/record/5'
```

If afterwards we query (get,put,delete) for the specific item we will obtain a 410:

```json
{
  "status": 410, 
  "message": "PID has been deleted."
}
```

## ACLs and permissions

Permissions are implemented in a CRUD fashion.

Read, Update and Delete follow the same pattern. The user has to be authenticated and to be allowed
to perform the action on the document, meaning one of its egroups is in the corresponding __access_ field.
Create also needs the user to be authenticated, but in this case the ownership/permissions are not check on
a document but on the mapping. The egroups allowed to create are specified in the mapping when setting up the 
Search instance.

Search is not treated as a normal read. It passes through the _cern_filter_. This filter applies the following rules:

``public | read_restricted ``

Which will get the documents that are public and those that are restricted but the user egroups match the _read_ field
of the __access_ property.

An example mapping containing the permission fields is:

```json
{
  "settings": {
    "index.percolator.map_unmapped_fields_as_string": true,
    "index.mapping.total_fields.limit": 3000
  },
  "mappings": {
    "cern-search-example-v0.0.1": {
      "_meta": { 
        "class": "cern-search-example",
        "_owner": "egroup_owner_one, egroup_owner_two,egroup_owner_three"
      },
      "properties": {
        "_access": {
          "type": "nested",
          "properties": {
            "read":{
              "type": "string"
            },
            "update":{
              "type": "string"
            }, 
            "delete":{
              "type": "string"
            }
          }  
        },
        "title": {
          "type": "string"
        },
        ...
      }
    }
  }
}
```

Note that there is no _create_ permission, that is specified by the __owner_ field in the metadata.

## Setup

An instance can be deployed using the OpenShift template (can be found in _template/cern-search-api.yml_)

Take into account:

The URI of the SQL database is set through a secret since it has to carry the user and password to access it. Therefore,
a secret must be created in OpenShift (e.g. running oc create -f <secret_file>). The following can be used as template:

Database (PostgreSQL) Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: srchdb-dev
stringData:
  dburi: postgresql+psycopg2://user:password@host:port/databasename
```

ES Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: es
stringData:
  # Localhost
  es_credentials: "[{'host': 'endpoint', 'url_prefix': '/es', 'port': 443, 'use_ssl': True, 'verify_certs': True, 'ca_certs':'/etc/pki/tls/certs/ca-bundle.trust.crt', 'http_auth': ('user','password')}]"
```

OAuth Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: oauth
stringData:
  # Localhost
  oauth_credentials: "{'consumer_key':'consumer_id','consumer_secret':'consumer_secret'}"
```

Starting command throw ssl:
```bash
gunicorn -b :5000 --certfile=ssl.crt --keyfile=ssl.key cern_search_rest.wsgi
```