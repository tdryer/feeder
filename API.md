# Unnamed Feed Reader API Specification

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

## Add feed
POST /feeds/

### Description
Used to add a new feed for the user.

### Request
    {
      "name": feed_name,
      "url": any_url
    }

### Response

  - 201 Created
  - 400 Bad Request: if any of the feed parameters were invalid
  - 401 Unauthorized: if user credentials are bad

## Get feed items and details
GET /feeds/:feed\_id/entries[?filter="all|read|unread"]

### Description
Get the entries (articles) of a feed that the user has access to.

### Request

### Response
    {
      "entries": [123, 345, 878978]
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed does not exist



## Delete feed
DELETE /feeds/:feed\_id

### Description
Unsubscribes the user from a feed.

### Request
None

### Response

  - 204 No Content
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed does not exist



## Get feed item
GET /feeds/:feed\_id/:entry\_id

### Description
Get the details of a specific entry.

### Request
None

### Response
    {
      "title": item_title,
      "pub-date": item_date,
      "status": "read"|"unread",
      "author": author_name,
      "feed_id": feed_id,
      "url": permalink
      "content": item_content
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed/item does not exist

## Update item details
PATCH /feeds/:feed\_id/:entry\_id

### Description
Update any modifiable item metadata that is specific to the user.

### Request
    {
      "status": "read"|"unread"
    }

### Response

  - 200 Success
  - 400 Bad Request: if I send gibberish
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed/item does not exist
