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
  "id": "http://localhost:5000/schemas/doc-v0.0.1.json",
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
documents to be returned (in total and per page), among other options. For a full list check refer to 
{TODO INSERT LINK}

An example query for the terms _awesome_ and _document_ looks like this:

```bash
curl -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' \
  'http://<host:port>/records/?q=awesome+document'
```

## Setup

An instance can be deployed using the OpenShift template (can be found in _template/cern-search-api.yml_)

Take into account:

The URI of the SQL database is set through a secret since it has to carry the user and password to access it. Therefore,
a secret must be created in OpenShift (e.g. running oc create -f <secret_file>). The following can be used as template:

```
apiVersion: v1
kind: Secret
metadata:
  name: srchdb-dev
stringData:
  dburi: postgresql+psycopg2://user:password@host:port/databasename
```