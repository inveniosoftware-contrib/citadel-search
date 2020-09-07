# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

r"""Pre-configured remote application for enabling sign in/up with CERN.

CERN (remote app).
^^^^^^^^^^^^^^^^^^

1. Edit your configuration and add:

   .. code-block:: python

       import copy

       from invenio_oauthclient.contrib import cern

       CERN_REMOTE_APP = copy.deepcopy(cern.REMOTE_APP)
       CERN_REMOTE_APP["params"].update(dict(request_token_params={
           "resource": "changeme.cern.ch",  # replace with your server
           "scope": "Name Email Bio Groups",
       }))

       OAUTHCLIENT_REMOTE_APPS = dict(
           cern=CERN_REMOTE_APP,
       )

       CERN_APP_CREDENTIALS = dict(
           consumer_key="changeme",
           consumer_secret="changeme",
       )

  Note, if you want to use the CERN sandbox, use ``cern.REMOTE_SANDBOX_APP``
  instead of ``cern.REMOTE_APP``.

2. Register a new application with CERN. When registering the
   application ensure that the *Redirect URI* points to:
   ``http://localhost:5000/oauth/authorized/cern/`` (note, CERN does not
   allow localhost to be used, thus testing on development machines is
   somewhat complicated by this).


3. Grab the *Client ID* and *Client Secret* after registering the application
   and add them to your instance configuration (``invenio.cfg``):

   .. code-block:: python

       CERN_APP_CREDENTIALS = dict(
           consumer_key="<CLIENT ID>",
           consumer_secret="<CLIENT SECRET>",
       )

4. Now login using CERN OAuth:
   http://localhost:5000/oauth/login/cern/.

5. Also, you should see CERN listed under Linked accounts:
   http://localhost:5000/account/settings/linkedaccounts/

By default the CERN module will try first look if a link already exists
between a CERN account and a user. If no link is found, the user is asked
to provide an email address to sign-up.

In templates you can add a sign in/up link:

.. code-block:: jinja

    <a href="{{ url_for("invenio_oauthclient.login", remote_app="cern") }}">
      Sign in with CERN
    </a>

For more details you can play with a :doc:`working example <examplesapp>`.


CERN (remote REST app)
^^^^^^^^^^^^^^^^^^^^^^

This configuration is appropriate for e.g. a SPA application which communicates
with Invenio via REST calls.

1. Edit your configuration and add:

   .. code-block:: python

        import copy
        from invenio_oauthclient.contrib import cern

        OAUTH_REMOTE_APP = copy.deepcopy(cern.REMOTE_REST_APP)

        # Path where you want your SPA to be redirected after a
        # successful login.
        OAUTH_REMOTE_APP["authorized_redirect_url"] = \
            'https://<my_SPA_site>/login'
        # Path where you want your SPA to be redirected after a
        # login error.
        OAUTH_REMOTE_APP["error_redirect_url"] = 'https://<my_SPA_site>/error'
        OAUTHCLIENT_REST_REMOTE_APPS = dict(
            cern=OAUTH_REMOTE_APP,
        )

2. Register a new application with CERN. When registering the
   application ensure that the *Redirect URI* points to:
   ``https://<my_invenio_site>:5000/oauth/authorized/cern/`` (note, CERN does
   not allow localhost to be used, thus testing on development machines is
   somewhat complicated by this).


3. Grab the *Client ID* and *Client Secret* after registering the application
   and add them to your instance configuration (``config.py``):

   .. code-block:: python

        CERN_APP_CREDENTIALS = dict(
            consumer_key='<client_id>',
            consumer_secret='<secret>',
        )

4. Now access the login page from your SPA using CERN OAuth:

.. code-block:: javascript

    window.location =
    "https://<my_invenio_site>:5000/api/oauth/login/cern?next=<my_next_page>";


By default the CERN module will try first look if a link already exists
between a CERN account and a user. If no link is found, the user is asked
to provide an email address to sign-up.

For more details you can play with a :doc:`working example <examplesapp>`.
"""

