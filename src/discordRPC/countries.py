class Country:
   def __init__(self, name: str, flag: str):
      self.name = name
      self.flag = flag
   
   def __str__(self) -> str:
      return f"{self.name}, {self.flag}"

def getCountry(country: str) -> Country:
   """Returns a Country object from the country code."""
   if country == "" or not country:
      raise ValueError("Country code cannot be empty.")
   
   country = country.upper()

   countryTuple = countries.get(country)

   # This is raised when there is a country that isn't in the countries dictionary
   if countryTuple is None:
      countries[country] = (country, HOI_ICON)

   # Raised if there isn't an image link
   elif countryTuple[1] == "":
      countries[country] = (countryTuple[0], HOI_ICON)

   countryName = countries[country][0]
   flag = countries[country][1]

   return Country(countryName, flag)

HOI_ICON = "https://hoi4.paradoxwikis.com/images/8/8a/HoI4_icon.png"

# List of countries, add more if you want
#
# Small img comments: img dimensions are very small, and should be replaced with higher resolutions
# Keep in mind the small img comments may or may not be small anymore since the wiki has had updates to their flag
# resolutions before
#
# Missing comments: Could not find flag images on either the wiki or imgur
countries: dict[str, tuple[str, str]] = {

   # Countries in this block of code have more than one tag or have a special case
   "ITA" : ("Italy", "https://hoi4.paradoxwikis.com/images/2/2a/Italy.png"),
   "SOV" : ("Soviet Union", "https://hoi4.paradoxwikis.com/images/6/67/Soviet_Union.png"),
   "FRA" : ("France", "https://hoi4.paradoxwikis.com/images/d/de/France.png"),
   "SPR" : ("Spain", "https://hoi4.paradoxwikis.com/images/2/2c/Nationalist_Spain.png"),
   "BUL" : ("Bulgaria", "https://hoi4.paradoxwikis.com/images/f/f4/Bulgaria.png"),
   "D##" : ("Civil War Country", HOI_ICON),

   "AFG" : ("Afghanistan", "https://hoi4.paradoxwikis.com/images/7/7d/Afghanistan.png"),
   "ALB" : ("Albania", "https://hoi4.paradoxwikis.com/images/0/07/Albania.png"),
   "ARG" : ("Argentina", "https://hoi4.paradoxwikis.com/images/b/bc/Sultanate_of_Aussa.png"),
   "AFA" : ("Sultanate of Aussa", "https://hoi4.paradoxwikis.com/images/4/43/Australia.png"),
   "AST" : ("Australia", "https://hoi4.paradoxwikis.com/images/7/7f/Austria.png"),
   "AUS" : ("Austria", "https://hoi4.paradoxwikis.com/images/7/7f/Austria.png"),
   "BEL" : ("Belgium", "https://hoi4.paradoxwikis.com/images/3/32/Belgium.png"),
   "BHU" : ("Bhutan", "https://hoi4.paradoxwikis.com/images/8/85/Bhutan.png"),
   "BOL" : ("Bolivia", "https://hoi4.paradoxwikis.com/images/3/38/Bolivia.png"),
   "BRA" : ("Brazil", "https://hoi4.paradoxwikis.com/images/8/8c/Brazil.png"),
   "MAL" : ("British Malaya", "https://hoi4.paradoxwikis.com/images/f/f7/British_Malaya.png"),
   "RAJ" : ("British Raj", "https://hoi4.paradoxwikis.com/images/2/2f/British_Raj.png"),
   "CAN" : ("Dominion of Canada", "https://hoi4.paradoxwikis.com/images/e/e1/Dominion_of_Canada.png"),
   "CHL" : ("Chile", "https://hoi4.paradoxwikis.com/images/f/fa/Chile.png"),
   "CHI" : ("China", "https://hoi4.paradoxwikis.com/images/8/81/China.png"),
   "COL" : ("Colombia", "https://hoi4.paradoxwikis.com/images/8/80/Colombia.png"),
   "PRC" : ("Communist China", "https://hoi4.paradoxwikis.com/images/1/1a/Communist_China.png"),
   "COS" : ("Costa Rica", "https://hoi4.paradoxwikis.com/images/d/da/Costa_Rica.png"),
   "CUB" : ("Cuba", "https://hoi4.paradoxwikis.com/images/6/6c/Cuba.png"),
   "CZE" : ("Czechoslovakia", "https://hoi4.paradoxwikis.com/images/c/c1/Czechoslovakia.png"),
   "DEN" : ("Denmark", "https://hoi4.paradoxwikis.com/images/6/69/Denmark.png"),
   "DOM" : ("Dominican Republic", "https://hoi4.paradoxwikis.com/images/5/5b/Dominican_Republic.png"),
   "INS" : ("Dutch East Indies", "https://hoi4.paradoxwikis.com/images/3/32/Netherlands.png"),
   "ECU" : ("Ecuador", "https://hoi4.paradoxwikis.com/images/b/b2/Ecuador.png"),
   "ELS" : ("El Salvador", "https://hoi4.paradoxwikis.com/images/5/5c/El_Salvador.png"),
   "EST" : ("Estonia", "https://hoi4.paradoxwikis.com/images/6/6f/Estonia.png"),
   "ETH" : ("Ethiopia", "https://hoi4.paradoxwikis.com/images/0/06/Ethiopia.png"),
   "FIN" : ("Finland", "https://hoi4.paradoxwikis.com/images/c/c4/Finland.png"),
   "GER" : ("German Reich", "https://hoi4.paradoxwikis.com/images/e/e9/German_Reich.png"),
   "GRE" : ("Kingdom of Greece", "https://hoi4.paradoxwikis.com/images/8/8e/Kingdom_of_Greece.png"),
   "GXC" : ("Guangxi Clique", "https://hoi4.paradoxwikis.com/images/6/68/Guangxi_Clique.png"),
   "GUA" : ("Guatemala", "https://hoi4.paradoxwikis.com/images/5/55/Guatemala.png"),
   "HAI" : ("Haiti", "https://hoi4.paradoxwikis.com/images/2/28/Haiti.png"),
   "HON" : ("Honduras", "https://hoi4.paradoxwikis.com/images/0/09/Honduras.png"),
   "HUN" : ("Hungary", "https://hoi4.paradoxwikis.com/images/5/53/Kingdom_of_Hungary.png"),
   "PER" : ("Iran", "https://hoi4.paradoxwikis.com/images/d/d1/Iran.png"),
   "IRQ" : ("Iraq", "https://hoi4.paradoxwikis.com/images/c/c4/Iraq.png"),
   "IRE" : ("Ireland", "https://hoi4.paradoxwikis.com/images/4/4b/Ireland.png"),
   "JAP" : ("Japan", "https://hoi4.paradoxwikis.com/images/f/fc/Japan.png"),
   "LAT" : ("Latvia", "https://hoi4.paradoxwikis.com/images/7/7c/Latvia.png"),
   "LIB" : ("Liberia", "https://hoi4.paradoxwikis.com/images/0/05/Liberia.png"),
   "LIT" : ("Lithuania", "https://hoi4.paradoxwikis.com/images/d/d9/Lithuania.png"),
   "LUX" : ("Luxembourg", "https://hoi4.paradoxwikis.com/images/3/3f/Luxembourg.png"),
   "MAN" : ("Manchukuo", "https://hoi4.paradoxwikis.com/images/1/16/Manchukuo.png"),
   "MEN" : ("Mengkukuo", "https://hoi4.paradoxwikis.com/images/4/4d/Mengkukuo.png"),
   "MEX" : ("Mexico", "https://hoi4.paradoxwikis.com/images/0/0a/Mexico.png"),
   "MON" : ("Mongolia", "https://hoi4.paradoxwikis.com/images/b/bc/Mongolia.png"),
   "NEP" : ("Nepal", "https://hoi4.paradoxwikis.com/images/3/3a/Nepal.png"),
   "HOL" : ("Netherlands", "https://hoi4.paradoxwikis.com/images/3/32/Netherlands.png"),
   "NZL" : ("New Zealand", "https://hoi4.paradoxwikis.com/images/d/d9/New_Zealand.png"),
   "NIC" : ("Nicaragua", "https://hoi4.paradoxwikis.com/images/7/7e/Republic_of_Nicaragua.png"),
   "NOR" : ("Norway", "https://hoi4.paradoxwikis.com/images/0/0f/Norway.png"),
   "OMA" : ("Oman", "https://hoi4.paradoxwikis.com/images/2/27/Oman.png"),
   "PAN" : ("Panama", "https://hoi4.paradoxwikis.com/images/3/3f/Panama.png"),
   "PAR" : ("Paraguay", "https://hoi4.paradoxwikis.com/images/5/57/Paraguay.png"),
   "PRU" : ("Peru", "https://hoi4.paradoxwikis.com/images/a/a8/Peru.png"),
   "PHI" : ("Philippines", "https://hoi4.paradoxwikis.com/images/3/3b/Philippines.png"),
   "POL" : ("Poland", "https://hoi4.paradoxwikis.com/images/9/99/Poland.png"),
   "POR" : ("Portugal", "https://hoi4.paradoxwikis.com/images/1/12/Portugal.png"),
   "ROM" : ("Romania", "https://hoi4.paradoxwikis.com/images/8/8f/Romania.png"),
   "SAU" : ("Saudi Arabia", "https://hoi4.paradoxwikis.com/images/1/1f/Saudi_Arabia.png"),
   "SHX" : ("Shanxi", "https://hoi4.paradoxwikis.com/images/d/d0/Shanxi.png"),
   "SIA" : ("Siam", "https://hoi4.paradoxwikis.com/images/7/7e/Siam.png"),
   "SIK" : ("Sinkiang", "https://hoi4.paradoxwikis.com/images/b/b8/Sinkiang.png"),
   "SAF" : ("South Africa", "https://hoi4.paradoxwikis.com/images/e/ef/South_Africa.png"),
   "SWE" : ("Sweden", "https://hoi4.paradoxwikis.com/images/9/98/Sweden.png"),
   "SWI" : ("Switzerland", "https://hoi4.paradoxwikis.com/images/0/01/Switzerland.png"),
   "TAN" : ("Tannu Tuva", "https://hoi4.paradoxwikis.com/images/5/54/Tannu_Tuva.png"),
   "TIB" : ("Tibet", "https://hoi4.paradoxwikis.com/images/0/03/Tibet.png"),
   "TUR" : ("Turkey", "https://hoi4.paradoxwikis.com/images/b/b3/Turkey.png"),
   "ENG" : ("United Kingdom", "https://hoi4.paradoxwikis.com/images/2/29/United_Kingdom.png"),
   "USA" : ("United States", "https://hoi4.paradoxwikis.com/images/3/32/United_States.png"),
   "URG" : ("Uruguay", "https://hoi4.paradoxwikis.com/images/2/29/Uruguay.png"),
   "VEN" : ("Venezuela", "https://hoi4.paradoxwikis.com/images/5/5d/Venezuela.png"),
   "XSM" : ("Xibei San Ma", "https://hoi4.paradoxwikis.com/images/6/6e/Xibei_San_Ma.png"),
   "YEM" : ("Yemen", "https://hoi4.paradoxwikis.com/images/f/fc/Yemen.png"),
   "YUG" : ("Yugoslavia", "https://hoi4.paradoxwikis.com/images/f/f3/Yugoslavia.png"),
   "YUN" : ("Yunnan", "https://hoi4.paradoxwikis.com/images/3/3b/Yunnan.png"),
   "ABK" : ("Abkhazia", "https://hoi4.paradoxwikis.com/images/b/be/Abkhazia.png"),
   "ADU" : ("Al-Andalus", "https://hoi4.paradoxwikis.com/images/9/9f/Al-Andalus.png"),
   "ALG" : ("Algeria", "https://hoi4.paradoxwikis.com/images/4/40/Algeria.png"),
   "ALT" : ("Altai", "https://hoi4.paradoxwikis.com/images/c/c7/Altai.png"),
   "ANG" : ("Angola", "https://hoi4.paradoxwikis.com/images/c/c4/Angola.png"),
   "ARM" : ("Armenia", "https://hoi4.paradoxwikis.com/images/9/90/Republic_of_Armenia.png"),
   "AZR" : ("Azerbaijan", "https://hoi4.paradoxwikis.com/images/0/05/Azerbaijan.png"),
   "BAH" : ("Bahamas", "https://hoi4.paradoxwikis.com/images/3/33/Commonwealth_of_the_Bahamas.png"),
   "BAN" : ("Bangladesh", "https://hoi4.paradoxwikis.com/images/9/9e/Bangladesh.png"),
   "BSK" : ("Bashkortostan", "https://hoi4.paradoxwikis.com/images/0/05/Bashkortostan.png"),
   "NAV" : ("Navarra", "https://hoi4.paradoxwikis.com/images/c/c8/Basque_Country.png"),
   "BAY" : ("Bavaria", "https://i.imgur.com/4LkDK0w.png"),
   "BLR" : ("Belarus", "https://hoi4.paradoxwikis.com/images/5/5c/Belarus.png"),
   "BLZ" : ("Belize", "https://hoi4.paradoxwikis.com/images/d/dd/Belize.png"),
   "BEG" : ("Benishangul-Gumuz Nation", "https://hoi4.paradoxwikis.com/images/9/9e/Bangladesh.png"),
   "BOS" : ("Bosnia", "https://i.imgur.com/1EzEwR4.png"),
   "BOT" : ("Botswana", "https://hoi4.paradoxwikis.com/images/1/1e/Botswana.png"),
   "BAS" : ("British Antilles", ""), # Missing
   "BRI" : ("Brittany", "https://hoi4.paradoxwikis.com/images/1/1c/Brittany.png"),
   "BUK" : ("Bukhara", "https://hoi4.paradoxwikis.com/images/1/14/Bukharan_Jadidist_Republic.png"),
   "BRM" : ("Burma", "https://hoi4.paradoxwikis.com/images/7/78/Burma.png"),
   "BRD" : ("Burundi", "https://hoi4.paradoxwikis.com/images/6/63/Burundi.png"),
   "BYA" : ("Buryatia", "https://hoi4.paradoxwikis.com/images/2/2c/Republic_of_Buryatia.png"),
   "CAM" : ("Cambodia", "https://hoi4.paradoxwikis.com/images/9/94/Republic_of_Cambodia.png"),
   "CMR" : ("Cameroon", "https://hoi4.paradoxwikis.com/images/9/92/Cameroon.png"),
   "CAT" : ("Catalonia", "https://hoi4.paradoxwikis.com/images/c/ca/Catalonian_Free_Republic.png"), # Small img
   "CAY" : ("Cayenne", "link"), # Missing
   "CAR" : ("Central African Republic", "https://hoi4.paradoxwikis.com/images/d/d3/Central_African_Republic.png"),
   "CHA" : ("Chad", "https://hoi4.paradoxwikis.com/images/7/79/Chad.png"),
   "CIN" : ("Chechnya Ingushetia", ""), # Missing
   "CKK" : ("Chukotka", "link"), # Missing
   "CHU" : ("Chuvashia", "https://hoi4.paradoxwikis.com/images/f/fa/Chuvashia.png"),
   "COR" : ("Corsica", "https://hoi4.paradoxwikis.com/images/3/30/Corsican_Republic.png"), # Small img
   "CSA" : ("Confederacy of American States", "https://hoi4.paradoxwikis.com/images/0/0a/Confederacy_of_American_States.png"),
   "RCG" : ("Congo-Brazzaville", "https://hoi4.paradoxwikis.com/images/f/fa/Congo-Brazzaville.png"),
   "IVO" : ("Côte d'Ivoire", "https://hoi4.paradoxwikis.com/images/7/7f/C%C3%B4te_d%27Ivoire.png"),
   "CRI" : ("Crimea", "https://hoi4.paradoxwikis.com/images/6/64/Crimea.png"),
   "CRO" : ("Croatia", "https://hoi4.paradoxwikis.com/images/b/bb/Independent_State_of_Croatia.png"),
   "CYP" : ("Cyprus", "https://hoi4.paradoxwikis.com/images/2/2b/Republic_of_Cyprus.png"),
   "DAG" : ("Dagestan", ""), # Missing
   "DAH" : ("Dahomey", "https://hoi4.paradoxwikis.com/images/f/f1/Dahomey.png"),
   "DNZ" : ("Danzig", "https://hoi4.paradoxwikis.com/images/d/d8/Free_City_of_Danzig.png"),
   "DJI" : ("Djibouti", "https://hoi4.paradoxwikis.com/images/e/e2/Djibouti.png"),
   "DON" : ("Don Host", "https://hoi4.paradoxwikis.com/images/b/bc/Don_Host.png"), # Small img
   "AOI" : ("Italian State of East Africa", "https://hoi4.paradoxwikis.com/images/2/22/Italian_State_of_East_Africa.png"),
   "DDR" : ("East Germany", "https://hoi4.paradoxwikis.com/images/f/f2/East_Germany.png"),
   "EGY" : ("Kingdom of Egypt", "https://hoi4.paradoxwikis.com/images/7/7b/Kingdom_of_Egypt.png"),
   "EQG" : ("Equatorial Guinea", "https://hoi4.paradoxwikis.com/images/f/f5/Equatorial_Guinea.png"),
   "ERI" : ("Eritrea", "https://hoi4.paradoxwikis.com/images/8/8b/Eritrea.png"),
   "FER" : ("Far Eastern Republic", "https://hoi4.paradoxwikis.com/images/0/0a/Far_Eastern_Republic.png"),
   "GAB" : ("Gabon", "https://hoi4.paradoxwikis.com/images/e/e7/Gabon.png"),
   "GLC" : ("Galicia", "https://hoi4.paradoxwikis.com/images/1/11/Galicia.png"),
   "GBA" : ("Gambela", "https://hoi4.paradoxwikis.com/images/a/ad/Gambela.png"),
   "GAM" : ("Gambia", "https://hoi4.paradoxwikis.com/images/a/a0/The_Gambia.png"),
   "GEO" : ("Georgia", "https://hoi4.paradoxwikis.com/images/d/d1/Republic_of_Georgia.png"),
   "GHA" : ("Ghana", "https://hoi4.paradoxwikis.com/images/8/88/Ghana.png"),
   "GDL" : ("Guadeloupe", ""), # Missing
   "GNA" : ("Guinea", "https://hoi4.paradoxwikis.com/images/b/b2/Guinea.png"),
   "GNB" : ("Guinea-Bissau", "https://hoi4.paradoxwikis.com/images/6/67/Guinea-Bissau.png"),
   "GYA" : ("Guyana", "https://i.imgur.com/loNcNcI.png"), # Small img
   "HAR" : ("Harar", "https://hoi4.paradoxwikis.com/images/9/90/Emirate_of_Harar.png"), # Small img
   "HAW" : ("Hawaii", fr"https://hoi4.paradoxwikis.com/images/d/d7/Kingdom_of_Hawai%27i.png"),
   "HRZ" : ("Herzegovina", "https://hoi4.paradoxwikis.com/images/f/f8/Herzegovina.png"),
   "ICE" : ("Iceland", "https://hoi4.paradoxwikis.com/images/c/c1/Iceland.png"),
   "ISR" : ("Israel", "https://hoi4.paradoxwikis.com/images/9/94/Israel.png"),
   "JAM" : ("Jamaica", "https://hoi4.paradoxwikis.com/images/e/e7/Jamaica.png"),
   "JOR" : ("Jordan", "https://hoi4.paradoxwikis.com/images/e/e4/Jordan.png"),
   "KBK" : ("Kabardino Balkaria", "https://hoi4.paradoxwikis.com/images/a/ab/Federal_Republic_of_Kabardins_and_Karachay-Balkars.png"),
   "KAL" : ("Kalmykia", "https://hoi4.paradoxwikis.com/images/8/8d/Kalmykia.png"),
   "KKP" : ("Karakalpakstan", "https://hoi4.paradoxwikis.com/images/f/ff/Republic_of_Karakalpakstan.png"),
   "KAR" : ("Karelia", "https://hoi4.paradoxwikis.com/images/d/d1/Karelia.png"),
   "KSH" : ("Kashubia", "https://hoi4.paradoxwikis.com/images/c/ca/Kashubia.png"),
   "KAZ" : ("Kazakhstan", "https://hoi4.paradoxwikis.com/images/0/0e/Kazakhstan.png"),
   "KEN" : ("Kenya", "https://hoi4.paradoxwikis.com/images/b/b9/Kenya.png"),
   "KHA" : ("Khakassia", "https://hoi4.paradoxwikis.com/images/8/87/Republic_of_Khakassia.png"), # Small img
   "KHI" : ("Khiva", "https://hoi4.paradoxwikis.com/images/a/a0/Khivan_Jadidist_Republic.png"),
   "KOM" : ("Komi", "https://hoi4.paradoxwikis.com/images/7/74/Komi_Republic.png"),
   "KOR" : ("Korea", "https://hoi4.paradoxwikis.com/images/4/45/Korea.png"),
   "KOS" : ("Kosovo", "https://hoi4.paradoxwikis.com/images/a/a9/Kosovo.png"),
   "KUB" : ("Kuban", "https://hoi4.paradoxwikis.com/images/3/38/Kuban_Host.png"), # Small img
   "KUW" : ("Kuwait", "https://hoi4.paradoxwikis.com/images/5/5c/Kuwait.png"),
   "KUR" : ("Kurdistan", "https://hoi4.paradoxwikis.com/images/9/95/Kurdistan.png"),
   "KYR" : ("Kyrgyzstan", "https://hoi4.paradoxwikis.com/images/c/ce/Kyrgyzstan.png"),
   "LAO" : ("Laos", "https://hoi4.paradoxwikis.com/images/1/16/Republic_of_Laos.png"),
   "LEB" : ("Lebanon", "https://hoi4.paradoxwikis.com/images/3/36/Lebanon.png"),
   "LBA" : ("Libya", "https://hoi4.paradoxwikis.com/images/4/45/Libya.png"),
   "LBV" : ("Lombardy-Venetia", "https://i.imgur.com/MWYmgso.png"),
   "MAC" : ("Macedonia", "https://hoi4.paradoxwikis.com/images/d/d2/Macedonia.png"),
   "MAD" : ("Madagascar", "https://hoi4.paradoxwikis.com/images/b/b3/Republic_of_Madagascar.png"),
   "MLW" : ("Malawi", "https://hoi4.paradoxwikis.com/images/0/08/Malawi.png"),
   "MLD" : ("Maldives", "https://hoi4.paradoxwikis.com/images/a/aa/Maldives.png"),
   "MLI" : ("Mali", "https://hoi4.paradoxwikis.com/images/f/f0/Mali.png"),
   "MLT" : ("Malta", "https://hoi4.paradoxwikis.com/images/1/10/Malta.png"),
   "MEL" : ("Mari El", "https://hoi4.paradoxwikis.com/images/c/cb/Mari_El.png"),
   "GUM" : ("Mariana Federation", "https://hoi4.paradoxwikis.com/images/4/44/Mariana_Federation.png"),
   "MRT" : ("Mauritania", "https://hoi4.paradoxwikis.com/images/f/f2/Mauritania.png"),
   "MEK" : ("Mecklenburg", "https://hoi4.paradoxwikis.com/images/7/74/Grand_Duchy_of_Mecklenburg.png"), # Small img
   "FIJ" : ("Fiji", "https://hoi4.paradoxwikis.com/images/2/2f/Melanesian_Federation.png"),
   "FSM" : ("Micronesia", "https://hoi4.paradoxwikis.com/images/0/03/Federated_States_of_Micronesia.png"),
   "MOL" : ("Moldova", "https://hoi4.paradoxwikis.com/images/3/3b/Moldova.png"),
   "MNT" : ("Montenegro", "https://hoi4.paradoxwikis.com/images/c/cd/Republic_of_Montenegro.png"),
   "MOR" : ("Morocco", "https://hoi4.paradoxwikis.com/images/7/7f/Kingdom_of_Morocco.png"),
   "MZB" : ("Mozambique", "https://hoi4.paradoxwikis.com/images/1/19/Mozambique.png"),
   "NMB" : ("Namibia", "https://hoi4.paradoxwikis.com/images/c/ce/Namibia.png"),
   "NEN" : ("Nenetsia", "https://hoi4.paradoxwikis.com/images/6/6e/Nenetsia.png"),
   "CRC" : ("Netherlands Antilles", "https://hoi4.paradoxwikis.com/images/4/46/Netherlands_Antilles.png"),
   "NGR" : ("Niger", "https://hoi4.paradoxwikis.com/images/7/72/Niger.png"),
   "NGA" : ("Nigeria", "https://hoi4.paradoxwikis.com/images/5/59/Nigeria.png"),
   "NIR" : ("Northern Ireland", "https://hoi4.paradoxwikis.com/images/1/12/Northern_Ireland.png"),
   "NOA" : ("North Ossetia-Alania", "https://hoi4.paradoxwikis.com/images/e/ea/North_Ossetia-Alania.png"),
   "OCC" : ("Occitania", "https://hoi4.paradoxwikis.com/images/a/a9/Occitania.png"),
   "ORO" : ("Oromia", "https://hoi4.paradoxwikis.com/images/e/e9/Oromia.png"),
   "OVO" : ("Ostyak Vogulia", "https://hoi4.paradoxwikis.com/images/d/d9/Ostyak-Vogul_National_Republic.png"),
   "PAK" : ("Pakistan", "https://hoi4.paradoxwikis.com/images/f/f3/Pakistan.png"),
   "PAL" : ("Palestine", "https://hoi4.paradoxwikis.com/images/1/1e/Palestine.png"),
   "PAP" : ("Papal States", "https://hoi4.paradoxwikis.com/images/f/f0/Papal_States.png"),
   "PNG" : ("Papua New Guinea", "https://hoi4.paradoxwikis.com/images/e/ed/Papua_New_Guinea.png"),
   "PRE" : ("Prussia", "https://i.imgur.com/huWWo2P.png"),
   "PUE" : ("Puerto Rico", "https://hoi4.paradoxwikis.com/images/8/87/Puerto_Rico.png"),
   "QAT" : ("Qatar", "https://hoi4.paradoxwikis.com/images/0/00/Republic_of_Qatar.png"),
   "QEM" : ("Qemant State", "https://hoi4.paradoxwikis.com/images/0/06/Qemant_State.png"),
   "RIF" : ("Rif", "https://hoi4.paradoxwikis.com/images/6/60/Republic_of_the_Rif.png"),
   "RWA" : ("Rwanda", "https://hoi4.paradoxwikis.com/images/8/8a/Rwanda.png"), # Small img
   "WES" : ("Western Sahara", "https://hoi4.paradoxwikis.com/images/8/88/Sahrawi_Arab_Democratic_Republic.png"),
   "YAK" : ("Sakha Republic", "https://hoi4.paradoxwikis.com/images/3/39/Sakha_Republic.png"),
   "SAM" : ("Samoa", "https://hoi4.paradoxwikis.com/images/4/45/Independent_State_of_Samoa.png"),
   "SPM" : ("Sardinia-Piedmont", "https://hoi4.paradoxwikis.com/images/2/22/Sardinia-Piedmont.png"),
   "SAX" : ("Saxony", "https://hoi4.paradoxwikis.com/images/0/0a/Kingdom_of_Saxony.png"),
   "SHL" : ("Schleswig-Holstein", "https://hoi4.paradoxwikis.com/images/6/61/Duchy_of_Schleswig-Holstein.png"), # Small img
   "SCO" : ("Scotland", "https://hoi4.paradoxwikis.com/images/2/27/Scotland.png"),
   "SEN" : ("Senegal", "https://hoi4.paradoxwikis.com/images/2/22/Senegal.png"),
   "SER" : ("Serbia", "https://hoi4.paradoxwikis.com/images/7/76/Serbia.png"),
   "SID" : ("Sidamo", "https://hoi4.paradoxwikis.com/images/8/87/Kingdom_of_Sidamo.png"), # Small img
   "SIE" : ("Sierra Leone", "https://hoi4.paradoxwikis.com/images/b/bc/Kingdom_of_Sierra_Leone.png"),
   "SIL" : ("Silesia", "https://hoi4.paradoxwikis.com/images/f/f7/Silesia.png"),
   "SLO" : ("Slovakia", "https://hoi4.paradoxwikis.com/images/8/89/Slovakia.png"),
   "SLV" : ("Slovenia", "https://hoi4.paradoxwikis.com/images/3/32/Slovenia.png"),
   "SOL" : ("Solomon Islands", "https://hoi4.paradoxwikis.com/images/1/19/Solomon_Islands.png"),
   "SOM" : ("Somalia", "https://i.imgur.com/HY1DG2G.png"), # Small img
   "SRL" : ("Sri Lanka", "https://hoi4.paradoxwikis.com/images/6/64/Democratic_Socialist_Republic_of_Sri_Lanka.png"),
   "SUD" : ("Sudan", "https://hoi4.paradoxwikis.com/images/3/38/Sudan.png"),
   "SUR" : ("Suriname", "https://hoi4.paradoxwikis.com/images/c/c9/Republic_of_Suriname.png"),
   "SYR" : ("Syria", "https://hoi4.paradoxwikis.com/images/0/0f/Syria.png"),
   "TAH" : ("Tahiti", "https://hoi4.paradoxwikis.com/images/0/0c/Tahiti.png"),
   "TAJ" : ("Tajikistan", "https://hoi4.paradoxwikis.com/images/c/cf/Republic_of_Tajikistan.png"),
   "TZN" : ("Tanzania", "https://hoi4.paradoxwikis.com/images/6/61/Tanzania.png"),
   "TAT" : ("Tatarstan", "https://hoi4.paradoxwikis.com/images/b/ba/Tatarstan.png"),
   "TAY" : ("Taymyria", "https://hoi4.paradoxwikis.com/images/e/e1/Taymyria.png"),
   "TIG" : ("Tigray", "https://hoi4.paradoxwikis.com/images/8/86/Tigray.png"),
   "TOG" : ("Togo", "https://hoi4.paradoxwikis.com/images/9/98/Togo.png"),
   "TRA" : ("Transylvania", "https://hoi4.paradoxwikis.com/images/8/8f/Transylvania.png"),
   "TRI" : ("Trinidad and Tobago", "https://hoi4.paradoxwikis.com/images/d/d7/Republic_of_Trinidad_and_Tobago.png"),
   "TUN" : ("Tunisia", "https://hoi4.paradoxwikis.com/images/0/08/Tunisia.png"),
   "TMS" : ("Turkmenistan", "https://hoi4.paradoxwikis.com/images/b/b6/Republic_of_Turkmenistan.png"),
   "TOS" : ("Tuscany", "https://hoi4.paradoxwikis.com/images/c/c2/Grand_Duchy_of_Tuscany.png"), # Small img
   "TTS" : ("Two Sicilies", "https://i.imgur.com/9bm3H1Z.png"),
   "UDM" : ("Udmurtia", "https://hoi4.paradoxwikis.com/images/5/53/Udmurtia.png"),
   "UGA" : ("Uganda", "https://hoi4.paradoxwikis.com/images/4/4c/Uganda.png"),
   "UKR" : ("Ukraine", "https://hoi4.paradoxwikis.com/images/1/1a/Ukraine.png"),
   "USB" : ("Unaligned States of America", ""), # Missing
   "UAE" : ("United Arab Emirates", "https://hoi4.paradoxwikis.com/images/6/66/United_Arab_Emirates.png"),
   "VOL" : ("Upper Volta", "https://hoi4.paradoxwikis.com/images/b/b8/Upper_Volta.png"),
   "UZB" : ("Uzbekistan", "https://hoi4.paradoxwikis.com/images/2/29/Republic_of_Uzbekistan.png"),
   "VIN" : ("Vietnam", "https://hoi4.paradoxwikis.com/images/9/93/Republic_of_Vietnam.png"),
   "VLA" : ("Vladivostok", "https://hoi4.paradoxwikis.com/images/6/65/Vladivostok_Independent_Republic.png"),
   "VGE" : ("Volga Germany", "https://hoi4.paradoxwikis.com/images/f/f4/Republic_of_Volga_Germany.png"),
   "WLS" : ("Wales", "https://hoi4.paradoxwikis.com/images/d/d9/Wales.png"),
   "WGR" : ("West Germany", "https://hoi4.paradoxwikis.com/images/c/cc/West_Germany.png"),
   "HAN" : ("Westphalia", "https://i.imgur.com/lBbQxjP.png"),
   "WUR" : ("Wurtemberg", "https://hoi4.paradoxwikis.com/images/0/0d/Kingdom_of_Wurtemberg.png"), # Small img
   "YAM" : ("Yamalia", "https://hoi4.paradoxwikis.com/images/6/64/Yamalian_Republic.png"),
   "COG" : ("Zaire", "https://hoi4.paradoxwikis.com/images/5/55/Zaire.png"),
   "ZAM" : ("Zambia", "https://hoi4.paradoxwikis.com/images/a/ad/Zambia.png"),
   "ZIM" : ("Zimbabwe", "https://hoi4.paradoxwikis.com/images/5/57/Zimbabwe.png")

}
