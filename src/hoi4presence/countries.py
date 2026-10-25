"""Mapping from HOI4 country tags to a display name and a Discord image.

Two styles of image reference live in this table:

* a short key such as ``"ger"`` names an asset uploaded to the Discord developer
  portal. Every one of those is mirrored as a PNG under ``assets/initialCountries/``
  so the set stays reviewable; ``tests/test_countries_data.py`` enforces that the
  two sides stay in sync.
* a full ``https://`` URL points straight at an image the portal does not host,
  mostly Wikimedia Commons. Released (non-starting) countries use these.

Add new countries to :data:`countries` below. See AGENTS.md for the rules.
"""

from __future__ import annotations

from dataclasses import dataclass

# Shown when a tag is unknown, or when its entry has no usable image.
DEFAULT_LARGE_IMAGE = "hoi4-logo2"

# List of countries, add more if you want
countries: dict[str, tuple[str, str]] = {
    # Countries that have more than one tag:
    # ITA, SOV, FRA, SPR, BUL, D##
    # especial case for the civil war:
    "D##": ("Civil War Country", DEFAULT_LARGE_IMAGE),
    # handling the special cases
    # Idk why they have more tags, since the game only uses the first one. But I'll add them anyway.
    "SOV": ("Soviet Union", "sov"),
    "ITA": ("Italy", "ita"),
    "SPR": ("Spain", "spr"),
    "SPA": ("Nationalist Spain", "spa"),
    "SPD": ("Republican Spain", "spd"),
    "BUL": ("Bulgaria", "bul"),
    "FRA": ("France", "fra"),
    "VIC": ("France", "vic"),  # wheres free france?
    # Initial countries:
    "AFG": ("Afghanistan", "afg"),
    "ALB": ("Albania", "alb"),
    "ARG": ("Argentina", "arg"),
    "AFA": ("Sultanate of Aussa", "afa"),
    "AST": ("Australia", "ast"),
    "AUS": ("Austria", "aus"),
    "BEL": ("Belgium", "bel"),
    "BHU": ("Bhutan", "bhu"),
    "BOL": ("Bolivian Republic", "bol"),
    "BRA": ("Brazil", "bra"),
    "MAL": ("British Malaya", "mal"),
    "RAJ": ("British Raj", "raj"),
    "CAN": ("Dominion of Canada", "can"),
    "CHL": ("Chile", "chl"),
    "CHI": ("China", "chi"),
    "COL": ("Colombia", "col"),
    "PRC": ("Communist China", "prc"),
    "COS": ("Costa Rica", "cos"),
    "CUB": ("Cuba", "cub"),
    "CZE": ("Czechoslovakia", "cze"),
    "DEN": ("Denmark", "den"),
    "DOM": ("Dominican Republic", "dom"),
    "INS": ("Dutch East Indies", "ins"),
    "ECU": ("Ecuador", "ecu"),
    "ELS": ("El Salvador", "els"),
    "EST": ("Estonia", "est"),
    "ETH": ("Ethiopia", "eth"),
    "FIN": ("Finland", "fin"),
    "GER": ("German Reich", "ger"),
    "GRE": ("Kingdom of Greece", "gre"),
    "GXC": ("Guangxi Clique", "gxc"),
    "GUA": ("Guatemala", "gua"),
    "HAI": ("Haiti", "hai"),
    "HON": ("Honduras", "hon"),
    "HUN": ("Kingdom of Hungary", "hun"),
    "ICE": ("Iceland", "ice"),
    "PER": ("Iran", "per"),
    "IRQ": ("Iraq", "irq"),
    "IRE": ("Ireland", "ire"),
    "JAP": ("Japan", "jap"),
    "LAT": ("Latvia", "lat"),
    "LIB": ("Liberia", "lib"),
    "LIT": ("Lithuania", "lit"),
    "LUX": ("Luxembourg", "lux"),
    "MAN": ("Manchukuo", "man"),
    "MEN": ("Mengkukuo", "men"),
    "MEX": ("Mexico", "mex"),
    "MON": ("Mongolia", "mon"),
    "NEP": ("Nepal", "nep"),
    "HOL": ("Netherlands", "hol"),
    "NZL": ("New Zealand", "nzl"),
    "NIC": ("Nicaragua", "nic"),
    "NOR": ("Norway", "nor"),
    "OMA": ("Oman", "oma"),
    "PAN": ("Panama", "pan"),
    "PAR": ("Republic of Paraguay", "par"),
    "PRU": ("Peru", "pru"),
    "PHI": ("Philippines", "phi"),
    "POL": ("Poland", "pol"),
    "POR": ("Portugal", "por"),
    "ROM": ("Romania", "rom"),
    "SAU": ("Saudi Arabia", "sau"),
    "SHX": ("Shanxi", "shx"),
    "SIA": ("Siam", "sia"),
    "SIK": ("Sinkiang", "sik"),
    "SAF": ("South Africa", "saf"),
    "SWE": ("Sweden", "swe"),
    "SWI": ("Switzerland", "swi"),
    "TAN": ("Tannu Tuva", "tan"),
    "TIB": ("Tibet", "tib"),
    "TUR": ("Turkey", "tur"),
    "ENG": ("United Kingdom", "eng"),
    "USA": ("United States", "usa"),
    "URG": ("Uruguay", "urg"),
    "VEN": ("Venezuela", "ven"),
    "XSM": ("Xibei San Ma", "xsm"),
    "YEM": ("Yemen", "yem"),
    "YUG": ("Yugoslavia", "yug"),
    "YUN": ("Yunnan", "yun"),
    # Released countries:
    "ABK": (
        "Abkhazia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Flag_of_the_Republic_of_Abkhazia.svg/330px-Flag_of_the_Republic_of_Abkhazia.svg.png",
    ),
    "ADU": (
        "Al-Andalus",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Flag_of_Andaluc%C3%ADa.svg/330px-Flag_of_Andaluc%C3%ADa.svg.png",
    ),
    "ALG": (
        "Algeria",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/330px-Flag_of_Algeria.svg.png",
    ),
    "ALT": (
        "Altai",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Altai_Republic.svg/330px-Flag_of_Altai_Republic.svg.png",
    ),
    "ANG": (
        "Angola",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/330px-Flag_of_Angola.svg.png",
    ),
    "ARM": (
        "Armenia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_Armenia.svg/330px-Flag_of_Armenia.svg.png",
    ),
    "AZR": (
        "Azerbaijan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Azerbaijan.svg/330px-Flag_of_Azerbaijan.svg.png",
    ),
    "BAH": (
        "Bahamas",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flag_of_the_Bahamas.svg/330px-Flag_of_the_Bahamas.svg.png",
    ),
    "BAN": (
        "Bangladesh",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/330px-Flag_of_Bangladesh.svg.png",
    ),
    "BSK": (
        "Bashkortostan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Flag_of_Bashkortostan.svg/330px-Flag_of_Bashkortostan.svg.png",
    ),
    "NAV": (
        "Navarra",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Flag_of_the_Basque_Country.svg/330px-Flag_of_the_Basque_Country.svg.png",
    ),
    "BAY": ("Bavaria", "https://i.imgur.com/4LkDK0w.png"),
    "BLR": (
        "Belarus",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Flag_of_Belarus.svg/330px-Flag_of_Belarus.svg.png",
    ),
    "BLZ": (
        "Belize",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/330px-Flag_of_Belize.svg.png",
    ),
    # Was wrongly reusing Bangladesh's flag (copy-paste from BAN). The wiki is behind a
    # bot challenge so the real image could not be confirmed; the likely URL, following the
    # naming convention used by every other entry, is
    # https://hoi4.paradoxwikis.com/images/f/f2/Benishangul-Gumuz_Nation.png
    "BEG": ("Benishangul-Gumuz Nation", DEFAULT_LARGE_IMAGE),
    "BOS": ("Bosnia", "https://i.imgur.com/1EzEwR4.png"),
    "BOT": (
        "Botswana",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_Botswana.svg/330px-Flag_of_Botswana.svg.png",
    ),
    "BAS": (
        "British Antilles",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_the_United_Kingdom_%283-5%29.svg/330px-Flag_of_the_United_Kingdom_%283-5%29.svg.png",
    ),  # Using UK Flag
    "BRI": (
        "Brittany",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Flag_of_Brittany_%28Gwenn_ha_du%29.svg/330px-Flag_of_Brittany_%28Gwenn_ha_du%29.svg.png",
    ),
    "BUK": (
        "Bukhara",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Flag_of_the_Bukharan_People%27s_Soviet_Republic.svg/330px-Flag_of_the_Bukharan_People%27s_Soviet_Republic.svg.png",
    ),
    "BRM": (
        "Burma",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Flag_of_Myanmar.svg/330px-Flag_of_Myanmar.svg.png",
    ),
    "BRD": (
        "Burundi",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Flag_of_Burundi.svg/330px-Flag_of_Burundi.svg.png",
    ),
    "BYA": (
        "Buryatia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Flag_of_Buryatia.svg/330px-Flag_of_Buryatia.svg.png",
    ),
    "CAM": (
        "Cambodia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/330px-Flag_of_Cambodia.svg.png",
    ),
    "CMR": (
        "Cameroon",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Cameroon.svg/330px-Flag_of_Cameroon.svg.png",
    ),
    "CAT": ("Catalonia", "https://i.imgur.com/qucdBrZ.png"),
    "CAY": ("Cayenne", "https://i.imgur.com/vH2hzqz.png"),
    "CAR": (
        "Central African Republic",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/330px-Flag_of_the_Central_African_Republic.svg.png",
    ),
    "CHA": (
        "Chad",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/330px-Flag_of_Chad.svg.png",
    ),
    "CIN": ("Chechen-Ingush Republic", "https://i.imgur.com/CSWCRN2.jpeg"),
    "CKK": ("Chukotka", "https://i.imgur.com/ftpUAMw.png"),
    "CHU": (
        "Chuvashia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Flag_of_Chuvashia.svg/330px-Flag_of_Chuvashia.svg.png",
    ),
    "COR": ("Corsica", "https://i.imgur.com/0y63AmO.png"),
    "CSA": ("Confederacy of American States", DEFAULT_LARGE_IMAGE),
    "RCG": (
        "Congo-Brazzaville",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/330px-Flag_of_the_Republic_of_the_Congo.svg.png",
    ),
    "IVO": (
        "Côte d'Ivoire",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_C%C3%B4te_d%27Ivoire.svg/330px-Flag_of_C%C3%B4te_d%27Ivoire.svg.png",
    ),
    "CRI": (
        "Crimea",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Flag_of_Crimea.svg/330px-Flag_of_Crimea.svg.png",
    ),
    "CRO": (
        "Croatia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Croatia.svg/330px-Flag_of_Croatia.svg.png",
    ),
    "CYP": (
        "Cyprus",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Cyprus.svg/330px-Flag_of_Cyprus.svg.png",
    ),
    "DAG": ("Dagestan", "https://i.imgur.com/cxnthyw.png"),
    "DAH": (
        "Dahomey",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/330px-Flag_of_Benin.svg.png",
    ),
    "DNZ": (
        "Danzig",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Flag_of_the_Free_City_of_Danzig.svg/330px-Flag_of_the_Free_City_of_Danzig.svg.png",
    ),
    "DJI": (
        "Djibouti",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Flag_of_Djibouti.svg/330px-Flag_of_Djibouti.svg.png",
    ),
    "DON": ("Don Host", "https://i.imgur.com/DjrdiB4.png"),
    "AOI": ("Italian State of East Africa", DEFAULT_LARGE_IMAGE),
    "DDR": (
        "East Germany",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Flag_of_East_Germany.svg/330px-Flag_of_East_Germany.svg.png",
    ),
    "EGY": (
        "Kingdom of Egypt",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Egypt_%281922-1958%29.svg/330px-Flag_of_Egypt_%281922-1958%29.svg.png",
    ),
    "EQG": (
        "Equatorial Guinea",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Equatorial_Guinea.svg/330px-Flag_of_Equatorial_Guinea.svg.png",
    ),
    "ERI": (
        "Eritrea",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Flag_of_Eritrea.svg/330px-Flag_of_Eritrea.svg.png",
    ),
    "FER": (
        "Far Eastern Republic",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Flag_of_Far_Eastern_Republic.svg/330px-Flag_of_Far_Eastern_Republic.svg.png",
    ),
    "GAB": (
        "Gabon",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Flag_of_Gabon.svg/330px-Flag_of_Gabon.svg.png",
    ),
    "GLC": (
        "Galicia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Galicia.svg/330px-Flag_of_Galicia.svg.png",
    ),
    "GBA": ("Gambela", DEFAULT_LARGE_IMAGE),
    "GAM": (
        "Gambia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_The_Gambia.svg/330px-Flag_of_The_Gambia.svg.png",
    ),
    "GEO": (
        "Georgia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Georgia.svg/330px-Flag_of_Georgia.svg.png",
    ),
    "GHA": (
        "Ghana",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Ghana.svg/330px-Flag_of_Ghana.svg.png",
    ),
    "GDL": ("Guadeloupe", "https://i.imgur.com/n1UPF8e.png"),
    "GNA": (
        "Guinea",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Flag_of_Guinea.svg/330px-Flag_of_Guinea.svg.png",
    ),
    "GNB": (
        "Guinea-Bissau",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Guinea-Bissau.svg/330px-Flag_of_Guinea-Bissau.svg.png",
    ),
    "GYA": ("Guyana", "https://i.imgur.com/oH9tyzR.png"),
    "HAR": ("Harar", "https://i.imgur.com/v08C5mU.png"),
    "HAW": (
        "Hawaii",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Flag_of_Hawaii.svg/330px-Flag_of_Hawaii.svg.png",
    ),
    "HRZ": ("Herzegovina", DEFAULT_LARGE_IMAGE),
    "ISR": (
        "Israel",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Israel.svg/330px-Flag_of_Israel.svg.png",
    ),
    "JAM": (
        "Jamaica",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Jamaica.svg/330px-Flag_of_Jamaica.svg.png",
    ),
    "JOR": (
        "Jordan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Flag_of_Jordan.svg/330px-Flag_of_Jordan.svg.png",
    ),
    "KBK": (
        "Kabardino Balkaria",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Flag_of_Kabardino-Balkaria.svg/330px-Flag_of_Kabardino-Balkaria.svg.png",
    ),
    "KAL": (
        "Kalmykia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Kalmykia.svg/330px-Flag_of_Kalmykia.svg.png",
    ),
    "KKP": (
        "Karakalpakstan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Flag_of_Karakalpakstan.svg/330px-Flag_of_Karakalpakstan.svg.png",
    ),
    "KAR": (
        "Karelia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Flag_of_Karelia.svg/330px-Flag_of_Karelia.svg.png",
    ),
    "KSH": (
        "Kashubia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/POL_Kaszuby_flag.svg/330px-POL_Kaszuby_flag.svg.png",
    ),
    "KAZ": (
        "Kazakhstan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kazakhstan.svg/330px-Flag_of_Kazakhstan.svg.png",
    ),
    "KEN": (
        "Kenya",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Kenya.svg/330px-Flag_of_Kenya.svg.png",
    ),
    "KHA": (
        "Khakassia",
        "https://i.imgur.com/wnoTtHs.gif",
    ),  # Only img I could find of this flag, need to test if Discord API accepts .gif
    "KHI": ("Khiva", DEFAULT_LARGE_IMAGE),
    "KOM": (
        "Komi",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Flag_of_Komi.svg/330px-Flag_of_Komi.svg.png",
    ),
    "KOR": (
        "Korea",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/330px-Flag_of_South_Korea.svg.png",
    ),
    "KOS": (
        "Kosovo",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Kosovo.svg/330px-Flag_of_Kosovo.svg.png",
    ),
    "KUB": ("Kuban", "https://i.imgur.com/GBRFUnx.png"),
    "KUW": (
        "Kuwait",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Flag_of_Kuwait.svg/330px-Flag_of_Kuwait.svg.png",
    ),
    "KUR": (
        "Kurdistan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Flag_of_Kurdistan.svg/330px-Flag_of_Kurdistan.svg.png",
    ),
    "KYR": (
        "Kyrgyzstan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Flag_of_Kyrgyzstan.svg/330px-Flag_of_Kyrgyzstan.svg.png",
    ),
    "LAO": (
        "Laos",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Laos.svg/330px-Flag_of_Laos.svg.png",
    ),
    "LEB": (
        "Lebanon",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Flag_of_Lebanon.svg/330px-Flag_of_Lebanon.svg.png",
    ),
    "LBA": (
        "Libya",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Libya.svg/330px-Flag_of_Libya.svg.png",
    ),
    "LBV": ("Lombardy-Venetia", "https://i.imgur.com/MWYmgso.png"),
    "MAC": (
        "Macedonia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_North_Macedonia.svg/330px-Flag_of_North_Macedonia.svg.png",
    ),
    "MAD": (
        "Madagascar",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Madagascar.svg/330px-Flag_of_Madagascar.svg.png",
    ),
    "MLW": (
        "Malawi",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Flag_of_Malawi.svg/330px-Flag_of_Malawi.svg.png",
    ),
    "MLD": (
        "Maldives",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Maldives.svg/330px-Flag_of_Maldives.svg.png",
    ),
    "MLI": (
        "Mali",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_Mali.svg/330px-Flag_of_Mali.svg.png",
    ),
    "MLT": (
        "Malta",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Malta.svg/330px-Flag_of_Malta.svg.png",
    ),
    "MEL": (
        "Mari El",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Flag_of_Mari_El.svg/330px-Flag_of_Mari_El.svg.png",
    ),
    "GUM": ("Mariana Federation", DEFAULT_LARGE_IMAGE),
    "MRT": (
        "Mauritania",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Flag_of_Mauritania.svg/330px-Flag_of_Mauritania.svg.png",
    ),
    "MEK": ("Mecklenburg", "https://i.imgur.com/pkzTyCX.png"),
    "FIJ": (
        "Fiji",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Fiji.svg/330px-Flag_of_Fiji.svg.png",
    ),
    "FSM": (
        "Micronesia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Flag_of_the_Federated_States_of_Micronesia.svg/330px-Flag_of_the_Federated_States_of_Micronesia.svg.png",
    ),
    "MOL": (
        "Moldova",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Moldova.svg/330px-Flag_of_Moldova.svg.png",
    ),
    "MNT": (
        "Montenegro",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Montenegro.svg/330px-Flag_of_Montenegro.svg.png",
    ),
    "MOR": (
        "Morocco",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Morocco.svg/330px-Flag_of_Morocco.svg.png",
    ),
    "MZB": (
        "Mozambique",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Mozambique.svg/330px-Flag_of_Mozambique.svg.png",
    ),
    "NMB": (
        "Namibia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Namibia.svg/330px-Flag_of_Namibia.svg.png",
    ),
    "NEN": (
        "Nenetsia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Flag_of_Nenets_Autonomous_District.svg/330px-Flag_of_Nenets_Autonomous_District.svg.png",
    ),
    "CRC": (
        "Netherlands Antilles",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Flag_of_the_Netherlands_Antilles_%281986%E2%80%932010%29.svg/330px-Flag_of_the_Netherlands_Antilles_%281986%E2%80%932010%29.svg.png",
    ),
    "NGR": (
        "Niger",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Flag_of_Niger.svg/330px-Flag_of_Niger.svg.png",
    ),
    "NGA": (
        "Nigeria",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_Nigeria.svg/330px-Flag_of_Nigeria.svg.png",
    ),
    "NIR": ("Northern Ireland", DEFAULT_LARGE_IMAGE),
    "NOA": (
        "North Ossetia-Alania",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Flag_of_North_Ossetia.svg/330px-Flag_of_North_Ossetia.svg.png",
    ),
    "OCC": (
        "Occitania",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Flag_of_Occitania.svg/330px-Flag_of_Occitania.svg.png",
    ),
    "ORO": (
        "Oromia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Flag_of_the_Oromia_Region.svg/330px-Flag_of_the_Oromia_Region.svg.png",
    ),
    "OVO": (
        "Ostyak Vogulia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Flag_of_Yugra.svg/330px-Flag_of_Yugra.svg.png",
    ),
    "PAK": (
        "Pakistan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Flag_of_Pakistan.svg/330px-Flag_of_Pakistan.svg.png",
    ),
    "PAL": (
        "Palestine",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Palestine.svg/330px-Flag_of_Palestine.svg.png",
    ),
    "PAP": (
        "Papal States",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_the_Papal_States_%281825-1870%29.svg/330px-Flag_of_the_Papal_States_%281825-1870%29.svg.png",
    ),
    "PNG": (
        "Papua New Guinea",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Flag_of_Papua_New_Guinea.svg/330px-Flag_of_Papua_New_Guinea.svg.png",
    ),
    "PRE": ("Prussia", "https://i.imgur.com/huWWo2P.png"),
    "PUE": (
        "Puerto Rico",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Flag_of_Puerto_Rico.svg/330px-Flag_of_Puerto_Rico.svg.png",
    ),
    "QAT": (
        "Qatar",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Flag_of_Qatar.svg/330px-Flag_of_Qatar.svg.png",
    ),
    "QEM": ("Qemant State", DEFAULT_LARGE_IMAGE),
    "RIF": (
        "Rif",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Flag_of_the_Republic_of_the_Rif.svg/330px-Flag_of_the_Republic_of_the_Rif.svg.png",
    ),
    "RWA": ("Rwanda", "https://i.imgur.com/PGcoWPx.png"),
    "WES": (
        "Western Sahara",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Flag_of_the_Sahrawi_Arab_Democratic_Republic.svg/330px-Flag_of_the_Sahrawi_Arab_Democratic_Republic.svg.png",
    ),
    "YAK": (
        "Sakha Republic",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Flag_of_Sakha.svg/330px-Flag_of_Sakha.svg.png",
    ),
    "SAM": (
        "Samoa",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Samoa.svg/330px-Flag_of_Samoa.svg.png",
    ),
    "SPM": (
        "Sardinia-Piedmont",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Civil_Flag_and_civil_Ensign_of_the_Savoyard_States_%281816-1848%29.svg/330px-Civil_Flag_and_civil_Ensign_of_the_Savoyard_States_%281816-1848%29.svg.png",
    ),
    "SAX": (
        "Saxony",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Flag_of_Saxony.svg/330px-Flag_of_Saxony.svg.png",
    ),
    "SHL": ("Schleswig-Holstein", "https://i.imgur.com/uJ4Rz2R.png"),
    "SCO": (
        "Scotland",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/330px-Flag_of_Scotland.svg.png",
    ),
    "SEN": (
        "Senegal",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Flag_of_Senegal.svg/330px-Flag_of_Senegal.svg.png",
    ),
    "SER": (
        "Serbia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/330px-Flag_of_Serbia.svg.png",
    ),
    "SID": ("Sidamo", "https://i.imgur.com/OEfH3Rc.png"),
    "SIE": (
        "Sierra Leone",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Flag_of_Sierra_Leone.svg/330px-Flag_of_Sierra_Leone.svg.png",
    ),
    "SIL": (
        "Silesia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Flag_of_Upper_Silesia.svg/330px-Flag_of_Upper_Silesia.svg.png",
    ),
    "SLO": (
        "Slovakia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/330px-Flag_of_Slovakia.svg.png",
    ),
    "SLV": (
        "Slovenia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Flag_of_Slovenia.svg/330px-Flag_of_Slovenia.svg.png",
    ),
    "SOL": (
        "Solomon Islands",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Flag_of_the_Solomon_Islands.svg/330px-Flag_of_the_Solomon_Islands.svg.png",
    ),
    "SOM": ("Somalia", "https://i.imgur.com/Y8Drza3.png"),
    "SRL": (
        "Sri Lanka",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/330px-Flag_of_Sri_Lanka.svg.png",
    ),
    "SUD": (
        "Sudan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Sudan.svg/330px-Flag_of_Sudan.svg.png",
    ),
    "SUR": (
        "Suriname",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Flag_of_Suriname.svg/330px-Flag_of_Suriname.svg.png",
    ),
    "SYR": (
        "Syria",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Flag_of_Syria_%282025-%29.svg/330px-Flag_of_Syria_%282025-%29.svg.png",
    ),
    "TAH": (
        "Tahiti",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Flag_of_French_Polynesia.svg/330px-Flag_of_French_Polynesia.svg.png",
    ),
    "TAJ": (
        "Tajikistan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Tajikistan.svg/330px-Flag_of_Tajikistan.svg.png",
    ),
    "TZN": (
        "Tanzania",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tanzania.svg/330px-Flag_of_Tanzania.svg.png",
    ),
    "TAT": (
        "Tatarstan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Flag_of_Tatarstan.svg/330px-Flag_of_Tatarstan.svg.png",
    ),
    "TAY": (
        "Taymyria",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Taymyr_Autonomous_Okrug.svg/330px-Flag_of_Taymyr_Autonomous_Okrug.svg.png",
    ),
    "TIG": (
        "Tigray",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Flag_of_the_Tigray_Region.svg/330px-Flag_of_the_Tigray_Region.svg.png",
    ),
    "TOG": (
        "Togo",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Flag_of_Togo.svg/330px-Flag_of_Togo.svg.png",
    ),
    "TRA": (
        "Transylvania",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Transylvania.svg/330px-Flag_of_Transylvania.svg.png",
    ),
    "TRI": (
        "Trinidad and Tobago",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Trinidad_and_Tobago.svg/330px-Flag_of_Trinidad_and_Tobago.svg.png",
    ),
    "TUN": (
        "Tunisia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Tunisia.svg/330px-Flag_of_Tunisia.svg.png",
    ),
    "TMS": (
        "Turkmenistan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Turkmenistan.svg/330px-Flag_of_Turkmenistan.svg.png",
    ),
    "TOS": ("Tuscany", "https://i.imgur.com/TdK1iAY.jpg"),
    "TTS": ("Two Sicilies", "https://i.imgur.com/9bm3H1Z.png"),
    "UDM": (
        "Udmurtia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Flag_of_Udmurtia.svg/330px-Flag_of_Udmurtia.svg.png",
    ),
    "UGA": (
        "Uganda",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flag_of_Uganda.svg/330px-Flag_of_Uganda.svg.png",
    ),
    "UKR": (
        "Ukraine",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/330px-Flag_of_Ukraine.svg.png",
    ),
    "USB": (
        "Unaligned States of America",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Flag_of_the_United_States.svg/330px-Flag_of_the_United_States.svg.png",
    ),  # Using US Flag
    "UAE": (
        "United Arab Emirates",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Flag_of_the_United_Arab_Emirates.svg/330px-Flag_of_the_United_Arab_Emirates.svg.png",
    ),
    "VOL": (
        "Upper Volta",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Flag_of_Upper_Volta.svg/330px-Flag_of_Upper_Volta.svg.png",
    ),
    "UZB": (
        "Uzbekistan",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Uzbekistan.svg/330px-Flag_of_Uzbekistan.svg.png",
    ),
    "VIN": (
        "Vietnam",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Vietnam.svg/330px-Flag_of_Vietnam.svg.png",
    ),
    "VLA": ("Vladivostok", DEFAULT_LARGE_IMAGE),
    "VGE": (
        "Volga Germany",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Flag_of_Volga_German_ASSR.svg/330px-Flag_of_Volga_German_ASSR.svg.png",
    ),
    "WLS": (
        "Wales",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Flag_of_Wales.svg/330px-Flag_of_Wales.svg.png",
    ),
    "WGR": (
        "West Germany",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Germany.svg/330px-Flag_of_Germany.svg.png",
    ),
    "HAN": ("Westphalia", "https://i.imgur.com/lBbQxjP.png"),
    "WUR": ("Wurtemberg", "https://i.imgur.com/5G1N75q.png"),
    "YAM": (
        "Yamalia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Flag_of_Yamal-Nenets_Autonomous_District.svg/330px-Flag_of_Yamal-Nenets_Autonomous_District.svg.png",
    ),
    "COG": (
        "Zaire",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Flag_of_Zaire_%281971%E2%80%931997%29.svg/330px-Flag_of_Zaire_%281971%E2%80%931997%29.svg.png",
    ),
    "ZAM": (
        "Zambia",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Zambia.svg/330px-Flag_of_Zambia.svg.png",
    ),
    "ZIM": (
        "Zimbabwe",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Flag_of_Zimbabwe.svg/330px-Flag_of_Zimbabwe.svg.png",
    ),
}


@dataclass(frozen=True)
class Country:
    """A country as the presence displays it."""

    name: str
    flag: str

    def __str__(self) -> str:
        return f"{self.name}, {self.flag}"


def getCountry(country: str) -> Country:
    """Return the :class:`Country` for a tag, falling back to the default image.

    Unknown tags resolve to the tag itself plus the default logo rather than
    being written back into :data:`countries` -- that mutation used to grow the
    table for the lifetime of the process and leak state between callers.
    """
    if not country:
        raise ValueError("Country code cannot be empty.")

    code = country.upper()
    name, flag = countries.get(code, (code, DEFAULT_LARGE_IMAGE))

    return Country(name, flag or DEFAULT_LARGE_IMAGE)


def withOverrides(country: Country, name: str | None = None, flag: str | None = None) -> Country:
    return Country(name or country.name, flag or country.flag)
