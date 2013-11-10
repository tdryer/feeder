# Unnamed Feed Reader API Specification

## List all feeds
GET /feeds/

### Description
Returns the feeds (in the form of feed_ids) that the user has access to.

### Request
None

### Response
    {
      'feeds': [feed_id]
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad

## Add feed
POST /feeds/

### Description
Used to add a new feed for the user.

### Request
    {
      'name': feed_name,
      'url': feed_url
    }

### Response

  - 201 Created
  - 400 Bad Request: if any of the feed parameters were invalid
  - 401 Unauthorized: if user credentials are bad

## Get feed items and details
GET /feeds/:feed\_id

### Description
Get the details of a feed that the user has access to, including the items (in the form of
item_id) that the feed has.

### Request
None

### Response
    {
      'name': feed_name,
      'url': feed_url,
      'last_update': feed_last_update,
      'next_update': feed_next_update,
      'items': [item_id]
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed does not exist

## Update feed details
PATCH /feeds/:feed\_id

### Description
Update any modifiable metadata of the feed that is specific to the user.

### Request
    {
      'name': new_feed_name
    }

### Response

  - 200 Success
  - 400 Bad Request: if any of the feed parameters were invalid
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed does not exist

## Delete feed
DELETE /feeds/:feed\_id

### Description
Deletes a feed for the user.

### Request
None

### Response

  - 204 No Content
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed does not exist

## Get feed item
GET /feeds/:feed\_id/:item\_id

### Description
Get the details of a specific feed item.

### Request
None

### Response
    {
      'title': item_title,
      'posted_on': item_date,
      'content': item_content,
      'read': item_read
    }

  - 200 Success
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed/item does not exist

## Update item details
PATCH /feeds/:feed\_id/:item\_id

### Description
Update any modifiable item metadata that is specific to the user.

### Request
    {
      'read': true/false
    }

### Response

  - 200 Success
  - 401 Unauthorized: if user credentials are bad
  - 403 Forbidden: if the user does not have permission to access this feed
  - 404 Not Found: if the feed/item does not exist
