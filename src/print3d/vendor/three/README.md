# three.js r160, vendored

view.html carries these files inline, so the 3D view opens with no network
(a file saved from a chat app, a phone, an offline laptop). They are unmodified
copies from the npm package `three@0.160.0`
(`https://registry.npmjs.org/three/-/three-0.160.0.tgz`, integrity
`sha512-DLU8lc0zNIPkM7rH5/e1Ks1Z8tWCGRq6g8mPowdDJpw1CFBJMU7UoJjC6PefXW7z//SSl0b2+GCw14LB+uDhng==`).

| File | From the package | sha256 |
|---|---|---|
| `three.module.min.js` | `build/three.module.min.js` | `3e690ac7d180b0aadf0891bea39eec643e29e2d3e75c99b18689518665f69ba6` |
| `OrbitControls.js` | `examples/jsm/controls/OrbitControls.js` | `5a44a9e86a2a0fb11933eed69bc2cd33c76a496854c1aed6ed776efa87d7b064` |
| `STLLoader.js` | `examples/jsm/loaders/STLLoader.js` | `896d006a48b8f125385a485ccae154dadee801a953f0b45ceffe7ddd8a29ca93` |
| `LICENSE` | `LICENSE` (MIT) | `852e0e8699169bf9f6fdc6bda3e682d078dcbc738b5d33e74df594721bff271d` |

`tests/test_viewer.py` checks the hashes. To move to another release, copy the
same four files from its package, update this table and the test, and check
that the viewer still renders.
