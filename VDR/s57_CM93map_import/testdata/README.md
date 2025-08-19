Binary sample data is omitted from version control.
Populate this directory with:

- `enc/` containing S-57 cell `.000` files
- `cm93/` containing a CM93 dataset root

`tools/build.sh` will run `dump-s57` or `dump-cm93` if these paths exist.
