from __future__ import annotations

import json
from pathlib import Path

import pytest

from hoi4presence.countries import getCountry
from hoi4presence.localisation import CountryNames, cleanName, readGameLanguage
from hoi4presence.mods import Mod, modLabel, parseDescriptor, readEnabledMods
from hoi4presence.presence import FIELD_MAX, LOGO_TEXT, buildIdlePresence, buildPresence, fitField
from hoi4presence.saves import SaveHeader
from hoi4presence.session import CONTINUE_GAME_FILE, readContinueGameName, readSession, resolveCountry
from hoi4presence.userconfig import (
    CONFIG_FILE,
    TEMPLATE,
    UserConfig,
    ensureConfigFile,
    loadUserConfig,
    parseUserConfig,
)

START = 1_700_000_000.0
SERBIA_2020 = SaveHeader(tag="SER", ideology="neutrality", date="2020.1.1.12", difficulty="normal")


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8-sig")
    return path


@pytest.fixture
def documents(tmp_path: Path) -> Path:
    docs = tmp_path / "Hearts of Iron IV"
    workshop = tmp_path / "workshop" / "394360"

    tfr = workshop / "2820469328"
    write(
        docs / "mod" / "ugc_2820469328.mod",
        'version="1.6"\ntags={\n\t"Alternative History"\n\t"name=not this"\n}\n'
        'replace_path="history/countries"\nreplace_path="common/national_focus"\n'
        f'name="The Fire Rises"\nsupported_version="1.16.*"\npath="{tfr.as_posix()}"\nremote_file_id="2820469328"\n',
    )
    write(
        tfr / "localisation" / "english" / "countries_l_english.yml",
        'l_english:\n SER:0 "Serbia"\n SER_DEF:0 "the Republic of Serbia"\n SER_ADJ:0 "Serbian"\n'
        ' GER:0 "Germany"\n SER_focus_road:0 "Serbia Road"\n ZZX:0 "[ZZX.GetName]"\n',
    )

    write(
        docs / "mod" / "yugoslavia_reborn.mod",
        'name="Yugoslavia Reborn"\npath="mod/yugoslavia_reborn"\ndependencies={\n\t"The Fire Rises"\n}\n',
    )
    write(
        docs / "mod" / "yugoslavia_reborn" / "localisation" / "replace" / "yr_countries_l_english.yml",
        'l_english:\n SER_neutrality:0 "§YRepublic of Serbia§!"\n NYU:0 "New Yugoslavia"\n',
    )
    write(
        docs / "mod" / "yugoslavia_reborn" / "localisation" / "french" / "yr_countries_l_french.yml",
        'l_french:\n NYU:0 "Nouvelle Yougoslavie"\n',
    )

    write(docs / "mod" / "ui_mod.mod", 'name="Better Mod Names"\npath="mod/ui_mod"\n')

    write(
        docs / "dlc_load.json",
        json.dumps(
            {
                "enabled_mods": ["mod/ugc_2820469328.mod", "mod/yugoslavia_reborn.mod", "mod/ui_mod.mod"],
                "disabled_dlcs": [],
            }
        ),
    )
    write(docs / "settings.txt", 'language="l_french"\nsave_as_binary=no\n')
    return docs


def test_descriptor_name_ignores_quoted_values_inside_blocks():
    fields = parseDescriptor('tags={\n\t"name=not this"\n}\nname="The Fire Rises"\npath="C:/mods/tfr"\n').fields

    assert fields["name"] == "The Fire Rises"
    assert fields["path"] == "C:/mods/tfr"


def test_descriptor_blocks_and_replace_paths():
    descriptor = parseDescriptor(
        'replace_path="history/states"\nreplace_path="map/strategicregions"\n'
        'dependencies={\n\t"The Road to 56"\n\t"Road to 56: Retro Release"\n}\ntags={ "Map" "Graphics" }\n'
        'name="Road to 56 : Expanded"\n'
    )

    assert descriptor.replacePaths == ("history/states", "map/strategicregions")
    assert descriptor.blocks["dependencies"] == ("The Road to 56", "Road to 56: Retro Release")
    assert descriptor.blocks["tags"] == ("Map", "Graphics")
    assert descriptor.fields["name"] == "Road to 56 : Expanded"


