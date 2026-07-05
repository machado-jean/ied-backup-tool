"""Small translation table for GUI, CLI, and status labels."""

from __future__ import annotations

DEFAULT_LANGUAGE = "pt_BR"

STATUS_TEXT = {
    "pt_BR": {
        "stored": "Novo",
        "replaced_current": "Atualiza ATU",
        "archived_history": "Arquivar HIS",
        "atu_duplicate": "Corrigir ATU",
        "sha_conflict": "Conflito SHA",
        "skipped_older": "Ignorado",
        "already_current": "Já atual",
    },
    "en_US": {
        "stored": "New",
        "replaced_current": "Update ATU",
        "archived_history": "Archive HIS",
        "atu_duplicate": "Fix ATU",
        "sha_conflict": "SHA conflict",
        "skipped_older": "Skipped",
        "already_current": "Already current",
    },
}

MESSAGE_TEXT = {
    "pt_BR": {
        "planned": "PREVISTO",
        "problematic": "PROBLEMÁTICO",
        "executed": "EXECUTADO",
    },
    "en_US": {
        "planned": "PLANNED",
        "problematic": "PROBLEMATIC",
        "executed": "EXECUTED",
    },
}

UI_TEXT = {
    "pt_BR": {
        "action": "Ação",
        "already_current": "Já atuais",
        "archive_count": "Históricos",
        "atu_corrections": "Correções ATU",
        "sha_conflicts": "Conflitos SHA",
        "atu_folder": "Pasta ATU",
        "backup_failed": "Falha ao gerar backup",
        "backup_canceled_message": (
            "A execução foi cancelada antes de iniciar o próximo arquivo. "
            "Itens concluídos: {completed}."
        ),
        "backup_canceled_title": "Backup cancelado",
        "backup_processed_title": "Backups processados",
        "cancel": "Cancelar",
        "collaborator": "Colaborador",
        "completed_at": "Concluído em",
        "confirm_execution": "Confirmar execução",
        "continue_question": "Continuar?",
        "current_folder": "Pasta atual",
        "destination": "Destino",
        "duplicate_files_found": "Foram encontrados arquivos antigos duplicados em ATU:",
        "duplicates_question": "Deseja mover esses arquivos problemáticos para HIS?",
        "duplicates_title": "Duplicidades em ATU",
        "dz5_type": "DIGSI 5 (.dz5)",
        "error_prefix": "ERRO",
        "execution": "Execução",
        "files_to_process": "Serão processados {count} backups.",
        "file": "Arquivo",
        "fill_fields": "Preencha",
        "generate_backups": "Gerar backups",
        "help": "Ajuda",
        "help_open_failed": "Não foi possível abrir a ajuda online: {url}",
        "ignored": "Ignorados",
        "integrity_conflicts_found": (
            "Foram encontrados backups com a mesma identidade técnica, mas SHA256 "
            "diferente. A execução foi bloqueada para evitar sobrescrever ou arquivar "
            "um backup potencialmente divergente.\n\n{details}"
        ),
        "integrity_conflicts_title": "Conflitos de integridade",
        "his_folder": "Pasta HIS",
        "language_tooltip": "Idioma",
        "license": "Licença",
        "license_message": (
            "IED Backup Manager<br>"
            "Copyright © 2026 Jean Carlos Machado.<br><br>"
            "Disponibilizado para uso gratuito e não comercial, conforme a licença "
            "do projeto.<br><br>"
            'Repositório: <a href="{url}">{url}</a>'
        ),
        "license_tooltip": "Licença e autoria",
        "mode": "Modo",
        "new": "Novos",
        "no_digsi_found": "Nenhum arquivo DIGSI 5 encontrado nesta pasta.",
        "no_new_backups": "Não há backups novos para processar.",
        "no_project_files_found": "Nenhum arquivo de projeto suportado encontrado nesta pasta.",
        "nothing_to_execute": "Nada a executar",
        "open_atu": "Abrir ATU",
        "open_his": "Abrir HIS",
        "preview": "Prévia do lote",
        "preview_note": "PRÉVIA: nenhum arquivo foi criado ou movido ainda.",
        "progress_finished": "Backups concluídos.",
        "progress_cancel_pending": (
            "Cancelamento solicitado. O arquivo atual será finalizado antes de parar."
        ),
        "progress_cancel_requested": (
            "Cancelamento solicitado.\nFinalizando a operação atual antes de parar..."
        ),
        "progress_fixing_atu": "Corrigindo duplicidades em ATU...",
        "progress_fixing_atu_detail": "Corrigindo duplicidades em ATU...\n{phase}: {percent}%",
        "progress_phase_archive_current": "Arquivando backup anterior",
        "progress_phase_copy_current": "Copiando backup final",
        "progress_phase_preparing": "Preparando",
        "progress_phase_zip": "Compactando arquivos",
        "progress_processing_file": (
            "Processando arquivo {index}/{total}\n{file}\n{phase}: {percent}%"
        ),
        "progress_starting": "Preparando processamento...",
        "progress_title": "Gerando backups",
        "process_from_current": "Processar apenas a partir do backup atual",
        "project": "Projeto",
        "refresh": "Atualizar",
        "replaced_current": "Substituições em ATU",
        "required_config": "Configure colaborador, ATU e HIS antes de gerar backup.",
        "required_fields": "Campos obrigatórios",
        "required_stage": "Selecione a etapa antes de gerar backup.",
        "required_type": "Selecione ao menos um tipo de arquivo suportado.",
        "required_software_version": (
            "Não foi possível detectar a versão de {file}. Informe a versão do software."
        ),
        "required_manual_software_version": "Informe a versão do software para {type}.",
        "save": "Salvar",
        "select": "Selecionar",
        "settings": "Configurações",
        "settings_invalid": "Configuração inválida",
        "settings_pending": "Configuração pendente",
        "settings_required": "Salve as configurações antes de gerar backup.",
        "storage_folder_missing_message": (
            "{label} não existe:\n\n{path}\n\nDeseja criá-la agora?"
        ),
        "storage_folder_missing_title": "Pasta não encontrada",
        "storage_folder_not_directory": "{label} aponta para um arquivo, não uma pasta: {path}",
        "storage_folder_open_failed": "Não foi possível abrir a pasta: {path}",
        "storage_paths_create_failed": "Não foi possível criar ou validar as pastas: {error}",
        "storage_paths_invalid_title": "Pastas ATU/HIS inválidas",
        "storage_paths_missing_message": (
            "As seguintes pastas não existem:\n\n{paths}\n\nDeseja criá-las agora?"
        ),
        "storage_paths_missing_title": "Criar pastas ATU/HIS",
        "storage_paths_nested_message": (
            "{detail}\n\nEssa configuração pode confundir o versionamento. Deseja continuar?"
        ),
        "storage_paths_nested_title": "Atenção aos caminhos ATU/HIS",
        "storage_paths_synced_message": (
            "As seguintes pastas parecem estar em diretórios sincronizados:\n\n"
            "{details}\n\n"
            "Se houver arquivos grandes, bloqueados ou sincronização pendente, "
            "o backup pode demorar, falhar ou o aplicativo pode parecer travado."
        ),
        "storage_paths_synced_title": "Pasta sincronizada detectada",
        "stage": "Etapa",
        "stage_description": "Descrição",
        "stage_description_option": "Descrição livre",
        "stage_description_placeholder": "Opcional; deixe vazio quando não se enquadrar",
        "summary": "Resumo",
        "summary_archived_line": "Históricos arquivados: {count}",
        "summary_atu_line": "Correções em ATU: {count}",
        "summary_current_line": "Já estavam atuais: {count}",
        "summary_sha_conflict_line": "Conflitos SHA: {count}",
        "summary_replaced_line": "ATU atualizado: {count}",
        "summary_skipped_line": "Ignorados por serem antigos: {count}",
        "summary_stored_line": "Novos backups criados: {count}",
        "summary_total_line": "Total analisado: {total}",
        "software_version": "Versão do software",
        "ingeteam_software_version": "v",
        "software_version_placeholder": "Ex.: 5.5.4",
        "timestamp": "Data/Hora",
        "total": "Total",
        "type": "Tipos",
        "update_available": "Nova versão disponível",
        "update_available_tooltip": "Clique para abrir a versão {version} no GitHub.",
        "version": "Versão",
    },
    "en_US": {
        "action": "Action",
        "already_current": "Already current",
        "archive_count": "History",
        "atu_corrections": "ATU fixes",
        "sha_conflicts": "SHA conflicts",
        "atu_folder": "ATU folder",
        "backup_failed": "Backup failed",
        "backup_canceled_message": (
            "Execution was canceled before starting the next file. "
            "Completed items: {completed}."
        ),
        "backup_canceled_title": "Backup canceled",
        "backup_processed_title": "Backups processed",
        "cancel": "Cancel",
        "collaborator": "Collaborator",
        "completed_at": "Completed at",
        "confirm_execution": "Confirm execution",
        "continue_question": "Continue?",
        "current_folder": "Current folder",
        "destination": "Destination",
        "duplicate_files_found": "Older duplicate files were found in ATU:",
        "duplicates_question": "Do you want to move these problematic files to HIS?",
        "duplicates_title": "ATU duplicates",
        "dz5_type": "DIGSI 5 (.dz5)",
        "error_prefix": "ERROR",
        "execution": "Execution",
        "files_to_process": "{count} backups will be processed.",
        "file": "File",
        "fill_fields": "Fill in",
        "generate_backups": "Generate backups",
        "help": "Help",
        "help_open_failed": "Could not open the online help: {url}",
        "ignored": "Ignored",
        "integrity_conflicts_found": (
            "Backups with the same technical identity but different SHA256 values "
            "were found. Execution was blocked to avoid overwriting or archiving a "
            "potentially divergent backup.\n\n{details}"
        ),
        "integrity_conflicts_title": "Integrity conflicts",
        "his_folder": "HIS folder",
        "language_tooltip": "Language",
        "license": "License",
        "license_message": (
            "IED Backup Manager<br>"
            "Copyright © 2026 Jean Carlos Machado.<br><br>"
            "Available for free non-commercial use under the project license."
            "<br><br>"
            'Repository: <a href="{url}">{url}</a>'
        ),
        "license_tooltip": "License and authorship",
        "mode": "Mode",
        "new": "New",
        "no_digsi_found": "No DIGSI 5 file found in this folder.",
        "no_new_backups": "There are no new backups to process.",
        "no_project_files_found": "No supported project file found in this folder.",
        "nothing_to_execute": "Nothing to execute",
        "open_atu": "Open ATU",
        "open_his": "Open HIS",
        "preview": "Batch preview",
        "preview_note": "PREVIEW: no file has been created or moved yet.",
        "progress_finished": "Backups completed.",
        "progress_cancel_pending": (
            "Cancellation requested. The current file will finish before stopping."
        ),
        "progress_cancel_requested": (
            "Cancellation requested.\nFinishing the current operation before stopping..."
        ),
        "progress_fixing_atu": "Fixing ATU duplicates...",
        "progress_fixing_atu_detail": "Fixing ATU duplicates...\n{phase}: {percent}%",
        "progress_phase_archive_current": "Archiving previous backup",
        "progress_phase_copy_current": "Copying final backup",
        "progress_phase_preparing": "Preparing",
        "progress_phase_zip": "Compressing files",
        "progress_processing_file": (
            "Processing file {index}/{total}\n{file}\n{phase}: {percent}%"
        ),
        "progress_starting": "Preparing processing...",
        "progress_title": "Generating backups",
        "process_from_current": "Process only from current backup",
        "project": "Project",
        "refresh": "Refresh",
        "replaced_current": "ATU updates",
        "required_config": "Configure collaborator, ATU and HIS before generating backup.",
        "required_fields": "Required fields",
        "required_stage": "Select the stage before generating backup.",
        "required_type": "Select at least one supported file type.",
        "required_software_version": (
            "Could not detect the version of {file}. Enter the software version."
        ),
        "required_manual_software_version": "Enter the software version for {type}.",
        "save": "Save",
        "select": "Select",
        "settings": "Settings",
        "settings_invalid": "Invalid settings",
        "settings_pending": "Pending settings",
        "settings_required": "Save settings before generating backup.",
        "storage_folder_missing_message": (
            "{label} does not exist:\n\n{path}\n\nDo you want to create it now?"
        ),
        "storage_folder_missing_title": "Folder not found",
        "storage_folder_not_directory": "{label} points to a file, not a folder: {path}",
        "storage_folder_open_failed": "Could not open the folder: {path}",
        "storage_paths_create_failed": "Could not create or validate the folders: {error}",
        "storage_paths_invalid_title": "Invalid ATU/HIS folders",
        "storage_paths_missing_message": (
            "The following folders do not exist:\n\n{paths}\n\nDo you want to create them now?"
        ),
        "storage_paths_missing_title": "Create ATU/HIS folders",
        "storage_paths_nested_message": (
            "{detail}\n\nThis configuration may confuse versioning. Do you want to continue?"
        ),
        "storage_paths_nested_title": "Check ATU/HIS paths",
        "storage_paths_synced_message": (
            "The following folders appear to be inside synced directories:\n\n"
            "{details}\n\n"
            "If files are large, locked, or waiting for sync, the backup may take longer, "
            "fail, or the application may appear frozen."
        ),
        "storage_paths_synced_title": "Synced folder detected",
        "stage": "Stage",
        "stage_description": "Description",
        "stage_description_option": "Free description",
        "stage_description_placeholder": "Optional; leave empty when it does not apply",
        "summary": "Summary",
        "summary_archived_line": "History archived: {count}",
        "summary_atu_line": "ATU fixes: {count}",
        "summary_current_line": "Already current: {count}",
        "summary_sha_conflict_line": "SHA conflicts: {count}",
        "summary_replaced_line": "ATU updated: {count}",
        "summary_skipped_line": "Skipped because older: {count}",
        "summary_stored_line": "New backups created: {count}",
        "summary_total_line": "Total analyzed: {total}",
        "software_version": "Software version",
        "ingeteam_software_version": "v",
        "software_version_placeholder": "Example: 5.5.4",
        "timestamp": "Date/Time",
        "total": "Total",
        "type": "Types",
        "update_available": "New version available",
        "update_available_tooltip": "Click to open version {version} on GitHub.",
        "version": "Version",
    },
}


def status_label(status: str, language: str = DEFAULT_LANGUAGE) -> str:
    """Return a translated label for an internal status code."""

    return STATUS_TEXT.get(language, STATUS_TEXT[DEFAULT_LANGUAGE]).get(status, status)


def message_label(key: str, language: str = DEFAULT_LANGUAGE) -> str:
    """Return a translated log/message prefix."""

    return MESSAGE_TEXT.get(language, MESSAGE_TEXT[DEFAULT_LANGUAGE]).get(key, key)


def ui_text(key: str, language: str = DEFAULT_LANGUAGE) -> str:
    """Return translated UI text, falling back to the key when unknown."""

    return UI_TEXT.get(language, UI_TEXT[DEFAULT_LANGUAGE]).get(key, key)
