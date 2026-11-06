# G7 original local history and publication mapping

The completed G7 research package is published in [Draft PR #169](https://github.com/zuizui0223/frogcs/pull/169). The shell could not authenticate to GitHub, so the connected GitHub app published an ordered copy of the six local commits. The app creates new commit IDs and publication timestamps. Every copied tree and all 58 uploaded blob hashes match the originals exactly.

The original commits, including their authors, timestamps, parents and messages, are preserved byte for byte in [g7_local_freeze_history_20261106.bundle](g7_local_freeze_history_20261106.bundle). [G7_PUBLICATION_COMMIT_MAP_2026-11-06.json](G7_PUBLICATION_COMMIT_MAP_2026-11-06.json) records the local-to-publication mapping and verification. This preserves the original local freeze order; it is not an independently timestamped public preregistration.

| Stage | Original local commit | Publication commit |
|---|---|---|
| Protocol freeze | `21fda6b3f8155a0eb8583fd0f70ef43a36874c0e` | `706063c6ecfd76513ee73b5979736149f4045acf` |
| Implementation freeze | `be77b4c4321eeaa2e29c680cac8ed201fa9dc673` | `5ec0d7b703ca30fc85ff61944f20c906ee16ed68` |
| Results and manuscript | `922eb96f3c1eb1c146cd2c78ec0b54efc8a08133` | `ef2392931537770c10d5a197f2fb071704b35911` |

## Restore the original commits

The bundle is incremental and requires commit `4e9884d8d18702428fa7ef87d3dba3a8722288f6`. In a clone of this repository, fetch that prerequisite if needed, then restore the archive into a separate branch:

```bash
git fetch origin 4e9884d8d18702428fa7ef87d3dba3a8722288f6
git bundle verify research/provenance/g7_local_freeze_history_20261106.bundle
git fetch research/provenance/g7_local_freeze_history_20261106.bundle refs/heads/research/g7-developmental-trait-bridge-20261106:refs/heads/archive/g7-original-freeze-20261106
```

The restored head is `fed98fae5746ee29d5f9287d1264809c7d5284fd`; its tree is `57dc8eda6555530f56adaa1a1e57de787f5fb9f1`. The bundle SHA256 is `793d81f9e9697fc6d6b137156666fb45ca9083f3f9d3318081bcc7a19bb81cf1` (1,608,818 bytes).

Independent restoration in an isolated bare repository verified all six original raw commit objects, the protocol hash, and the final tree. Bundle verification and strict Git object checks passed. The source checkout had a shallow boundary at `e6a1a7b1`; its existing prerequisite boundary was retained for that isolated check. A normal full clone can obtain the prerequisite ancestry from GitHub.

The subsequent publication-record commit adds this archive, mapping and current PR status. Those additions are separate from the six exact tree comparisons and do not change the scientific code, protocol, result tables, figures or manuscript.
