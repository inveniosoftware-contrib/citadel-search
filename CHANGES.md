Changes
=======

**Version 1.2-beta (released 2020-05-14)**

Changes:
- [SEARCH-85] Fix reindex cli
    - Instead of `invenio index reindex -t recid` now should use `invenio utils reindex -t recid`
    - Instead of `invenio index run` now should use `invenio utils runindex`
- [NI] fix indico jonschemas

---- 

**Version 1.1.2-beta (released 2020-05-14)**

Changes:
- Update full compose
- [SEARCH-67] Remove binary mappings

---- 

**Version 1.1.1-beta (released 2020-04-28)**

Changes:
- [SEARCH-72] Fix too_many_clauses error

----

**Version 1.1.0-beta (released 2020-04-28)**

Changes:
- [SEARCH-67] Migrate to ES v7

----

**Version 1.0.9-beta (released 2020-04-16)**

Changes:
- [SEARCH-71] egroupsarchives: make group searchable

----

**Version 1.0.8-beta (released 2020-04-14)**

Changes:
- [SEARCH-70] Add field to egroups archives

----


**Version 1.0.7-beta (released 2020-04-07)**

Changes:
- [SEARCH-69] Multifields type search parameter


----

**Version 1.0.6-beta (released 2020-04-06)**

Changes:
- [egroupsarchives] Update archive_v1.0.0.json

----

**Version 1.0.5-beta (released 2020-04-06)**

Changes:
- [SEARCH-66] Add highlight and explain params to search api

----

**Version 1.0.4-beta (released 2020-04-03)**

Changes:
- [SEARCH-60] Egroups Archives mapping fix
- [SEARCH-68] Improve score calculations

----

**Version 1.0.3-beta (released 2020-04-02)**

Changes:
- [SEARCH-60] Add egroups archives schemas

----

**Version 1.0.2-beta (released 2020-03-23)**

Changes:
- [SEARCH-47] Bump tika to 1.24 

----

**Version 1.0.1-beta (released 2020-03-19)**

Changes:
- [SEARCH-42] Bump invenio-records to 1.2.2 - security vulnerability

----

**Version 1.0.0-beta (released 2020-03-17)**

Changes:

- [SEARCH-1] File indexing via Tika + remove support for OCR extraction via ES pipelines
- [#94] Fix rate limit configuration
- [#91] CI: refactor to dev, test and prod usecase
- [#85] EDMS: file v5
- [#88] Files: implement file upload
- [#77] Tests: Run on CI against local changes
- [#83] Mappings: add edms objects
- [#48] Permissions: make schema owner configurable and refactor logic
- [#79] Automate linting
- [#82] Build: bugfixes and improvements
- [#53] Create docker-compose environments
- [#68] Improvements on EDMS documents schema
- [EDMS] config: add sorting options for cernsearchqa-edms
- [EDMS] mappings: new versions
- [TEST] mappings: refactor search-as-you-type analyzer and add did-you-mean
- [WEBSERVICES] mappings: add suggest field for search-as-you-type
- [TEST] mappings: add suggest schema


----

**Version 0.7.0 (released 2019-05-31)**

Features:

- Refactor folders hierarchy
- Created datamodel convention for searchable data (_data)
- Improve Webservices Mappings
- Upgrade to ES6
- Enable OCR extraction in ES
- Migrate to Python3
- Migrate to Pipenv
- Split docker images (Base and App)

----

**Version 0.6.0 (released 2018-01-17)**

Features:

- Refactor access patter to allow cascade.
- Add health check endpoint to web app.
- Add licensing.
- Add schema validation.

Fixes:

- Change ``_access`` mappings field from type nested to object for performance reasons.
- Setup.py versions.

----

**Version 0.5.3 (released 2018-11-13)**

Features:

- Add an endpoint to perform ``Update By Query`` actions over single documents.
- Add ``document_v1.0.0`` schema for EDMS instance.
- Add ``Health`` blueprint with three possible endpoints (uWSGI, Elasticsearch and database).
- Make ``access`` parameter optional in requests.
- Make optional the use of CERN e-groups for permissions.

Fixes:

- Document creation should just check if the user is authenticated in the first iteration. Permissions over the schema are checked on the second iteration. 
