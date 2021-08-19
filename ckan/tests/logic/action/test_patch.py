# encoding: utf-8
"""Unit tests for ckan/logic/action/patch.py."""
import pytest

from ckan.tests import helpers


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestPatch(object):
    def test_package_patch_updating_single_field(self, user, package_factory):
        dataset = package_factory(
            name="annakarenina", notes="some test now", user=user
        )

        dataset = helpers.call_action(
            "package_patch", id=dataset["id"], name="somethingnew"
        )

        assert dataset["name"] == "somethingnew"
        assert dataset["notes"] == "some test now"

        dataset2 = helpers.call_action("package_show", id=dataset["id"])

        assert dataset2["name"] == "somethingnew"
        assert dataset2["notes"] == "some test now"

    def test_resource_patch_updating_single_field(self, user, package_factory):
        dataset = package_factory(
            name="annakarenina",
            notes="some test now",
            user=user,
            resources=[{"url": "http://example.com/resource"}],
        )

        resource = helpers.call_action(
            "resource_patch",
            id=dataset["resources"][0]["id"],
            name="somethingnew",
        )

        assert resource["name"] == "somethingnew"
        assert resource["url"] == "http://example.com/resource"

        dataset2 = helpers.call_action("package_show", id=dataset["id"])

        resource2 = dataset2["resources"][0]
        assert resource2["name"] == "somethingnew"
        assert resource2["url"] == "http://example.com/resource"

    def test_group_patch_updating_single_field(self, user, group_factory):
        group = group_factory(
            name="economy", description="some test now", user=user
        )

        group = helpers.call_action(
            "group_patch",
            id=group["id"],
            description="somethingnew",
            context={"user": user["name"]},
        )

        assert group["name"] == "economy"
        assert group["description"] == "somethingnew"

        group2 = helpers.call_action("group_show", id=group["id"])

        assert group2["name"] == "economy"
        assert group2["description"] == "somethingnew"

    @pytest.mark.ckan_config(u"ckan.auth.public_user_details", u"false")
    def test_group_patch_updating_single_field_when_public_user_details_is_false(self, user, group_factory):
        group = group_factory(
            name="economy", description="some test now", user=user
        )

        group = helpers.call_action(
            "group_patch",
            id=group["id"],
            description="somethingnew",
            context={"user": user["name"]},
        )

        assert group["name"] == "economy"
        assert group["description"] == "somethingnew"

        group2 = helpers.call_action("group_show", id=group["id"], include_users=True)

        assert group2["name"] == "economy"
        assert group2["description"] == "somethingnew"
        assert len(group2["users"]) == 1
        assert group2["users"][0]["name"] == user["name"]

    def test_group_patch_preserve_datasets(self, user, group_factory, package_factory):
        group = group_factory(
            name="economy", description="some test now", user=user
        )
        package_factory(groups=[{"name": group["name"]}])

        group2 = helpers.call_action("group_show", id=group["id"])
        assert 1 == group2["package_count"]

        group = helpers.call_action(
            "group_patch", id=group["id"], context={"user": user["name"]}
        )

        group3 = helpers.call_action("group_show", id=group["id"])
        assert 1 == group3["package_count"]

        group = helpers.call_action(
            "group_patch",
            id=group["id"],
            packages=[],
            context={"user": user["name"]},
        )

        group4 = helpers.call_action(
            "group_show", id=group["id"], include_datasets=True
        )
        assert 0 == group4["package_count"]

    def test_organization_patch_updating_single_field(self, user, organization_factory):
        organization = organization_factory(
            name="economy", description="some test now", user=user
        )

        organization = helpers.call_action(
            "organization_patch",
            id=organization["id"],
            description="somethingnew",
            context={"user": user["name"]},
        )

        assert organization["name"] == "economy"
        assert organization["description"] == "somethingnew"

        organization2 = helpers.call_action(
            "organization_show", id=organization["id"]
        )

        assert organization2["name"] == "economy"
        assert organization2["description"] == "somethingnew"

    @pytest.mark.ckan_config(u"ckan.auth.public_user_details", u"false")
    def test_organization_patch_updating_single_field_when_public_user_details_is_false(self, user, organization_factory):
        organization = organization_factory(
            name="economy", description="some test now", user=user
        )

        organization = helpers.call_action(
            "organization_patch",
            id=organization["id"],
            description="somethingnew",
            context={"user": user["name"]},
        )

        assert organization["name"] == "economy"
        assert organization["description"] == "somethingnew"

        organization2 = helpers.call_action(
            "organization_show", id=organization["id"], include_users=True
        )

        assert organization2["name"] == "economy"
        assert organization2["description"] == "somethingnew"
        assert len(organization2["users"]) == 1
        assert organization2["users"][0]["name"] == user["name"]

    def test_user_patch_updating_single_field(self, user_factory):
        user = user_factory(
            fullname="Mr. Test User",
            about="Just another test user.",
        )

        user = helpers.call_action(
            "user_patch",
            id=user["id"],
            about="somethingnew",
            context={"user": user["name"]},
        )

        assert user["fullname"] == "Mr. Test User"
        assert user["about"] == "somethingnew"

        user2 = helpers.call_action("user_show", id=user["id"])

        assert user2["fullname"] == "Mr. Test User"
        assert user2["about"] == "somethingnew"
