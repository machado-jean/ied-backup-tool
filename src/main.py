"""Command-line entry point for backup automation and dry runs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from src.config.config_manager import AppConfig, ConfigError, load_config
from src.core.backup_service import (
    BackupSummary,
    plan_all_backups,
    plan_latest_backup,
    process_all_backups,
    process_latest_backup,
    summarize_results,
)
from src.core.detector import Dz5DetectionError
from src.core.digsi import DigsiVersionError
from src.core.i18n import DEFAULT_LANGUAGE, message_label, status_label
from src.core.logger import get_logger
from src.core.naming import BackupStage
from src.core.project_types.base import ProjectVersionRequiredError
from src.core.project_types.registry import DEFAULT_PROJECT_TYPE, PROJECT_TYPES, get_project_type
from src.core.storage import StorageError
from src.core.zipper import BackupZipError


def parse_args() -> argparse.Namespace:
    """Parse CLI options while keeping config.json as the default source of paths."""

    parser = argparse.ArgumentParser(description="IED Backup Manager")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Pasta do projeto. Padrao: pasta atual.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.json"),
        help="Arquivo de configuracao.",
    )
    parser.add_argument(
        "--stage",
        default=BackupStage.DEV.value,
        choices=[stage.value for stage in BackupStage],
        help="Etapa do backup.",
    )
    parser.add_argument(
        "--process-all",
        action="store_true",
        help="Processa todos os arquivos suportados da pasta em ordem cronologica.",
    )
    parser.add_argument(
        "--project-type",
        default=DEFAULT_PROJECT_TYPE.key,
        choices=[project_type.key for project_type in PROJECT_TYPES],
        help="Tipo de projeto/IED a processar.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra a acao prevista sem criar ZIP nem mover arquivos.",
    )
    parser.add_argument(
        "--collaborator",
        help="Sobrescreve o colaborador do config.json.",
    )
    parser.add_argument(
        "--atu-path",
        type=Path,
        help="Sobrescreve a pasta ATU do config.json.",
    )
    parser.add_argument(
        "--his-path",
        type=Path,
        help="Sobrescreve a pasta HIS do config.json.",
    )
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        choices=["pt_BR", "en_US"],
        help="Idioma das mensagens.",
    )
    parser.add_argument(
        "--software-version",
        help="Versao manual quando o tipo de projeto nao conseguir detectar automaticamente.",
    )
    return parser.parse_args()


@dataclass(frozen=True)
class RuntimeConfig:
    """Resolved runtime configuration after applying CLI overrides."""

    collaborator: str
    atu_path: Path
    his_path: Path


def resolve_runtime_config(args: argparse.Namespace) -> RuntimeConfig:
    """Merge config.json with explicit CLI overrides."""

    config = load_optional_config(args.config)
    collaborator = args.collaborator or (config.collaborator if config else None)
    atu_path = args.atu_path or (config.atu_path if config else None)
    his_path = args.his_path or (config.his_path if config else None)

    missing = [
        name
        for name, value in [
            ("collaborator", collaborator),
            ("atu-path", atu_path),
            ("his-path", his_path),
        ]
        if value is None
    ]
    if missing:
        raise ConfigError(
            "Informe config.json ou os argumentos obrigatorios: "
            + ", ".join(f"--{name}" for name in missing)
        )

    return RuntimeConfig(
        collaborator=str(collaborator),
        atu_path=Path(atu_path),
        his_path=Path(his_path),
    )


def load_optional_config(path: Path) -> AppConfig | None:
    """Load config.json only when it exists."""

    if not path.exists():
        return None
    return load_config(path)


def main() -> int:
    """Execute the requested backup action and return a process exit code."""

    args = parse_args()
    logger = get_logger()

    try:
        runtime_config = resolve_runtime_config(args)
        stage = BackupStage(args.stage)
        project_type = get_project_type(args.project_type)

        if args.dry_run:
            plans = (
                plan_all_backups(
                    project_dir=args.project_dir,
                    atu_path=runtime_config.atu_path,
                    his_path=runtime_config.his_path,
                    collaborator=runtime_config.collaborator,
                    stage=stage,
                    project_type=project_type,
                    software_version_override=args.software_version,
                )
                if args.process_all
                else [
                    plan_latest_backup(
                        project_dir=args.project_dir,
                        atu_path=runtime_config.atu_path,
                        his_path=runtime_config.his_path,
                        collaborator=runtime_config.collaborator,
                        stage=stage,
                        project_type=project_type,
                        software_version_override=args.software_version,
                    )
                ]
            )
            for plan in plans:
                print(
                    f"{message_label('planned', args.language)}: "
                    f"{plan.source_file.name} -> {plan.destination_path.name} "
                    f"[{status_label(plan.status, args.language)}]"
                )
            print_summary(summarize_results(plans))
            return 0

        if args.process_all:
            results = process_all_backups(
                project_dir=args.project_dir,
                atu_path=runtime_config.atu_path,
                his_path=runtime_config.his_path,
                collaborator=runtime_config.collaborator,
                stage=stage,
                project_type=project_type,
                software_version_override=args.software_version,
            )
            for result in results:
                logger.info("Backup processado: %s -> %s", result.source_file, result.final_path)
                print(
                    f"{message_label('executed', args.language)}: "
                    f"{result.source_file.name} -> {result.final_path.name} "
                    f"[{status_label(result.status, args.language)}]"
                )
            print_summary(summarize_results(results))
            return 0

        result = process_latest_backup(
            project_dir=args.project_dir,
            atu_path=runtime_config.atu_path,
            his_path=runtime_config.his_path,
            collaborator=runtime_config.collaborator,
            stage=stage,
            project_type=project_type,
            software_version_override=args.software_version,
        )

    except (
        BackupZipError,
        ConfigError,
        Dz5DetectionError,
        DigsiVersionError,
        ProjectVersionRequiredError,
        StorageError,
        ValueError,
    ) as exc:
        logger.exception("Falha ao gerar backup: %s", exc)
        print(f"Erro: {exc}")
        return 1

    logger.info("Backup gerado com sucesso: %s", result.final_path)
    print(f"Backup gerado: {result.final_path}")
    return 0


def print_summary(summary: BackupSummary) -> None:
    """Print a compact CLI summary."""

    print(
        "Resumo: "
        f"total={summary.total}, "
        f"novos={summary.stored}, "
        f"substituidos={summary.replaced_current}, "
        f"historicos={summary.archived_history}, "
        f"correcoes_atu={summary.atu_duplicates}, "
        f"ignorados_antigos={summary.skipped_older}, "
        f"ja_atuais={summary.already_current}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
