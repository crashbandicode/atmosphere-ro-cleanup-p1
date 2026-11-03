# RO failed-load cleanup patch 1

2026-11-03. Based on Atmosphere 1.12.1,
`6b0c077b4c608a3a2ee712b8dc35fee87ceb62e8`.

After successfully mapping an NRO, register the existing failure-unmap guard
before calling the fallible parser. Parser errors, including authorization
failure, now release the NRO/BSS code mappings before returning the original
error. Successful loads retain their mapping. Validation remains enforced.
The fix does not determine why a particular NRO was rejected and does not
address the separate render-pointer corruption under investigation.

The System Settings firmware display includes `AMS 1.12.1p1` followed by the
existing `S` or `E` mode indicator. Numeric Atmosphere API version fields
remain 1.12.1. The display has a 24-byte limit; this suffix fits with an
eight-character HOS version at the current Atmosphere version.

Run `python3 -I tests/ro_cleanup_p1/run.py` from the source root. It compiles
the actual production load function with its real result/guard macros and
injects failures at its context/OS boundaries. The patched function passes
64 boundary/format cases, while the official 1.12.1 function fails the parser
cleanup case. Cases cover validation, no free slot, initial map failure,
parser and permission failures, successful metadata on both sides of the
23.0.0 split, zero/nonzero BSS, compressed/uncompressed paths, cleanup-error
propagation, both eMMC indicators and display length. The injected boundary
is not a hardware page-lifecycle test.

Cross-build, artifact identity, installation/rollback and console observations
are recorded in the task's external handoff and receipts. No repaired console
boot is implied by these host checks. This patch was developed with the
assistance of AI. Upstream GPLv2 licensing applies.
