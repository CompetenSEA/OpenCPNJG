# ocpn-mini vendor

The `cpp/vendor/ocpn-mini` directory bundles C++ sources copied from the
[OpenCPN](https://github.com/OpenCPN/OpenCPN) project at commit `867b06a`.
These files are licensed under the GNU General Public License version 2 or,
at your option, any later version.  The full license text is included in
`cpp/vendor/ocpn-mini/LICENSE`.

Vendored paths:

- `gui/src/Osenc.cpp`
- `gui/src/cm93.cpp`
- `gui/src/s57chart.cpp`
- `libs/s52plib/src/*`

The sources are minimally pruned to remove tests and platform-specific code so
that the bridge can build a reduced chart stack when `OPB_WITH_OCPN_MINI=ON`.