import copy
import re
from datetime import datetime, timedelta

from flask import Blueprint, current_app, flash, g, redirect, session, url_for
from flask_babelex import gettext as _
from flask_login import current_user
from flask_principal import AnonymousIdentity, RoleNeed, UserNeed, identity_changed, identity_loaded
from invenio_db import db
from invenio_oauthclient.errors import OAuthCERNRejectedAccountError
from invenio_oauthclient.handlers.rest import response_handler
from invenio_oauthclient.models import RemoteAccount
from invenio_oauthclient.proxies import current_oauthclient
from invenio_oauthclient.utils import oauth_link_external_id, oauth_unlink_external_id

OAUTHCLIENT_CERN_HIDDEN_GROUPS = (
    'All Exchange People',
    'CERN Users',
    'cern-computing-postmasters',
    'cern-nice2000-postmasters',
    'CMF FrontEnd Users',
    'CMF_NSC_259_NSU',
    'Domain Users',
    'GP Apply Favorites Redirection',
    'GP Apply NoAdmin',
    'info-terminalservices',
    'info-terminalservices-members',
    'IT Web IT',
    'NICE Deny Enforce Password-protected Screensaver',
    'NICE Enforce Password-protected Screensaver',
    'NICE LightWeight Authentication WS Users',
    'NICE MyDocuments Redirection (New)',
    'NICE Profile Redirection',
    'NICE Terminal Services Users',
    'NICE Users',
    'NICE VPN Users',
)
"""Tunable list of groups to be hidden."""

OAUTHCLIENT_CERN_HIDDEN_GROUPS_RE = (
    re.compile(r'Users by Letter [A-Z]'),
    re.compile(r'building-[\d]+'),
    re.compile(r'Users by Home CERNHOME[A-Z]'),
)
"""Tunable list of regexps of groups to be hidden."""

OAUTHCLIENT_CERN_REFRESH_TIMEDELTA = timedelta(minutes=-5)
"""Default interval for refreshing CERN extra data (e.g. groups)."""

OAUTHCLIENT_CERN_SESSION_KEY = 'identity.cern_provides'
"""Name of session key where CERN roles are stored."""

OAUTHCLIENT_CERN_ALLOWED_IDENTITY_CLASSES = [
    'CERN Registered',
    'CERN Shared'
]
"""Cern oauth identityClass values that are allowed to be used."""

BASE_APP = dict(
    title='CERN',
    description='Connecting to CERN Organization.',
    icon='',
    logout_url='https://login.cern.ch/adfs/ls/?wa=wsignout1.0',
    params=dict(
        base_url='https://oauth.web.cern.ch/',
        request_token_url=None,
        access_token_url='https://oauth.web.cern.ch/OAuth/Token',
        access_token_method='POST',
        authorize_url='https://oauth.web.cern.ch/OAuth/Authorize',
        app_key='CERN_APP_CREDENTIALS',
        content_type='application/json',
        request_token_params={'scope': 'Name Email Bio Groups',
                              'show_login': 'true'}
    )
)

REMOTE_APP = dict(BASE_APP)
REMOTE_APP.update(dict(
    authorized_handler='invenio_oauthclient.handlers'
                       ':authorized_signup_handler',
    disconnect_handler='invenio_oauthclient.contrib.cern'
                       ':disconnect_handler',
    signup_handler=dict(
        info='invenio_oauthclient.contrib.cern:account_info',
        setup='invenio_oauthclient.contrib.cern:account_setup',
        view='invenio_oauthclient.handlers:signup_handler',
    )
))
"""CERN Remote Application."""

REMOTE_REST_APP = dict(BASE_APP)
REMOTE_REST_APP.update(dict(
    authorized_handler='invenio_oauthclient.handlers.rest'
                       ':authorized_signup_handler',
    disconnect_handler='invenio_oauthclient.contrib.cern'
                       ':disconnect_rest_handler',
    signup_handler=dict(
        info='invenio_oauthclient.contrib.cern:account_info_rest',
        setup='invenio_oauthclient.contrib.cern:account_setup',
        view='invenio_oauthclient.handlers.rest:signup_handler',
    ),
    response_handler=(
        'invenio_oauthclient.handlers.rest:default_remote_response_handler'
    ),
    authorized_redirect_url='/',
    disconnect_redirect_url='/',
    signup_redirect_url='/',
    error_redirect_url='/'
))
"""CERN Remote REST Application."""


