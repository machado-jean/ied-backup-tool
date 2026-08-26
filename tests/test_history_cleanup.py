from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.core.history_cleanup import execute_history_cleanup, plan_history_cleanup


def test_plan_history_cleanup_keeps_latest_backup_per_stage(tmp_path: Path) -> None:
    his = tmp_path / "HIS"
    his.mkdir()
    old_dev = _backup(his, "DIGSI5-V10.00_SE-AAA_2026-01-01_10h00_COLABORADOR_DEV.zip")
    latest_dev = _backup(his, "DIGSI5-V10.00_SE-AAA_2026-02-01_10h00_COLABORADOR_DEV.zip")
    latest_taf = _backup(his, "DIGSI5-V10.00_SE-AAA_2026-01-05_10h00_COLABORADOR_TAF.zip")
    recent_dev = _backup(his, "DIGSI5-V10.00_SE-BBB_2026-06-20_10h00_COLABORADOR_DEV.zip")

    plan = plan_history_cleanup(
        his,
        retention_days=30,
        now=datetime(2026, 7, 11, 12, 0),
    )

    candidate_paths = {candidate.path for candidate in plan.candidates}
    assert candidate_paths == {old_dev}
    assert latest_dev not in candidate_paths
    assert latest_taf not in candidate_paths
    assert recent_dev not in candidate_paths
    assert plan.total_his_files == 4
    assert plan.candidate_size_bytes == old_dev.stat().st_size


def test_execute_history_cleanup_deletes_selected_candidates(tmp_path: Path) -> None:
    his = tmp_path / "HIS"
    his.mkdir()
    old_dev = _backup(his, "DIGSI5-V10.00_SE-AAA_2026-01-01_10h00_COLABORADOR_DEV.zip")
    _backup(his, "DIGSI5-V10.00_SE-AAA_2026-02-01_10h00_COLABORADOR_DEV.zip")
    plan = plan_history_cleanup(
        his,
        retention_days=30,
        now=datetime(2026, 7, 11, 12, 0),
    )

    removed = execute_history_cleanup(plan.candidates)

    assert removed == [old_dev]
    assert not old_dev.exists()


def test_plan_history_cleanup_zero_days_disables_candidates_but_keeps_totals(
    tmp_path: Path,
) -> None:
    his = tmp_path / "HIS"
    his.mkdir()
    first = _backup(his, "DIGSI5-V10.00_SE-AAA_2026-01-01_10h00_COLABORADOR_DEV.zip")
    second = _backup(his, "DIGSI5-V10.00_SE-AAA_2026-02-01_10h00_COLABORADOR_DEV.zip")

    plan = plan_history_cleanup(
        his,
        retention_days=0,
        now=datetime(2026, 7, 11, 12, 0),
    )

    assert plan.candidates == []
    assert plan.total_his_files == 2
    assert plan.total_his_size_bytes == first.stat().st_size + second.stat().st_size
    assert plan.candidate_size_bytes == 0


def _backup(folder: Path, name: str) -> Path:
    path = folder / name
    path.write_bytes(b"backup")
    return path