def test_enabled_mods_are_read_in_load_order(documents):
    mods = readEnabledMods(documents)

    assert [mod.name for mod in mods] == ["The Fire Rises", "Yugoslavia Reborn", "Better Mod Names"]
    assert mods[1].contentDir == documents / "mod" / "yugoslavia_reborn"
    assert [mod.isOverhaul for mod in mods] == [True, False, False]
    assert mods[1].dependencies == ("The Fire Rises",)


def test_vanilla_has_no_mods(tmp_path):
    assert readEnabledMods(tmp_path) == []


def test_a_broken_dlc_load_is_not_fatal(tmp_path):
    write(tmp_path / "dlc_load.json", "{ not json")

    assert readEnabledMods(tmp_path) == []


def test_a_missing_descriptor_is_skipped(tmp_path):
    write(tmp_path / "dlc_load.json", json.dumps({"enabled_mods": ["mod/gone.mod"]}))

    assert readEnabledMods(tmp_path) == []


def test_windows_absolute_descriptor_paths_are_kept(tmp_path):
    write(tmp_path / "dlc_load.json", json.dumps({"enabled_mods": ["C:/nowhere/x.mod"]}))

    assert readEnabledMods(tmp_path) == []


MODS = [
    Mod("The Fire Rises", replacePaths=("history/countries",)),
    Mod("Yugoslavia Reborn", dependencies=("The Fire Rises",)),
    Mod("Better Mod Names"),
]


def utility(name: str) -> Mod:
    return Mod(name)


ROAD_TO_56_PLAYSET = [
    utility("Animated Super Events"),
    Mod("[TNO MAP] Compatibility Patch", dependencies=("Kaiserreich", "The Fire Rises")),
    Mod("Captured Generals Expanded", dependencies=("Equestria at War",)),
    utility("Descriptive Icons"),
    utility("Emoneh's Army HQs"),
    utility("Map Modes+"),
    utility("Native Country Names Revived"),
    utility("Reichskommissariats Plus"),
    Mod(
        "Road to 56 : Expanded",
        replacePaths=("gfx/loadingscreens",),
        dependencies=("The Road to 56", "The Road to 56 [BETA]"),
    ),
    Mod("The Road to 56", replacePaths=("history/states", "map/strategicregions")),
]


def test_mod_line_names_the_overhaul_and_its_submods_and_counts_the_rest():
    assert modLabel(MODS) == "The Fire Rises + Yugoslavia Reborn + 1 mod"
    assert modLabel(ROAD_TO_56_PLAYSET) == "The Road to 56 + Road to 56 : Expanded + 8 mods"


def test_a_compatibility_patch_for_an_absent_overhaul_is_only_counted():
    assert "TNO" not in modLabel(ROAD_TO_56_PLAYSET)


def test_without_an_overhaul_the_line_says_vanilla():
    assert modLabel([utility("Descriptive Icons"), utility("Map Modes+")]) == "Vanilla + 2 mods"


def test_pinned_mods_are_named_instead_of_counted():
    label = modLabel(ROAD_TO_56_PLAYSET, pinned=["reichskommissariats plus"])

    assert label == "The Road to 56 + Road to 56 : Expanded + Reichskommissariats Plus + 7 mods"


def test_mod_line_hides_and_renames_case_insensitively():
    label = modLabel(MODS, hidden=["better mod names "], renames={"the fire rises": "TFR"})

    assert label == "TFR + Yugoslavia Reborn"


def test_show_all_names_every_mod():
    assert modLabel(MODS, showAll=True) == "The Fire Rises + Yugoslavia Reborn + Better Mod Names"


def test_everything_hidden_means_no_line():
    assert modLabel([utility("Map Modes+")], hidden=["Map Modes+"]) == ""


def test_a_long_playset_is_clipped_to_discords_limit():
    many = [Mod(f"A rather long mod name number {index}") for index in range(10)]
    line = fitField(modLabel(many, showAll=True))

    assert len(line) == FIELD_MAX
    assert line.endswith("…")


def test_a_one_letter_field_is_dropped_rather_than_rejected():
    assert fitField("X") is None