REMOTE_SANDBOX_APP = copy.deepcopy(REMOTE_APP)
"""CERN Sandbox Remote Application."""

REMOTE_SANDBOX_APP['params'].update(dict(
    base_url='https://test-oauth.web.cern.ch/',
    access_token_url='https://test-oauth.web.cern.ch/OAuth/Token',
    authorize_url='https://test-oauth.web.cern.ch/OAuth/Authorize',
))

REMOTE_APP_RESOURCE_API_URL = 'https://oauthresource.web.cern.ch/api/Me'
REMOTE_APP_RESOURCE_SCHEMA = 'http://schemas.xmlsoap.org/claims/'

cern_oauth_blueprint = Blueprint('cern_oauth', __name__)


@cern_oauth_blueprint.route('/cern/logout')
def logout():
    """CERN logout view."""
    logout_url = REMOTE_APP['logout_url']

    apps = current_app.config.get('OAUTHCLIENT_REMOTE_APPS')
    if apps:
        cern_app = apps.get('cern', REMOTE_APP)
        logout_url = cern_app['logout_url']

    return redirect(logout_url, code=302)


def find_remote_by_client_id(client_id):
    """Return a remote application based with given client ID."""
    current_app.logger.debug(f"find_remote_by_client_id: client_id={client_id}")

    for remote in current_oauthclient.oauth.remote_apps.values():
        current_app.logger.debug(f"Remote: consumer_key={remote.consumer_key}  name={remote.name}")

        if remote.name == 'cern' and remote.consumer_key == client_id:
            return remote


def fetch_groups(groups):
    """Prepare list of allowed group names.

    :param groups: The complete list of groups.
    :returns: A filtered list of groups.
    """
    hidden_groups = current_app.config.get(
        'OAUTHCLIENT_CERN_HIDDEN_GROUPS', OAUTHCLIENT_CERN_HIDDEN_GROUPS)
    hidden_groups_re = current_app.config.get(
        'OAUTHCLIENT_CERN_HIDDEN_GROUPS_RE',
        OAUTHCLIENT_CERN_HIDDEN_GROUPS_RE)
    groups = [group for group in groups if group not in hidden_groups]
    filter_groups = []
    for regexp in hidden_groups_re:
        for group in groups:
            if regexp.match(group):
                filter_groups.append(group)
    groups = [group for group in groups if group not in filter_groups]

    return groups


def fetch_extra_data(resource):
    """Return a dict with extra data retrieved from cern oauth."""
    person_id = resource.get('PersonID', [None])[0]
    identity_class = resource.get('IdentityClass', [None])[0]
    department = resource.get('Department', [None])[0]

    return dict(
        person_id=person_id,
        identity_class=identity_class,
        department=department
    )


def should_refresh_groups(extra_data_updated=None, refresh_timedelta=None):
    """Check if updating the groups is needed."""
    updated = datetime.utcnow()
    modified_since = updated
    if refresh_timedelta is not None:
        modified_since += refresh_timedelta
    modified_since = modified_since.isoformat()
    if updated is None:
        updated = modified_since
    last_update = extra_data_updated

    if last_update > modified_since:
        return False

    return True


def account_groups_and_extra_data(account, resource,
                                  refresh_timedelta=None):
    """Fetch account groups and extra data from resource if necessary."""
    updated = datetime.utcnow()
    modified_since = updated
    if refresh_timedelta is not None:
        modified_since += refresh_timedelta
    modified_since = modified_since.isoformat()
    last_update = account.extra_data.get('updated', modified_since)

    if last_update > modified_since:
        return account.extra_data.get('groups', [])

    groups = fetch_groups(resource['Group'])
    extra_data = current_app.config.get(
        'OAUTHCLIENT_CERN_EXTRA_DATA_SERIALIZER',
        fetch_extra_data
    )(resource)

    account.extra_data.update(
        groups=groups,
        updated=updated.isoformat(),
        **extra_data
    )
    return groups


