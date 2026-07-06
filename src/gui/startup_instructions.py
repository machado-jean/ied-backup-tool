"""Startup usage instructions dialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from src.core.i18n import DEFAULT_LANGUAGE
from src.gui.language_button import configure_language_button
from src.gui.resources import language_flag_path


class StartupInstructionsDialog(QDialog):
    """Instruction dialog shown when the application starts."""

    def __init__(self, *, language: str = DEFAULT_LANGUAGE, parent=None) -> None:
        super().__init__(parent)
        self.language = language
        self.do_not_show_again = False
        self.setMinimumWidth(700)

        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        self.language_button = QPushButton()
        configure_language_button(self.language_button)
        self.language_button.clicked.connect(self.toggle_language)
        header.addWidget(self.title_label, 1)
        header.addWidget(self.language_button)
        layout.addLayout(header)

        self.body_label = QLabel()
        self.body_label.setTextFormat(Qt.TextFormat.RichText)
        self.body_label.setWordWrap(True)
        self.body_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.body_label)

        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self.accept)
        layout.addWidget(self.buttons)
        self.retranslate()

    def toggle_language(self) -> None:
        """Switch the instruction dialog language without closing it."""

        self.language = "en_US" if self.language == "pt_BR" else "pt_BR"
        self.retranslate()

    def retranslate(self) -> None:
        """Apply the current language to every instruction dialog label."""

        texts = self._texts(self.language)
        self.setWindowTitle(texts["title"])
        self.title_label.setText(f"<h2>{texts['title']}</h2>")
        self.body_label.setText(texts["body"])
        self.checkbox.setText(texts["do_not_show_again"])
        self.language_button.setIcon(QIcon(str(language_flag_path(self.language))))
        self.language_button.setToolTip(texts["language_tooltip"])

    def accept(self) -> None:
        """Store the opt-out state before closing the dialog."""

        self.do_not_show_again = self.checkbox.isChecked()
        super().accept()

    @staticmethod
    def _texts(language: str) -> dict[str, str]:
        """Return translated instruction dialog text."""

        if language == "en_US":
            return {
                "title": "Usage Instructions",
                "do_not_show_again": "Do not show again",
                "language_tooltip": "Language",
                "body": """
                <p>This executable must stay inside the folder that contains the
                working files for the substation, application, bay, or equipment
                that will be processed.</p>

                <p><b>Recommended structure:</b></p>
                <pre>Local folder/
└─ SE, ETD, bay, or equipment folder/
   ├─ IED Backup Manager.exe
   ├─ config.json
   ├─ SE-XXX_GENERIC-COMMENT_20260622_1350.dz5
   ├─ ETD-YYY_GENERIC-COMMENT_20260612_0350.dz5
   ├─ ETD-YYY_OTHER-COMMENT.rdb
   └─ other working files</pre>

                <p><b>File naming rules:</b></p>
                <ul>
                  <li>The SE, ETD, bay, or equipment name must come before the
                  first underscore <code>"_"</code>.</li>
                  <li>Use hyphen <code>"-"</code> to separate text inside the SE,
                  ETD, bay, or equipment name.</li>
                  <li>All text after the first underscore <code>"_"</code> is treated
                  as a user comment and will not be used to identify the backup.</li>
                  <li>The backup will be grouped by the text before the first
                  underscore <code>"_"</code>.</li>
                </ul>

                <p><b>Example 1 - Siemens backup</b></p>
                <p>Input file:</p>
                <pre>SE-XXX_GENERIC-COMMENT_20260622_1350.dz5</pre>
                <p>Output:</p>
                <pre>DIGSIn-Vmmm_SE-XXX_YYYYMMDD-HHMM_COLLABORATOR_STAGE.zip</pre>
                <p><code>DIGSIn</code> represents the DIGSI family, for example
                <code>DIGSI5</code>, and <code>Vmmm</code> represents the detected
                version, for example <code>V10.00</code>.</p>

                <p><b>Example 2 - Multiple IEDs from the same SE</b></p>
                <p>Input files:</p>
                <pre>ETD-YYY_GENERIC-COMMENT_20260612_0350.dz5
ETD-YYY_OTHER-COMMENT.rdb</pre>
                <p>Output:</p>
                <pre>IED-PACK_ETD-YYY_YYYYMMDD-HHMM_COLLABORATOR_STAGE.zip</pre>
                <p>The ZIP will include <code>IEDS-BACKUP-INFO.txt</code> with
                versions and included file details.</p>

                <p>Before generating backups, check the <b>Project</b> column in the
                batch preview.</p>
                """,
            }

        return {
            "title": "Instruções de uso",
            "do_not_show_again": "Não exibir novamente",
            "language_tooltip": "Idioma",
            "body": """
            <p>Este executável deve ficar dentro da pasta que contém os arquivos
            de trabalho da subestação, aplicação ou vãos/equipamentos que serão
            processados.</p>

            <p><b>Estrutura recomendada:</b></p>
            <pre>Pasta local/
└─ Pasta da SE, ETD, vão ou equipamento/
   ├─ IED Backup Manager.exe
   ├─ config.json
   ├─ SE-XXX_COMENTARIO-GENERICO_20260622_1350.dz5
   ├─ ETD-YYY_COMENTARIO-GENERICO_20260612_0350.dz5
   ├─ ETD-YYY_OUTRO-COMENTARIO.rdb
   └─ outros arquivos de trabalho</pre>

            <p><b>Regras para nome dos arquivos:</b></p>
            <ul>
              <li>O nome da SE, ETD, vão ou equipamento deve vir antes do primeiro
              sublinhado <code>"_"</code>.</li>
              <li>Use hífen <code>"-"</code> para separar textos dentro do nome da SE,
              ETD, vão ou equipamento.</li>
              <li>Todo texto depois do primeiro sublinhado <code>"_"</code> é tratado
              como comentário do usuário e não será usado para identificar o backup.</li>
              <li>O backup será agrupado pelo trecho antes do primeiro sublinhado
              <code>"_"</code>.</li>
            </ul>

            <p><b>Exemplo 1 - Backup Siemens</b></p>
            <p>Arquivo de entrada:</p>
            <pre>SE-XXX_COMENTARIO-GENERICO_20260622_1350.dz5</pre>
            <p>Saída:</p>
            <pre>DIGSIn-Vmmm_SE-XXX_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip</pre>
            <p>Onde <code>DIGSIn</code> representa a família do DIGSI, por exemplo
            <code>DIGSI5</code>, e <code>Vmmm</code> representa a versão detectada,
            por exemplo <code>V10.00</code>.</p>

            <p><b>Exemplo 2 - Múltiplos IEDs da mesma SE</b></p>
            <p>Arquivos de entrada:</p>
            <pre>ETD-YYY_COMENTARIO-GENERICO_20260612_0350.dz5
ETD-YYY_OUTRO-COMENTARIO.rdb</pre>
            <p>Saída:</p>
            <pre>IED-PACK_ETD-YYY_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip</pre>
            <p>Dentro do ZIP haverá o arquivo <code>IEDS-BACKUP-INFO.txt</code> com
            versões e detalhes dos arquivos incluídos.</p>

            <p>Antes de gerar backups, confira a coluna <b>Projeto</b> na prévia do lote.</p>
            """,
        }
