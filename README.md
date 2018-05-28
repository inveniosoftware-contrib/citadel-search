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
           "_access": {
             "delete": "test-egroup@cern.ch", 
             "owner": "test-egroup@cern.ch", 
             "read": "test-egroup@cern.ch", 
             "update": "test-egroup@cern.ch"
           }, 
        "description": "This is an awesome description for our first uploaded document",
        "title": "Demo document"
        "$schema": "http://0.0.0.0/schemas/test-doc_v0.0.1.json"
       }
       '
```
Note: The ``$schema`` field is not mandatory, if it is not set the documents will be inserted in the default schema 
(defined upon instance creation).

The response should be a code 200 with a selflink to the new inserted document. 
It should look something similar to the url of the next query. With it we can obtain the document:

```bash
curl -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' \
  'http://<host:port>/api/record/1'

```

### Query documents

In order to query documents we need to perform a *GET* operation. We can specify the amount of 
documents to be returned (in total and per page), among other options. For a full list check
[here](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html). Note that all the indices of an 
instance have the same alias, and one per folder of the mappings tree. Therefore, the ``invenio-records-rest`` library can be set with only one search index 
(that allow searching over multiple indices, but only the allowed ones).

```
/cernsearch-test/ 
      |
      '---> /type_one/
      |         |
      |         '---> mapping_one_a.json
      |         '---> mapping_one_b.json
      '---> /type_two/
      |         |
      |         '---> mapping_two.json
      |
      '---> mapping_test.json
```

Indices ``mapping_one_a`` and ``mapping_one_b`` will have ``cernsearch-test`` and ``type_one`` aliases, ``mapping_two`` 
will have ``cernsearch-test`` and ``type_two`` aliases, and finally ``mapping_test`` will have ``cernsearch-test`` as
alias.

Concerning the queries, an example query for the terms _awesome_ and _document_ looks like this:

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

Documents can also be updated partially. To perform this action we need to do a *PATCH*. The endpoint accepts 
application/json+patch as Content-Type. An example to update the description would be:

```bash
curl -k -X PATCH -H 'Content-Type: application/json-patch+json' -H 'Accept: application/json' \
    -i 'https://test-cern-search.web.cern.ch/api/record/9' --data '
    [
        {"op": "replace", "path": "/metadata/description", "value": "Description changed with patch partial update"}
    ]'
```

More about the options of json+patch can be found [here](http://jsonpatch.com/).

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
            "owner":{
              "type": "string"
            },
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

Note that there is no _create_ permission, that is specified by the __owner_ field in the metadata. The owner field in 
the document schema is still needed for querying purposes and should be the owner of the document (in most cases it 
will be the same than the owner of the document collection or index but it is specified at document indexing time 
rather than upon index creation).

### Importante note

There is a bug in invenio-oauthclient. Once the user SSO token expires there is no way of updating the egroups 
(and other information) of the user, failing with a _401 Unauthorized_ from the SSO (due to expired token). There is an 
issue opened ([link](https://github.com/inveniosoftware/invenio-oauthclient/issues/154)). In the meanwhile the solution is to edit the _invenio-oauthclient/contrib/cern.py:account_groups_ 
with the following lines:

```python
    def account_groups(account, resource, refresh_timedelta=None):
        """Fetch account groups from resource if necessary."""
        updated = datetime.utcnow()
        modified_since = updated
        if refresh_timedelta is not None:
            modified_since += refresh_timedelta
        modified_since = modified_since.isoformat()
        last_update = account.extra_data.get('updated', modified_since)
    
        #if last_update > modified_since:
        groups_db = account.extra_data.get('groups', [])
        if groups_db is not None and groups_db:
            return account.extra_data.get('groups', [])
    
        groups = fetch_groups(resource['Group'])
        account.extra_data.update(
            groups=groups,
            updated=updated.isoformat(),
        )
        return groups
``` 

This means the groups will be taken upon the first login of the user and never updated. A fix will come soon.

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

## Configuration

CERN Search specific parameters:

-
-
-

The rest of the configuration comes from the parameters are configurable thought the Invenio Framework. The full list of
the overwriten ones is show below, nonetheless, if needed others can be overwriten (check documentation of the 
corresponding project in the [invenio repository](www.github.com/inveniosoftware)):

-
-
-