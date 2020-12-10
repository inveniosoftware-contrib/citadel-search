# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2021 CERN.
#
# Citadel Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for access/CRUD permissions."""
import pytest

from cern_search_rest_api.modules.cernsearch.permissions import (
    has_delete_permission,
    has_list_permission,
    has_owner_permission,
    has_read_record_permission,
    has_update_permission,
)


@pytest.fixture(scope="module")
def app_config(app_config):
    """Application configuration fixture."""
    app_config["SEARCH_INSTANCE_IMMUTABLE"] = True

    return app_config


def test_has_list_permission(appctx, anonymous_user, authenticated_user):
    """Test list records (search) permission."""
    assert has_list_permission(anonymous_user)
    assert has_list_permission(authenticated_user)


def test_has_read_record_permission(
    appctx,
    mocker,
    anonymous_user,
    authenticated_user,
    private_access_record,
    public_access_record,
):
    """Test read record permission."""
    # Anonymous usertest_file_ops
    assert not has_read_record_permission(anonymous_user, public_access_record)
    assert not has_read_record_permission(anonymous_user, private_access_record)

    # User with no rights over private record and public record
    patched_g = mocker.patch("cern_search_rest_api.modules.cernsearch.utils.g")
    patched_g.identity.provides = []
    assert not has_read_record_permission(authenticated_user, public_access_record)
    assert not has_read_record_permission(authenticated_user, private_access_record)

    # User with read permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="read-perm")]
    assert not has_read_record_permission(authenticated_user, private_access_record)

    # User with update permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="update-perm")]
    assert not has_read_record_permission(authenticated_user, private_access_record)

    # User with delete permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="delete-perm")]
    assert not has_read_record_permission(authenticated_user, private_access_record)

    # User with owner permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="owner-perm")]
    assert not has_read_record_permission(authenticated_user, private_access_record)


def test_has_update_permission(
    appctx,
    mocker,
    anonymous_user,
    authenticated_user,
    private_access_record,
    public_access_record,
):
    """Test update record permission."""
    # Anonymous user cannot update
    assert not has_update_permission(anonymous_user, public_access_record)

    # User with no rights over private record and public record
    patched_g = mocker.patch("cern_search_rest_api.modules.cernsearch.utils.g")
    patched_g.identity.provides = []
    assert not has_update_permission(authenticated_user, public_access_record)
    assert not has_update_permission(authenticated_user, private_access_record)

    # User with read permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="read-perm")]
    assert not has_update_permission(authenticated_user, private_access_record)

    # User with update permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="update-perm")]
    assert not has_update_permission(authenticated_user, private_access_record)

    # User with delete permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="delete-perm")]
    assert not has_update_permission(authenticated_user, private_access_record)

    # User with owner permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="owner-perm")]
    assert not has_update_permission(authenticated_user, private_access_record)


def test_has_delete_permission(
    appctx,
    mocker,
    anonymous_user,
    authenticated_user,
    private_access_record,
    public_access_record,
):
    """Test delete record permission."""
    # Anonymous user cannot update
    assert not has_delete_permission(anonymous_user, public_access_record)

    # User with no rights over private record and public record
    patched_g = mocker.patch("cern_search_rest_api.modules.cernsearch.utils.g")
    patched_g.identity.provides = []
    assert not has_delete_permission(authenticated_user, public_access_record)
    assert not has_delete_permission(authenticated_user, private_access_record)

    # User with read permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="read-perm")]
    assert not has_delete_permission(authenticated_user, private_access_record)

    # User with update permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="update-perm")]
    assert not has_delete_permission(authenticated_user, private_access_record)

    # User with delete permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="delete-perm")]
    assert not has_delete_permission(authenticated_user, private_access_record)

    # User with owner permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="owner-perm")]
    assert not has_delete_permission(authenticated_user, private_access_record)


def test_has_owner_permission(
    appctx,
    mocker,
    anonymous_user,
    authenticated_user,
    private_access_record,
    public_access_record,
):
    """Test colletion/schema owner permission."""
    appctx.config["ADMIN_ACCESS_GROUPS"] = "non-existing-perm,owner-perm"
    # Anonymous user cannot update
    assert not has_owner_permission(anonymous_user, public_access_record)

    # Authenticated user when theres no record
    assert not has_owner_permission(authenticated_user, None)
    assert not has_owner_permission(authenticated_user)

    # User with no rights over private record and public record
    patched_g = mocker.patch("cern_search_rest_api.modules.cernsearch.utils.g")
    patched_g.identity.provides = []
    assert not has_owner_permission(authenticated_user, public_access_record)
    assert not has_owner_permission(authenticated_user, private_access_record)

    # User with read permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="read-perm")]
    assert not has_owner_permission(authenticated_user, private_access_record)

    # User with update permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="update-perm")]
    assert not has_owner_permission(authenticated_user, private_access_record)

    # User with delete permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="delete-perm")]
    assert not has_owner_permission(authenticated_user, private_access_record)

    # User with owner permissions
    patched_g.identity.provides = [mocker.Mock(method="perm", value="owner-perm")]
    assert not has_owner_permission(authenticated_user, private_access_record)
