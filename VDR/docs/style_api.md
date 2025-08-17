# Style API

The style bundle consumes CM93 tiles without mariner parameters. Two vector
sources are expected:

- `cm93-core` – feature geometry
- `cm93-label` – dictionary-coded labels

Clients fetch `/tiles/cm93/dict.json` and use the integer codes in MapLibre
style expressions. Mariner safety, shallow and deep parameters are applied via
style expressions and **no URL parameters** are appended to tile requests.
