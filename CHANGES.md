Changes
=======

Version 0.5.3 (released 2018-11-13)

Features:

- Add an endpoint to perform ``Update By Query`` actions over single documents.
- Add ``document_v1.0.0`` schema for EDMS instance.
- Add ``Health`` blueprint with three possible endpoints (uWSGI, Elasticsearch and database).
- Make ``access`` parameter optional in requests.
- Make optional the use of CERN e-groups for permissions.

Fixes:

- Document creation should just check if the user is authenticated in the first iteration. Permissions over the schema are checked on the second iteration.