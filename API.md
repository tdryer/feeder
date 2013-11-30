# Unnamed Feed Reader API Specification

Every API endpoint requires HTTP Basic Authentication unless stated otherwise.

## Register a new user
POST /users/

### Description
Registers a new using with the given username and password. Authentication is
not required.

### Request
    {
      "username": "username",
      "password": "password",
    }

### Response

  - 201 Created
  - 400 Bad Request: Invalid request body, those credentials are already taken,
    or unsuitable credentials

---

## Get user information
GET /users/

### Description
Returns information about the current user.

### Request
None

### Response
    {
        "username": "Heyzeus Crisco"
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad

---

## List all feeds
GET /feeds/

### Description
Returns the feeds (in the form of feed_ids) that the user has access to.

### Request
None

### Response
    {
      "feeds": [{
        "id": 123,
        "name": "David yan blog",
        "url": "awesome-blog.com",
        "unreads": 123
      }, {
        ...
      }]
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad

---

## Get a single feed
GET /feeds/:feed\_id

## Description
Returns the metadata for a particular feed

## Request
None

## Response
    {
        "id": 123,
        "name": "David yan blog",
        "url": "awesome-blog.com",
        "unreads": 123
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad
  - 404 Not Found: if feed does not exist or user is not subscribed

---

## Add feed
POST /feeds/

### Description
Subscribe the user to a new feed by URL.

### Request
    {
      "url": any_url
    }

### Response

  - 201 Created
  - 400 Bad Request: if any of the feed parameters were invalid, or feed could not be added, or user is already subscribed to feed
  - 401 Unauthorized: if user credentials are bad

---

## Get feed items and details
GET /feeds/:feed\_id/entries[?filter="read|unread"]

### Description
Get the entry (article) ids of a feed that the user has access to.

### Request

### Response
    {
      "entries": [123, 345, 878978]
    }

  - 200 Success
  - 400 Bad Request: if the filter value is not valid
  - 401 Unauthorized: if user credentials are bad
  - 404 Not Found: if feed does not exist or user is not subscribed

---

## Delete feed
DELETE /feeds/:feed\_id

### Description
Unsubscribes the user from a feed.

### Request
None

### Response

  - 204 No Content
  - 401 Unauthorized: if user credentials are bad
  - 404 Not Found: if feed does not exist or user is not subscribed

---

## Get feed item
GET /entries/:entry\_id(,entry\_id,...)

### Description
Get the details of entries.

### Request
None

### Response
    {
      "entries": [{
          "id": entry_id,
          "title": entry_title,
          "pub-date": entry_date,
          "status": "read"|"unread",
          "author": entry_author_name,
          "feed_id": feed_id,
          "url": entry_permalink
          "content": entry_content
      }, { ... }]
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad
  - 404 Not Found: if an entry does not exist

---

## Update item details
PATCH /entries/:entry\_id(,entry\_id,...)

### Description
Update any modifiable entry metadata for that user.

### Request
    {
      "status": "read"|"unread"
    }

### Response

  - 200 Success
  - 400 Bad Request: if I send gibberish
  - 401 Unauthorized: if user credentials are bad
  - 404 Not Found: if an entry does not exist
