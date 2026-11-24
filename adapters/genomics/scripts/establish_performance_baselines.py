# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Establish native performance baselines for genomics microcosting."""

from dapane_genomics.legacy_performance import (
    compare_baselines as compare_baselines,
)
from dapane_genomics.legacy_performance import (
    establish_performance_baselines as establish_performance_baselines,
)
from dapane_genomics.legacy_performance import (
    load_baselines as load_baselines,
)
from dapane_genomics.legacy_performance import (
    main,
)
from dapane_genomics.legacy_performance import (
    print_baseline_summary as print_baseline_summary,
)
from dapane_genomics.legacy_performance import (
    save_baselines as save_baselines,
)

if __name__ == "__main__":
    raise SystemExit(main())
