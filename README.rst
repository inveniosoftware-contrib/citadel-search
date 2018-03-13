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