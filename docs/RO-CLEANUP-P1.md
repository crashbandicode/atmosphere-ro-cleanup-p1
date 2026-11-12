# RO failed-load cleanup patch 1

2026-11-03; rebased 2026-11-12 onto Atmosphere 1.12.2 (`4e3f37038d9e82dde7054897213ab32b2ecf651f`).
After a successful NRO map, the existing unmap guard is registered before the parser.
Failed parsing, including authorization failure, releases the NRO/BSS mappings
and returns the original error. Success keeps the mapping. Authorization stays enforced.

System Settings shows `AMS 1.12.2p1` with `S` or `E`. Numeric API fields stay 1.12.2.

`python3 -I tests/ro_cleanup_p1/run.py` compiles the map/parse region with real Vapours
guards and injects map failure, parse failure, and success. The official baseline must
fail parse cleanup. The OS boundary is stubbed, not a hardware page-lifecycle test.
Developed with the assistance of AI. Upstream GPLv2 licensing applies.