def test_mods_go_in_the_flags_hover_text():
    payload = buildPresence(getCountry("SER"), SERBIA_2020, START, "The Fire Rises + Yugoslavia Reborn")

    assert payload["details"] == "Serbia — Non-Aligned"
    assert payload["state"] == "1 Jan 2020 · Regular"
    assert payload["large_text"] == "The Fire Rises + Yugoslavia Reborn"


def test_a_long_mod_line_is_clipped_in_the_hover_text():
    payload = buildPresence(getCountry("SER"), SERBIA_2020, START, "x" * 300)

    assert len(payload["large_text"]) == FIELD_MAX


def test_without_mods_the_payload_is_unchanged():
    assert buildPresence(getCountry("SER"), SERBIA_2020, START) == buildPresence(
        getCountry("SER"), SERBIA_2020, START, ""
    )
    assert buildPresence(getCountry("SER"), SERBIA_2020, START)["state"] == "1 Jan 2020 · Regular"


def test_the_idle_card_is_unchanged():
    assert buildIdlePresence(START)["large_text"] == LOGO_TEXT
    assert "state" not in buildIdlePresence(START)


def test_game_language_comes_from_settings():
    assert readGameLanguage('language="l_french"\n') == "l_french"
    assert readGameLanguage("save_as_binary=no\n") is None


def test_scripted_names_are_not_shown_raw():
    assert cleanName("[ZZX.GetName]") is None
    assert cleanName("§YRepublic§!") == "Republic"


def test_ideology_name_from_a_submod_wins(documents):
    mods = readEnabledMods(documents)
    dirs = [mod.contentDir for mod in mods]

    names = CountryNames()
    assert names.lookup("SER", "neutrality", dirs, "l_french") == "Republic of Serbia"
    assert names.lookup("SER", "communism", dirs, "l_french") == "Serbia"


def test_game_language_is_preferred_over_english(documents):
    dirs = [mod.contentDir for mod in readEnabledMods(documents)]

    assert CountryNames().lookup("NYU", "neutrality", dirs, "l_french") == "Nouvelle Yougoslavie"
    assert CountryNames().lookup("NYU", "neutrality", dirs, "l_english") == "New Yugoslavia"


def test_a_replace_file_beats_an_overhaul_loaded_after_it(tmp_path):
    names = tmp_path / "native_names"
    overhaul = tmp_path / "road_to_56"
    write(
        names / "localisation" / "english" / "replace" / "countries_l_english.yml",
        'l_english:\n GER_fascism: "Deutsches Reich"\n GER: "Deutschland"\n',
    )
    write(
        overhaul / "localisation" / "english" / "countries_l_english.yml",
        'l_english:\n GER_fascism:0 "German Reich"\n GER:0 "Germany"\n GER_communism:0 "Socialist Germany"\n',
    )

    lookup = CountryNames()
    assert lookup.lookup("GER", "fascism", [names, overhaul], "l_english") == "Deutsches Reich"
    assert lookup.lookup("GER", "communism", [names, overhaul], "l_english") == "Socialist Germany"


def test_unknown_tags_have_no_mod_name(documents):
    dirs = [mod.contentDir for mod in readEnabledMods(documents)]

    assert CountryNames().lookup("ZZX", "neutrality", dirs, None) is None
    assert CountryNames().lookup("SER", "neutrality", [], None) is None


def test_mod_line_settings_are_read():
    config = parseUserConfig({"mod_line": "all", "pinned_mods": ["A", ""]})

    assert config.modLine == "all"
    assert config.pinnedMods == ("A",)
    assert parseUserConfig({"mod_line": "none"}).modLine == "auto"


def test_template_is_written_once_and_parses_to_the_defaults(tmp_path):
    ensureConfigFile(tmp_path)
    path = tmp_path / CONFIG_FILE
    path.write_text(path.read_text(encoding="utf-8").replace('"hidden_mods": []', '"hidden_mods": ["x"]'))
    ensureConfigFile(tmp_path)

    assert loadUserConfig(tmp_path).hiddenMods == ("x",)
    assert loadUserConfig(tmp_path).showMods is True


def test_the_template_holds_the_defaults():
    assert parseUserConfig(TEMPLATE) == UserConfig()