def extend_identity(identity, groups):
    """Extend identity with roles based on CERN groups."""
    provides = set([UserNeed(current_user.email)] + [
        RoleNeed('{0}@cern.ch'.format(name)) for name in groups
    ])
    identity.provides |= provides
    session[OAUTHCLIENT_CERN_SESSION_KEY] = provides


def disconnect_identity(identity):
    """Disconnect identity from CERN groups."""
    provides = session.pop(OAUTHCLIENT_CERN_SESSION_KEY, {})
    identity.provides -= provides


def get_dict_from_response(response):
    """Prepare new mapping with 'Value's groupped by 'Type'."""
    result = {}
    if getattr(response, '_resp') and response._resp.code > 400:
        return result

    for i in response.data:
        # strip the schema from the key
        k = i['Type'].replace(REMOTE_APP_RESOURCE_SCHEMA, '')
        result.setdefault(k, list())
        result[k].append(i['Value'])
    return result


def get_user_resources_ldap(user):
    current_app.logger.debug(f"get_user_resources_ldap")

    import ldap
    from flask import jsonify
    # assert not isinstance(user, AnonymousUser)

    query=user.email

    if not query:
        return jsonify([])

    lc = ldap.initialize('ldap://xldap.cern.ch')
    lc.search_ext(
        'OU=Users,OU=Organic Units,DC=cern,DC=ch',
        ldap.SCOPE_ONELEVEL,
        'mail=*{}*'.format(query),
        # rf,
        ['memberOf', 'mail', 'uidNumber', 'displayName'],
        serverctrls=[ldap.controls.SimplePagedResultsControl(
            True, size=20, cookie='')]
    )

    res = lc.result()[1]
    res = res[0][1]

    groups = []
    if res['mail'][0] == user.email:
        for group in res['memberOf']:
            group = group.split(',')[0]
            group = group.split('=')[1]
            groups.append(group)

    return {
        'groups': groups,
        'email': user.email,
        'cern_uid': res['uidNumber'][0],
        'name': res['displayName'][0]
    }


def get_resource(remote):
    """Query CERN Resources to get user info and groups."""
    current_app.logger.debug(f"get_resource")

    cached_resource = session.pop('cern_resource', None)
    if cached_resource:
        return cached_resource

    response = remote.get(REMOTE_APP_RESOURCE_API_URL)

    if response.status == 200:
        dict_response = get_dict_from_response(response)
        session['cern_resource'] = dict_response
        return dict_response
    else:
        response = get_user_resources_ldap(current_user)
        r = {}
        r['EmailAddress'] = [response['email']]
        r['uidNumber'] = [response['cern_uid']]
        r['CommonName'] = [response['name']]
        r['DisplayName'] = [response['name']]
        r['Group'] = response['groups']

        return r


def _account_info(remote, resp):
    """Retrieve remote account information used to find local user."""
    resource = get_resource(remote)

    valid_identities = current_app.config.get(
        'OAUTHCLIENT_CERN_ALLOWED_IDENTITY_CLASSES',
        OAUTHCLIENT_CERN_ALLOWED_IDENTITY_CLASSES
    )
    identity_class = resource.get('IdentityClass', [None])[0]
    if identity_class is None or identity_class not in valid_identities:
        raise OAuthCERNRejectedAccountError(
            'Identity class {0} is not one of [{1}]'.format(
                identity_class, ''.join(valid_identities)), remote, resp, )

    email = resource['EmailAddress'][0]
    person_id = resource.get('PersonID', [None])
    external_id = resource.get('uidNumber', person_id)[0]
    nice = resource['CommonName'][0]
    name = resource['DisplayName'][0]

    return dict(
        user=dict(
            email=email.lower(),
            profile=dict(username=nice, full_name=name),
        ),
        external_id=external_id, external_method='cern',
        active=True
    )


