Summary

Added stage_local_assets.py to copy S-52/S-57 assets from data/s57data/ into dist/assets/s52 and emit a manifest (local, reproducible; no network).

Extended build_all_styles.py with --emit-name; still validates Day/Dusk/Night.

Broadened coverage to scan all generated styles and surfaced deltas; docs now show missing OBJL and delta.

Expanded ignore rules to keep generated binaries and dist artifacts out of Git.

Added a regression test that ingests every S-57 object class and encodes to MVT to ensure safe handling.

Testing

See the commands above; all bullets must pass locally.

Risks & Rollback

Doc-only & tooling changes; rollback by deleting the new helper and reverting touched files. No runtime behavior change apart from improved docs/coverage.
