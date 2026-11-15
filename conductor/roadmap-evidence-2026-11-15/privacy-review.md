# Coordination evidence privacy review

This is a value-free review of the coordination PR's evidence packaging. It does
not approve a scanner exception or change any security gate. The seven lane PRs
retain their separate, passing privacy checks on their recorded heads.

## Observed hosted result

Coordination source `b26ef961ab696057d088d6f5be34da441be09daf` failed
[privacy job 132731740695](https://github.com/edithatogo/dapane/actions/runs/43687768627/job/132731740695).
The action remains pinned to repository-standards
`985503bc8eae58e7d6ef36a6e5427d0077e0193c`.

| Control | Actual observation | Disposition |
| --- | --- | --- |
| Gitleaks 8.30.1 | 16 blocking `generic-api-key` findings in the retained qualification receipts | All 16 values were independently verified as SHA-256 digests of tracked files at the receipts' exact source commits. They are locally classified as digest false positives; the blocking scanner outcome remains in force. |
| Presidio, repository profile | Zero blocking findings; seven advisory phone-number matches | Source-context inspection identifies six elapsed-duration numbers and one command timestamp. These are execution metadata. No contact or patient-data claim is inferred from the detector result. |
| Presidio coverage | 44 of 46 selected files scanned; two compressed static result files reported as binary coverage gaps | This follow-up stores their original JSON as readable UTF-8. Incomplete coverage alone did not cause this pinned action's nonzero exit; Gitleaks did. |

Fourteen digest findings refer to the unchanged privacy-workflow file. Two refer
to the static lane's duplicate-JSON-key synthetic fixture. The integrator read
the named immutable Git blobs and recomputed every SHA-256; all sixteen match.
No credential value, raw secret-scanner report or matched source snippet is
reproduced in this review.

## Evidence format correction

The two `static-results.json` files are the exact uncompressed bytes from the
verified hosted artifacts: 1,360,595 and 1,360,573 bytes. Both are valid UTF-8,
contain no NUL and fall below the pinned scanner's 10 MiB per-blob limit. Their
SHA-256 values match both the original hosted receipts and the retained
compression records. No result, source identity, numerical value, failed case,
slower observation or unmeasured limitation has been edited.

The original compressed packaging remains in the history at
`b26ef961ab696057d088d6f5be34da441be09daf`. The current evidence index links the
plain JSON. The historical compression records retain the original/compressed
byte counts and hashes; they describe the earlier packaging, not an additional
current binary file. All fourteen qualification receipts remain byte-for-byte
unchanged.

## Central review request; gate remains blocked

The [pinned privacy standard](https://github.com/edithatogo/repository-standards/blob/985503bc8eae58e7d6ef36a6e5427d0077e0193c/docs/privacy-secrets-standard.md)
uses the complete submitted commit range for Gitleaks. It intentionally ignores
consumer suppression files, environment overrides and inline allow comments.
Changing the current receipt formatting cannot erase the already-scanned
historical findings, and rewriting this evidence history is not authorised.

Fresh central main `bef6721531ae014e583ca420b2e27e66475fe5d5` already supplies
an [exact reviewed-finding registry](https://github.com/edithatogo/repository-standards/blob/bef6721531ae014e583ca420b2e27e66475fe5d5/privacy/reviewed-findings.json)
and a [documented review process](https://github.com/edithatogo/repository-standards/blob/bef6721531ae014e583ca420b2e27e66475fe5d5/privacy/reviewed-findings.md).
Its ten approved coordinates concern eight Tobac and two Genomics findings;
none covers this Dapane evidence. Merged central
[PR #132](https://github.com/edithatogo/repository-standards/pull/132) qualified
specific SHA-256 admissions and nearby real-positive/mismatch controls. It did
not exempt arbitrary hashes, and the underlying Gitleaks configuration remains
unchanged. Updating Dapane's pin alone would not clear these historical findings.

The existing central owner can resolve this through sixteen exact registry
entries, without a new scanner implementation or generic hash allowlist. Each
entry needs the actual scanner commit, canonical path, rule, starting line and
SHA-256 of the actual matched UTF-8 value, plus immutable nonsecret proof. Raw
values/reports must stay private. This receipt does not claim those exact
admissions have been authored, reviewed or accepted centrally.

The requested acceptance boundary is:

1. Admit only the complete, reviewed historical finding identities in the
   trusted central registry, supported by recomputed immutable file-digest
   evidence. No path, rule or generic hash pattern becomes exempt.
2. Continue to detect real API credentials, including hexadecimal credentials,
   in nearby context and in the same submitted history.
3. Preserve fail-closed handling for malformed provenance, missing source,
   scanner errors, incomplete history and conflicting evidence.
4. Run the existing central policy/privacy suites, real Gitleaks positive and
   mismatch controls, required review/checks and a canary on this exact historical
   range while preserving the original failed scan. Only then explicitly review
   a Dapane consumer-pin update. No new revision is selected in this record.

No central repository is changed by this follow-up. No consumer allowlist,
scanner bypass, reduced scope, force-push or history rewrite is introduced.
Until a reviewed central resolution is available, **coordination PR #20's
privacy gate remains blocked**, separately from the queued offline-security
jobs and the five lanes' owner quality findings. Publication and merging remain
disabled under the continuing release boundary.
