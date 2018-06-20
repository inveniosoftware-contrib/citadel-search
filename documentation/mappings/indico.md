# Indico Instance

No denormalization has been used due to the nature of the user use cases. There is a high number of updates, which would result in an even higher number of updates to handle the denormalized information. Application-side joins are used instead. 

For the analysis, tokenizing and steeming the ``standard`` analyzed is used by default, with multifields for ``english`` and ``french`` analyzers.

The _category path_ field is not analyzed as a ``path`` and ``reverse path`` due to the unique nature of the path, being it treated as an array (better performance).

Rollover will be based on event ID. Conditions: Num documents is uniformly distributed over time and in size. IDs are seq and inc. Old (>1.5y aprox) are not usually updated (use a signal to check this). Use a signal to run rollover (curator does nto accept custom condition).

## Mappings

### Events

--- v1.0.0 ---

The first version of the _Events_ mapping stores the information about an Indico event.

* __\_access__: owner, read, update, delete rights base on an egroup list. Stored as a nested object, being each of the permissions of keyword type (exact match).
* __id__: ID of the event. Stored as keyword for exact match queries.
* __caterogy path__: Array containing the different path levels to which the event belongs to. Stored as keyword for exact match queries.
* __event_type__: Type of the event. Stored as keyword for exact match queries.
* __creation_date__: Creation date of the event. Stored as date with 'YYYY-MM-DDZHH:MM' format.
* __start_date__: Starting date of the event. Stored as date with 'YYYY-MM-DDZHH:MM' format.
* __end_date__: Ending date of the event. Stored as date with 'YYYY-MM-DDZHH:MM' format.
* __location__: Location/Place of the event. Stored as text for full-text search, only using ``standard`` analyzer.
* __title__: Title of the event. Stored as text for full-text search. The ``title`` field is analyzed with the ``standard`` analyzer, ``title.english`` with the ``english`` one and the corresponding is done for ``title.french``. This three times analyzis helps improve query relevance.
* __description__: Description of the event. Stored as text for full-text search. The ``title`` field is analyzed with the ``standard`` analyzer, ``title.english`` with the ``english`` one and the corresponding is done for ``title.french``. This three times analyzis helps improve query relevance.
* __speakers_chairs__: Speakers/charimans of the event. Stored as a nested object (This field cannot be flatten since the searches are done for a specific person of a specific organization.) with two fields:
	- __name__: Name of the speaker/chairman. Stored both as keyword and text, for exact match and full-text search.
	- __affiliation__: Affiliation of the speaker/chairman. Stored as text for full-text search.
  
- jsonschema path: '/cernsearch/jsonschemas/indico/event_v1.0.0.json'
- mapping path: '/cernsearch/mappings/v5/indico/event_v1.0.0.json'

Q: Title with 'keyword' field. Is exact match needed?
Q: speakers_chairs, both field should they be keyword, text or both? Analyzers will not do much good with 'custom' names.


