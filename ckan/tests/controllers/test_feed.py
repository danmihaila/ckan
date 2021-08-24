# encoding: utf-8

import pytest

from ckan.lib.helpers import url_for

import ckan.tests.helpers as helpers
import ckan.plugins as plugins


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestFeeds(object):
    @pytest.mark.parametrize("page", [0, -2, "abc"])
    def test_atom_feed_incorrect_page_gives_error(self, page, app, group):
        offset = url_for(
            u"feeds.group", id=group["name"]
        ) + u"?page={}".format(page)
        res = app.get(offset, status=400)
        assert (
            "&#34;page&#34; parameter must be a positive integer" in res
        ), res

    def test_general_atom_feed_works(self, app, package):
        offset = url_for(u"feeds.general")
        res = app.get(offset)

        assert helpers.body_contains(res, u"<title>{0}</title>".format(package["title"]))

    def test_group_atom_feed_works(self, app, group, package_factory):
        dataset = package_factory(groups=[{"id": group["id"]}])
        offset = url_for(u"feeds.group", id=group["name"])
        res = app.get(offset)

        assert helpers.body_contains(res, u"<title>{0}</title>".format(dataset["title"]))

    def test_organization_atom_feed_works(self, app, package_factory, organization):
        dataset = package_factory(owner_org=organization["id"])
        offset = url_for(u"feeds.organization", id=organization["name"])
        res = app.get(offset)

        assert helpers.body_contains(res, u"<title>{0}</title>".format(dataset["title"]))

    def test_custom_atom_feed_works(self, app, package_factory):
        dataset1 = package_factory(
            title=u"Test weekly",
            extras=[{"key": "frequency", "value": "weekly"}],
        )
        dataset2 = package_factory(
            title=u"Test daily",
            extras=[{"key": "frequency", "value": "daily"}],
        )

        offset = url_for(u"feeds.custom")
        params = {"q": "frequency:weekly"}

        res = app.get(offset, query_string=params)

        assert helpers.body_contains(res, u"<title>{0}</title>".format(dataset1["title"]))

        assert not helpers.body_contains(res, u'<title">{0}</title>'.format(dataset2["title"]))


class MockFeedPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFeed)

    def get_item_additional_fields(self, dataset_dict):
        extras = {e["key"]: e["value"] for e in dataset_dict["extras"]}

        box = tuple(
            float(extras.get(n)) for n in ("ymin", "xmin", "ymax", "xmax")
        )
        return {"geometry": box}
