#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Handlers for customizing oauthclient endpoints."""

from __future__ import absolute_import, print_function

from cern_search_rest_api.modules.cernsearch.utils import get_user_provides
from flask import after_this_request, current_app, g, redirect, session, url_for
from flask_login import current_user, user_logged_in
from flask_security import logout_user
from flask_security.utils import get_post_logout_redirect
from invenio_db import db
from invenio_oauthclient.handlers import (get_session_next_url, oauth_error_handler, response_token_setter,
                                          token_getter, token_session_key)
from invenio_oauthclient.proxies import current_oauthclient
from invenio_oauthclient.signals import account_info_received, account_setup_committed, account_setup_received
from invenio_oauthclient.utils import (create_csrf_disabled_registrationform, fill_form, oauth_authenticate,
                                       oauth_get_user, oauth_register)


@oauth_error_handler
def cern_authorized_signup_handler(resp, remote, *args, **kwargs):
    """Handle sign-in/up functionality.
    :param remote: The remote application.
    :param resp: The response.
    :returns: Redirect response.
    """
    # Remove any previously stored auto register session key
    session.pop(token_session_key(remote.name) + '_autoregister', None)

    # Store token in session
    # ----------------------
    # Set token in session - token object only returned if
    # current_user.is_authenticated().
    token = response_token_setter(remote, resp)
    handlers = current_oauthclient.signup_handlers[remote.name]

    # Sign-in/up user
    # ---------------
    if not current_user.is_authenticated:
        account_info = handlers['info'](resp)
        account_info_received.send(
            remote, token=token, response=resp, account_info=account_info
        )

        user = oauth_get_user(
            remote.consumer_key,
            account_info=account_info,
            access_token=token_getter(remote)[0],
        )
        if user is None:
            # Auto sign-up if user not found
            form = create_csrf_disabled_registrationform()
            form = fill_form(
                form,
                account_info['user']
            )
            user = oauth_register(form)

            # if registration fails ...
            if user is None:
                # requires extra information
                session[
                    token_session_key(remote.name) + '_autoregister'] = True
                session[token_session_key(remote.name) +
                        '_account_info'] = account_info
                session[token_session_key(remote.name) +
                        '_response'] = resp
                db.session.commit()
                return redirect(url_for(
                    '.signup',
                    remote_app=remote.name,
                ))
        # Authenticate user
        if not oauth_authenticate(remote.consumer_key, user,
                                  require_existing_link=False):
            return current_app.login_manager.unauthorized()

        # Link account
        # ------------
        # Need to store token in database instead of only the session when
        # called first time.
        token = response_token_setter(remote, resp)

    # Setup account
    # -------------
    if not token.remote_account.extra_data:
        account_setup = handlers['setup'](token, resp)
        account_setup_received.send(
            remote, token=token, response=resp, account_setup=account_setup
        )
        db.session.commit()
        account_setup_committed.send(remote, token=token)
    else:
        db.session.commit()

    # Redirect to next
    if current_user.is_authenticated and not egroup_admin():
        logout_user()
        return redirect(get_post_logout_redirect())

    next_url = get_session_next_url(remote.name)
    if next_url:
        return redirect(next_url)
    return redirect(url_for('invenio_oauthclient_settings.index'))


def egroup_admin():
    admin_access_groups = current_app.config['ADMIN_ACCESS_GROUPS']
    # Allow based in the '_access' key
    user_provides = get_user_provides()
    # set.isdisjoint() is faster than set.intersection()
    admin_access_groups = admin_access_groups.split(',')
    return user_provides and not set(user_provides).isdisjoint(set(admin_access_groups))
