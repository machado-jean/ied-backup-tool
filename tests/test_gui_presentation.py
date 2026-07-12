from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTableWidget

from src.config.config_manager import AppConfig, HistoryCleanupConfig, save_config
from src.core.backup_models import BackupPlan, BackupSummary
from src.gui.backup_confirmation import execution_confirmation_message, integrity_conflict_details
from src.gui.execution_summary_dialog import _summary_rows
from src.gui.history_cleanup_window import HistoryCleanupWindow
from src.gui.main_window import MainWindow
from src.gui.preview_table import populate_preview_table, source_files_text
from src.gui.summary_text import format_summary_text


def test_source_files_text_shows_first_file_and_extra_count(tmp_path: Path) -> None:
    first = tmp_path / "SE-AAA_COMENTARIO.dz5"
    second = tmp_path / "SE-AAA_COMENTARIO.rdb"

    assert source_files_text((first,)) == "SE-AAA_COMENTARIO.dz5"
    assert source_files_text((first, second)) == "SE-AAA_COMENTARIO.dz5 + 1"
    assert source_files_text(()) == "-"


def test_format_summary_text_uses_translated_labels() -> None:
    summary = BackupSummary(
        total=2,
        stored=1,
        replaced_current=0,
        archived_history=1,
        atu_duplicates=0,
        sha_conflicts=0,
        skipped_older=0,
        already_current=0,
    )

    text = format_summary_text(summary, "pt_BR")

    assert "Total analisado: 2" in text
    assert "Novos backups criados: 1" in text
    assert "Históricos arquivados: 1" in text


def test_execution_summary_rows_hide_zero_values() -> None:
    summary = BackupSummary(
        total=10,
        stored=0,
        replaced_current=1,
        archived_history=0,
        atu_duplicates=0,
        sha_conflicts=0,
        skipped_older=0,
        already_current=9,
    )

    rows = _summary_rows(summary, "pt_BR")

    assert rows == [
        ("Total analisado", 10),
        ("ATU atualizado", 1),
        ("Já estavam atuais", 9),
    ]


def test_populate_preview_table_writes_plan_columns(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    _ = app
    source = tmp_path / "SE-AAA_COMENTARIO.dz5"
    plan = BackupPlan(
        source_file=source,
        backup_name="DIGSI5-V10.00_SE-AAA_20260622-1350_COLABORADOR-EXEMPLO_DEV.zip",
        destination_path=tmp_path / "IED-ATU" / "backup.zip",
        status="stored",
        software="DIGSI5-V10.00",
        project="SE-AAA",
        timestamp_text="20260622-1350",
        collaborator="COLABORADOR-EXEMPLO",
        stage="DEV",
        project_type_key="digsi",
        project_type_label="DIGSI 5 (.dz5)",
        source_files=(source,),
    )
    table = QTableWidget()
    table.setColumnCount(6)

    populate_preview_table(table, plans=[plan], duplicate_plans=[], language="pt_BR")

    assert table.rowCount() == 1
    assert table.item(0, 0).text() == "Novo"
    assert table.item(0, 1).text() == "SE-AAA_COMENTARIO.dz5"
    assert table.item(0, 2).text() == "SE-AAA"


def test_confirmation_helpers_format_execution_and_conflicts(tmp_path: Path) -> None:
    source = tmp_path / "SE-AAA_COMENTARIO.dz5"
    plan = BackupPlan(
        source_file=source,
        backup_name="DIGSI5-V10.00_SE-AAA_20260622-1350_COLABORADOR-EXEMPLO_DEV.zip",
        destination_path=tmp_path / "IED-ATU" / "backup.zip",
        status="sha_conflict",
        software="DIGSI5-V10.00",
        project="SE-AAA",
        timestamp_text="20260622-1350",
        collaborator="COLABORADOR-EXEMPLO",
        stage="DEV",
        project_type_key="digsi5",
        project_type_label="DIGSI 5 (.dz5)",
        source_files=(source,),
    )
    summary = BackupSummary(
        total=1,
        stored=1,
        replaced_current=0,
        archived_history=0,
        atu_duplicates=0,
        sha_conflicts=0,
        skipped_older=0,
        already_current=0,
    )

    assert "SE-AAA_COMENTARIO.dz5 -> backup.zip" in integrity_conflict_details([plan])
    assert "Serão processados 1 backups." in execution_confirmation_message(
        summary,
        fix_duplicates=False,
        language="pt_BR",
    )


def test_history_cleanup_window_shows_candidates(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    _ = app
    his_path = tmp_path / "HIS"
    his_path.mkdir()
    (his_path / "DIGSI5-V10.00_SE-AAA_20260101-1000_COLABORADOR_DEV.zip").write_bytes(
        b"old"
    )
    (his_path / "DIGSI5-V10.00_SE-AAA_20260201-1000_COLABORADOR_DEV.zip").write_bytes(
        b"latest"
    )
    config = AppConfig(
        collaborator="COLABORADOR",
        atu_path=tmp_path / "ATU",
        his_path=his_path,
    )

    window = HistoryCleanupWindow(
        config_path=tmp_path / "config.json",
        config=config,
        language="pt_BR",
    )

    assert window.windowTitle() == "Limpeza HIS"
    assert window.table.rowCount() == 1
    assert window.table.item(0, 0).checkState() == Qt.CheckState.Unchecked
    assert window.table.item(0, 1).text().startswith("DIGSI5-V10.00_SE-AAA_20260101")


def test_history_cleanup_window_uses_checked_candidates(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    _ = app
    his_path = tmp_path / "HIS"
    his_path.mkdir()
    first = his_path / "DIGSI5-V10.00_SE-AAA_20260101-1000_COLABORADOR_DEV.zip"
    second = his_path / "DIGSI5-V10.00_SE-AAA_20260102-1000_COLABORADOR_DEV.zip"
    latest = his_path / "DIGSI5-V10.00_SE-AAA_20260201-1000_COLABORADOR_DEV.zip"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    latest.write_bytes(b"latest")
    config = AppConfig(
        collaborator="COLABORADOR",
        atu_path=tmp_path / "ATU",
        his_path=his_path,
    )
    window = HistoryCleanupWindow(
        config_path=tmp_path / "config.json",
        config=config,
        language="pt_BR",
    )

    assert window.table.rowCount() == 2
    assert window._selected_candidates() == []
    window.table.item(1, 0).setCheckState(Qt.CheckState.Checked)

    selected = window._selected_candidates()

    assert len(selected) == 1
    assert selected[0].path == second


def test_manual_history_cleanup_notice_does_not_delete_files(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    _ = app
    his_path = tmp_path / "HIS"
    atu_path = tmp_path / "ATU"
    his_path.mkdir()
    atu_path.mkdir()
    old_backup = his_path / "DIGSI5-V10.00_SE-AAA_20260101-1000_COLABORADOR_DEV.zip"
    latest_backup = his_path / "DIGSI5-V10.00_SE-AAA_20260201-1000_COLABORADOR_DEV.zip"
    old_backup.write_bytes(b"old")
    latest_backup.write_bytes(b"latest")
    save_config(
        tmp_path / "config.json",
        AppConfig(
            collaborator="COLABORADOR",
            atu_path=atu_path,
            his_path=his_path,
            history_cleanup=HistoryCleanupConfig(retention_days=30),
        ),
    )
    window = MainWindow(project_dir=tmp_path, auto_startup_dialogs=False)

    message = window._handle_history_cleanup_after_backup()

    assert "Limpeza HIS" in message
    assert old_backup.exists()
    assert latest_backup.exists()
