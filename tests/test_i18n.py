from src.core.i18n import MESSAGE_TEXT, STATUS_TEXT, UI_TEXT, ui_text


def test_translation_tables_have_matching_keys() -> None:
    for table in (UI_TEXT, STATUS_TEXT, MESSAGE_TEXT):
        assert set(table["pt_BR"]) == set(table["en_US"])


def test_yes_no_translations_are_language_specific() -> None:
    assert ui_text("yes", "pt_BR") == "Sim"
    assert ui_text("no", "pt_BR") == "Não"
    assert ui_text("yes", "en_US") == "Yes"
    assert ui_text("no", "en_US") == "No"


def test_folder_picker_and_splash_texts_are_translated() -> None:
    assert ui_text("select_folder_title", "pt_BR") == "Selecionar pasta"
    assert ui_text("select_folder_title", "en_US") == "Select folder"
    assert ui_text("splash_loading", "pt_BR") == "Carregando..."
    assert ui_text("splash_loading", "en_US") == "Loading..."
