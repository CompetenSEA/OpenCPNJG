# Backend endpoints

This service exposes a small HTTP API for chart access.

## /charts

Returns the catalog of chart datasets known to the server.  Each entry
includes the dataset identifier, title, bounds and zoom range.

```
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/charts
```

## Authentication

Most endpoints expect a bearer token supplied in the `Authorization`
header.  Tokens are application specific and can be issued by the
backend.

## Example usage

Fetching details for a specific chart:

```
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/charts/US5NY1BF
```