def test_broken_settings_fall_back_to_defaults(tmp_path):
    write(tmp_path / CONFIG_FILE, '{"show_mods": false,')

    assert loadUserConfig(tmp_path).showMods is True


def test_country_overrides_need_an_https_flag():
    config = parseUserConfig({"countries": {"ser": {"name": "Srbija", "flag": "http://insecure.png"}}})

    assert config.countries["SER"].name == "Srbija"
    assert config.countries["SER"].flag is None


def test_session_combines_mods_settings_and_names(documents):
    write(
        documents / CONFIG_FILE,
        json.dumps(
            {
                "hidden_mods": ["Better Mod Names"],
                "mod_names": {"The Fire Rises": "TFR"},
                "countries": {"NYU": {"flag": "https://example.com/nyu.png"}},
            }
        ),
    )
    session = readSession(documents)
    names = CountryNames()

    assert session.gameLanguage == "l_french"
    assert session.modLine == "TFR + Yugoslavia Reborn"

    serbia = resolveCountry(SERBIA_2020, session, names)
    assert serbia.name == "Republic of Serbia"
    assert serbia.flag == getCountry("SER").flag

    newYugoslavia = resolveCountry(SaveHeader("NYU", "communism", "2025.1.1.1", "hard"), session, names)
    assert newYugoslavia.name == "Nouvelle Yougoslavie"
    assert newYugoslavia.flag == "https://example.com/nyu.png"


GERMANY_1936 = SaveHeader(tag="GER", ideology="fascism", date="1936.2.9.9", difficulty="normal")
CONTINUE_GERMANY = {
    "title": "Deutsches Reich 1936.2.9.9",
    "desc": "",
    "date": "Tue Oct 20 14:57:03 2026\n",
    "filename": "GER_1936_02_09_09.hoi4",
    "is_remote": False,
}


def test_the_games_own_title_names_the_country():
    assert readContinueGameName(CONTINUE_GERMANY, "C:\\saves\\GER_1936_02_09_09.hoi4") == "Deutsches Reich"
    assert readContinueGameName(CONTINUE_GERMANY, "/saves/ger_1936_02_09_09.hoi4") == "Deutsches Reich"


def test_the_title_of_another_save_is_ignored():
    assert readContinueGameName(CONTINUE_GERMANY, "/saves/autosave.hoi4") is None
    assert readContinueGameName(None, "/saves/GER_1936_02_09_09.hoi4") is None
    assert readContinueGameName({"title": 3, "filename": "x"}, "x") is None


def test_continue_game_wins_over_localisation_but_not_over_the_player(documents):
    write(documents / CONTINUE_GAME_FILE, json.dumps({**CONTINUE_GERMANY, "title": "Srbija 2020.1.1.12"}))
    savePath = documents / "save games" / "GER_1936_02_09_09.hoi4"
    session = readSession(documents)

    assert resolveCountry(SERBIA_2020, session, CountryNames(), savePath).name == "Srbija"

    write(documents / CONFIG_FILE, json.dumps({"countries": {"SER": {"name": "Serbie"}}}))
    session = readSession(documents)
    assert resolveCountry(SERBIA_2020, session, CountryNames(), savePath).name == "Serbie"


def test_the_mod_line_can_be_switched_off(documents):
    write(documents / CONFIG_FILE, json.dumps({"show_mods": False}))

    assert readSession(documents).modLine == ""


def test_no_documents_folder_means_plain_behaviour():
    session = readSession(None)

    assert session.modLine == ""
    assert resolveCountry(SERBIA_2020, session, CountryNames()) == getCountry("SER")


@pytest.mark.parametrize(("choice", "expected"), [("game", None), ("country", 2)])
def test_status_text_choice(choice, expected):
    payload = buildPresence(getCountry("SER"), SERBIA_2020, START, "The Fire Rises", choice)

    assert payload.get("status_display_type") == expected


def test_unknown_status_text_uses_the_default():
    assert parseUserConfig({"status_text": "anything"}).statusText == "game"
    assert parseUserConfig({"status_text": "mods"}).statusText == "game"
    assert parseUserConfig({"status_text": "country"}).statusText == "country"