def account_info(remote, resp):
    """Retrieve remote account information used to find local user."""
    try:
        return _account_info(remote, resp)
    except OAuthCERNRejectedAccountError as e:
        current_app.logger.warning(e.message, exc_info=True)
        flash(_('CERN account not allowed.'), category='danger')
        return redirect('/')


def account_info_rest(remote, resp):
    """Retrieve remote account information used to find local user."""
    try:
        return _account_info(remote, resp)
    except OAuthCERNRejectedAccountError as e:
        current_app.logger.warning(e.message, exc_info=True)
        remote_app_config = current_app.config['OAUTHCLIENT_REST_REMOTE_APPS'][
            remote.name]
        return response_handler(
            remote,
            remote_app_config['error_redirect_url'],
            payload=dict(
                message='CERN account not allowed.',
                code=400)
        )


def _disconnect(remote, *args, **kwargs):
    """Handle unlinking of remote account."""
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    account = RemoteAccount.get(user_id=current_user.get_id(),
                                client_id=remote.consumer_key)
    external_id = account.extra_data.get('external_id')

    if external_id:
        oauth_unlink_external_id(dict(id=external_id, method='cern'))
    if account:
        with db.session.begin_nested():
            account.delete()

    disconnect_identity(g.identity)


def disconnect_handler(remote, *args, **kwargs):
    """Handle unlinking of remote account."""
    _disconnect(remote, *args, **kwargs)
    return redirect(url_for('invenio_oauthclient_settings.index'))


def disconnect_rest_handler(remote, *args, **kwargs):
    """Handle unlinking of remote account."""
    _disconnect(remote, *args, **kwargs)
    redirect_url = current_app.config['OAUTHCLIENT_REST_REMOTE_APPS'][
        remote.name]['disconnect_redirect_url']
    return response_handler(remote, redirect_url)


def account_setup(remote, token, resp):
    """Perform additional setup after user have been logged in."""
    resource = get_resource(remote)

    with db.session.begin_nested():
        person_id = resource.get('PersonID', [None])
        external_id = resource.get('uidNumber', person_id)[0]

        # Set CERN person ID in extra_data.
        token.remote_account.extra_data = {
            'external_id': external_id,
        }
        groups = account_groups_and_extra_data(token.remote_account, resource)
        assert not isinstance(g.identity, AnonymousIdentity)
        extend_identity(g.identity, groups)

        user = token.remote_account.user

        # Create user <-> external id link.
        oauth_link_external_id(user, dict(id=external_id, method='cern'))


@identity_changed.connect
def on_identity_changed(sender, identity):
    """Store groups in session whenever identity changes.

    :param identity: The user identity where information are stored.
    """
    current_app.logger.debug(f"on_identity_changed")

    if isinstance(identity, AnonymousIdentity):
        return

    client_id = current_app.config['CERN_APP_CREDENTIALS']['consumer_key']
    account = RemoteAccount.get(
        user_id=current_user.get_id(),
        client_id=client_id,
    )

    if account:
        groups = account.extra_data.get('groups', [])

        resources_last_updated = account.extra_data.get('updated', None)
        refresh_timedelta = current_app.config.get(
            'OAUTHCLIENT_CERN_REFRESH_TIMEDELTA',
            OAUTHCLIENT_CERN_REFRESH_TIMEDELTA
        )

        if should_refresh_groups(resources_last_updated, refresh_timedelta):
            current_app.logger.debug(f"should_refresh_groups")

            remote = find_remote_by_client_id(client_id)
            resource = get_resource(remote)

            current_app.logger.debug(f"resource {resource}")

            groups.extend(
                account_groups_and_extra_data(account, resource,
                                              refresh_timedelta=refresh_timedelta)
            )

        extend_identity(identity, groups)


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    """Store groups in session whenever identity is loaded."""
    identity.provides.update(session.get(OAUTHCLIENT_CERN_SESSION_KEY, []))
