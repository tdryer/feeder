"""Functional tests for the API."""

from tornado.testing import AsyncHTTPTestCase
import base64
import json

import feedreader.main
from feedreader.database import models


# TODO: these should probably be attributes of ApiTest
TEST_USER = "username1"
TEST_PASSWORD = "password1"
TEST_NEW_USER = "username2"
TEST_NEW_PASSWORD = "password2"


def get_basic_auth(user, passwd):
    """Return basic auth header."""
    return "Basic " + base64.b64encode("{}:{}".format(user, passwd))


class ApiTest(AsyncHTTPTestCase):

    def setUp(self):
        super(ApiTest, self).setUp()

        # create the TEST_USER
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": TEST_USER, "password": TEST_PASSWORD})
        )
        self.assertEqual(response.code, 201)
        self.headers = {
            'Authorization': get_basic_auth(TEST_USER, TEST_PASSWORD),
        }

        # create a session and some model instances for tests to use
        self.s = self.Session()
        self.feed1 = models.Feed("Tombuntu",
                                 "http://feeds.feedburner.com/Tombuntu",
                                 "http://tombuntu.com")
        self.feed1_entry1 = models.Entry(
            None, "This is test content.", "http://tombuntu.com/test-content",
            "Test title", "Tom", 1384402853
        )
        # TODO: make this entry different
        self.feed1_entry2 = models.Entry(
            None, "This is test content.",
            "http://tombuntu.com/test-content", "Test title", "Tom", 1384402853
        )
        self.sub1 = models.Subscription(TEST_USER, None)
        self.read1 = models.Read(TEST_USER, None)

    def tearDown(self):
        self.s.close()
        super(ApiTest, self).tearDown()

    def get_app(self):
        # hack to get access to the session class
        def hook(Session): self.Session = Session
        return feedreader.main.get_application(db_setup_f=hook)

    def assert_api_call(self, api_call, headers=None, json_body=None,
                        expect_code=None, expect_json=None):
        """Make an API call with optional assertions."""
        method, url = api_call.split(" ", 1)
        body = None if json_body is None else json.dumps(json_body)
        response = self.fetch(url, method=method, body=body, headers=headers)
        if expect_code is not None:
            self.assertEqual(
                response.code, expect_code,
                "Expected {} to return {}, but it returned {}. "
                "Response body was:\n{}"
                .format(api_call, expect_code, response.code, response.body)
            )
        if expect_json is not None:
            self.assertEqual(json.loads(response.body), expect_json)
        try:
            return json.loads(response.body)
        except ValueError:
            return None

    def add_commit(self, model, model_patches=None):
        """Add a model instance to the session and commit."""
        if model_patches is not None:
            for key, val in model_patches.iteritems():
                setattr(model, key, val)
        self.s.add(model)
        self.s.commit()

    ######################################################################
    # POST /users/
    ######################################################################

    def test_create_new_user(self):
        self.assert_api_call("POST /users", json_body={
            "username": TEST_NEW_USER, "password": TEST_NEW_PASSWORD
        }, expect_code=201)
        # try a request to check that it worked
        self.assert_api_call("GET /", headers={
            "Authorization": get_basic_auth(TEST_NEW_USER, TEST_NEW_PASSWORD),
        }, expect_code=200)

    def test_create_new_user_invalid_body(self):
        self.assert_api_call("POST /users", json_body={
            "username": TEST_NEW_USER,
        }, expect_code=400)

    def test_create_new_user_empty_username(self):
        self.assert_api_call("POST /users", json_body={
            "username": "", "password": TEST_NEW_PASSWORD,
        }, expect_code=400)

    def test_create_new_user_empty_password(self):
        self.assert_api_call("POST /users", json_body={
            "username": TEST_NEW_USER, "password": "",
        }, expect_code=400)

    def test_create_duplicate_username(self):
        self.assert_api_call("POST /users", json_body={
            "username": TEST_NEW_USER, "password": TEST_NEW_PASSWORD
        }, expect_code=201)
        res = self.assert_api_call("POST /users", json_body={
            "username": TEST_NEW_USER, "password": TEST_NEW_PASSWORD
        }, expect_code=400)
        self.assertIn("Username already registered", res["error"]["message"])

    ######################################################################
    # GET /users/
    ######################################################################

    def test_get_user_requires_auth(self):
        self.assert_api_call("GET /users", expect_code=401)

    def test_get_user(self):
        self.assert_api_call("GET /users", headers=self.headers,
                             expect_code=200,
                             expect_json={"username": TEST_USER})

    ######################################################################
    # GET /feeds/
    ######################################################################

    def test_get_feeds_requires_auth(self):
        self.assert_api_call("GET /feeds", expect_code=401)

    def test_get_feeds_empty(self):
        self.assert_api_call("GET /feeds", headers=self.headers,
                             expect_code=200,
                             expect_json={"feeds": []})

    def test_get_feeds(self):
        # add a feed with an entry, and subscribe to it
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.assert_api_call('GET /feeds/', headers=self.headers,
                             expect_code=200, expect_json={
            "feeds": [
                {
                    "id": self.feed1.id,
                    "name": self.feed1.title,
                    "url": self.feed1.site_url,
                    "unreads": 1,
                },
            ],

        })

    def test_get_feeds_only_shows_subscribed_feeds(self):
        # add a feed with an entry
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.assert_api_call("GET /feeds", headers=self.headers,
                             expect_code=200,
                             expect_json={"feeds": []})

    def test_get_feeds_does_not_count_read_entries(self):
        # add a feed with an entry, subscribe to it, and read the entry
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.add_commit(self.read1, {"entry_id": self.feed1_entry1.id})
        self.assert_api_call('GET /feeds/', headers=self.headers,
                             expect_code=200, expect_json={
            "feeds": [
                {
                    "id": self.feed1.id,
                    "name": self.feed1.title,
                    "url": self.feed1.site_url,
                    "unreads": 0,
                },
            ],

        })

    ######################################################################
    # POST /feeds/
    ######################################################################

    def test_add_feed_requires_auth(self):
        self.assert_api_call("POST /feeds", json_body={
            'url': 'http://awesome-blog.github.io'
        }, expect_code=401)

    def test_add_feed_success(self):
        # TODO: mock this so we're not (slowly) fetching a real feed here
        self.assert_api_call("POST /feeds", headers=self.headers, json_body={
            'url': 'http://awesome-blog.github.io'
        }, expect_code=201)

    def test_duplicate_subscription(self):
        self.assert_api_call("POST /feeds", headers=self.headers, json_body={
            'url': 'http://awesome-blog.github.io'
        }, expect_code=201)
        # try subscribing to the feed a second time
        self.assert_api_call("POST /feeds", headers=self.headers, json_body={
            'url': 'http://awesome-blog.github.io'
        }, expect_code=400)

    ######################################################################
    # GET /feeds/ID/entries
    ######################################################################

    def test_get_feed_entries_requires_auth(self):
        self.assert_api_call("GET /feeds/1/entries", expect_code=401)

    def test_get_feed_entries_feed_does_not_exist(self):
        self.assert_api_call("GET /feeds/1/entries", headers=self.headers,
                             expect_code=404)

    def test_get_feed_entries_all(self):
        # add a feed with an entry, and subscribe to it
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.assert_api_call("GET /feeds/{}/entries".format(self.feed1.id),
                             headers=self.headers, expect_code=200,
                             expect_json={"entries": [self.feed1_entry1.id]})

    def test_get_feed_entries_unread(self):
        # add feed with 2 entries, subscribe to the feed, read the first entry
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.feed1_entry2, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.add_commit(self.read1, {"entry_id": self.feed1_entry1.id})
        self.assert_api_call(
            "GET /feeds/{}/entries?filter=unread".format(self.feed1.id),
            headers=self.headers, expect_code=200,
            expect_json={"entries": [self.feed1_entry2.id]}
        )

    def test_get_feed_entries_read(self):
        # add feed with 2 entries, subscribe to the feed, read the first entry
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.feed1_entry2, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.add_commit(self.read1, {"entry_id": self.feed1_entry1.id})
        self.assert_api_call(
            "GET /feeds/{}/entries?filter=read".format(self.feed1.id),
            headers=self.headers, expect_code=200,
            expect_json={"entries": [self.feed1_entry1.id]}
        )

    def test_get_feed_entries_invalid_filter(self):
        # add feed, subscribe to the feed
        self.add_commit(self.feed1)
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.assert_api_call(
            "GET /feeds/{}/entries?filter=foobar".format(self.feed1.id),
            headers=self.headers, expect_code=400
        )

    ######################################################################
    # GET /entries/ID
    ######################################################################

    def test_get_entries_requires_auth(self):
        self.assert_api_call("GET /entries/1", expect_code=401)

    def test_get_entries_does_not_exist(self):
        self.assert_api_call("GET /entries/1", headers=self.headers,
                             expect_code=404)

    def test_get_entries_single(self):
        # add feed with 2 entries, subscribe to the feed, read the first entry
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.feed1_entry2, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.add_commit(self.read1, {"entry_id": self.feed1_entry1.id})
        self.assert_api_call(
            "GET /entries/{}".format(self.feed1_entry1.id),
            headers=self.headers, expect_code=200, expect_json={
                "entries": [
                    {
                        "id": self.feed1_entry1.id,
                        "title": self.feed1_entry1.title,
                        "pub-date": self.feed1_entry1.date,
                        "status": self.feed1_entry1.been_read(self.s,
                                                              TEST_USER),
                        "author": self.feed1_entry1.author,
                        "feed_id": self.feed1.id,
                        "url": self.feed1_entry1.url,
                        "content": self.feed1_entry1.content,
                    },
                ]
        })

    def test_get_entries_multiple(self):
        # add feed with 2 entries, subscribe to the feed, read the first entry
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.feed1_entry2, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.add_commit(self.read1, {"entry_id": self.feed1_entry1.id})
        self.assert_api_call(
            "GET /entries/{},{}".format(self.feed1_entry1.id,
                                        self.feed1_entry2.id),
            headers=self.headers, expect_code=200, expect_json={
                "entries": [
                    {
                        "id": self.feed1_entry1.id,
                        "title": self.feed1_entry1.title,
                        "pub-date": self.feed1_entry1.date,
                        "status": self.feed1_entry1.been_read(self.s,
                                                              TEST_USER),
                        "author": self.feed1_entry1.author,
                        "feed_id": self.feed1.id,
                        "url": self.feed1_entry1.url,
                        "content": self.feed1_entry1.content,
                    },
                    {
                        "id": self.feed1_entry2.id,
                        "title": self.feed1_entry2.title,
                        "pub-date": self.feed1_entry2.date,
                        "status": self.feed1_entry2.been_read(self.s,
                                                              TEST_USER),
                        "author": self.feed1_entry2.author,
                        "feed_id": self.feed1.id,
                        "url": self.feed1_entry2.url,
                        "content": self.feed1_entry2.content,
                    },
                ]
        })

    ######################################################################
    # PATCH /entries/ID
    ######################################################################

    def test_patch_entries_requires_auth(self):
        self.assert_api_call("PATCH /entries/1",
                             json_body={"status": "read"},
                             expect_code=401)

    def test_path_entries_bad_input_value(self):
        self.assert_api_call("PATCH /entries/1", headers=self.headers,
                             json_body={
                                 "status": ""
                             }, expect_code=400)

    def test_path_entries_bad_input_keyword(self):
        self.assert_api_call("PATCH /entries/1", headers=self.headers,
                             json_body={
                                 "what": "read"
                             }, expect_code=400)

    def test_patch_entries_not_exists(self):
        self.assert_api_call("PATCH /entries/1", headers=self.headers,
                             json_body={
                                 "status": "read"
                             }, expect_code=404)

    def test_patch_entries_not_subbed(self):
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.assert_api_call("PATCH /entries/1", headers=self.headers,
                             json_body={
                                 "status": "read"
                             }, expect_code=403)

    def test_patch_entries_update_read(self):
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.feed1_entry2, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.assert_api_call("PATCH /entries/1,2", headers=self.headers,
                             json_body={
                                 "status": "read"
                             }, expect_code=200)

    def test_patch_entries_update_unread(self):
        self.add_commit(self.feed1)
        self.add_commit(self.feed1_entry1, {"feed_id": self.feed1.id})
        self.add_commit(self.feed1_entry2, {"feed_id": self.feed1.id})
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.add_commit(self.read1, {"entry_id": self.feed1_entry1.id})
        self.assert_api_call("PATCH /entries/1,2", headers=self.headers,
                             json_body={
                                 "status": "unread"
                             }, expect_code=200)

    ######################################################################
    # GET /feeds/ID
    ######################################################################

    def test_get_feed_requires_auth(self):
        self.assert_api_call("GET /feeds/1", expect_code=401)

    def test_get_feed_not_found(self):
        self.assert_api_call("GET /feeds/1", headers=self.headers,
                             expect_code=404)

    def test_get_feed_unsubscribed(self):
        # add a feed
        self.add_commit(self.feed1)
        self.assert_api_call("GET /feeds/{}".format(self.feed1.id),
                             headers=self.headers, expect_code=404)

    def test_get_feed(self):
        # add a feed and subscribe to it
        self.add_commit(self.feed1)
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.assert_api_call(
            "GET /feeds/{}".format(self.feed1.id), headers=self.headers,
            expect_code=200, expect_json={
                'id': self.feed1.id,
                'name': self.feed1.title,
                'unreads': 0,
                'url': self.feed1.site_url,
        })

    ######################################################################
    # DELETE /feeds/ID
    ######################################################################

    def test_delete_feed_requires_auth(self):
        self.assert_api_call("DELETE /feeds/1", expect_code=401)

    def test_delete_feed_unsubbed_user(self):
        # add a feed
        self.add_commit(self.feed1)
        self.assert_api_call("DELETE /feeds/{}".format(self.feed1.id),
                             headers=self.headers, expect_code=404)

    def test_delete_feed_does_not_exist(self):
        self.assert_api_call("DELETE /feeds/{}".format(self.feed1.id),
                             headers=self.headers, expect_code=404)

    def test_delete_feed(self):
        # add a feed and subscribe to it
        self.add_commit(self.feed1)
        self.add_commit(self.sub1, {"feed_id": self.feed1.id})
        self.assert_api_call("DELETE /feeds/{}".format(self.feed1.id),
                             headers=self.headers, expect_code=204)
