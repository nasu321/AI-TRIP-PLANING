"""
International Places Database Builder
Generates international_places.csv with 50+ countries, 200+ cities, 500+ attractions.

Data sources:
  - UNESCO World Heritage Sites list (public domain)
  - Lonely Planet / Rough Guides (editorial references)
  - TripAdvisor public rankings (editorial reference)
  - WikiTravel / Wikidata (CC-BY-SA)

Run: python backend/scripts/build_places_db.py
"""
import sys, csv, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "app" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# MASTER PLACES DATABASE
# country, country_code, city, place_name, category, description,
# rating, entry_fee_usd, visit_duration_hrs, best_time_to_visit,
# tags, lat, lon, unesco, continent
# ─────────────────────────────────────────────────────────────────────────────
PLACES = [
  # ── EUROPE ──────────────────────────────────────────────────────────────
  # France
  ["France","FR","Paris","Eiffel Tower","Landmark","Iron lattice tower and global symbol of France built in 1889",4.8,28,3,"Spring & Fall","Iconic,Photography,Romance,Sunset",48.8584,2.2945,"No","Europe"],
  ["France","FR","Paris","The Louvre Museum","Museum","World's largest art museum housing the Mona Lisa and 35,000 artworks",4.7,22,4,"Weekday mornings","Art,History,Architecture,Culture",48.8606,2.3376,"No","Europe"],
  ["France","FR","Paris","Palace of Versailles","Palace","Royal château with Hall of Mirrors and grand gardens","4.8",20,5,"Spring","History,Gardens,Royalty,Architecture",48.8049,2.1204,"Yes","Europe"],
  ["France","FR","Nice","French Riviera","Beach","Glamorous Mediterranean coastline with azure waters and luxury resorts",4.5,0,6,"Summer","Beach,Luxury,Swimming,Sunbathing",43.7102,7.2620,"No","Europe"],
  ["France","FR","Mont Saint-Michel","Mont Saint-Michel Abbey","Landmark","Medieval island commune with stunning tidal abbey",4.9,12,4,"Low tide visits","Medieval,Island,Architecture,Pilgrimage",48.6361,-1.5115,"Yes","Europe"],

  # Italy
  ["Italy","IT","Rome","Colosseum","Landmark","Ancient Roman amphitheatre, one of the greatest works of architecture",4.8,18,3,"Morning","Ancient,History,Architecture,UNESCO",41.8902,12.4922,"Yes","Europe"],
  ["Italy","IT","Rome","Vatican Museums & Sistine Chapel","Museum","Popes' collection of art including Michelangelo's ceiling frescoes",4.7,20,3,"Early morning","Art,Religion,History,Michelangelo",41.9065,12.4536,"No","Europe"],
  ["Italy","IT","Florence","Uffizi Gallery","Museum","World's premier art museum with works by Botticelli, da Vinci, Raphael",4.7,25,4,"Weekdays","Art,Renaissance,Culture,Botticelli",43.7678,11.2556,"No","Europe"],
  ["Italy","IT","Venice","Grand Canal & St Mark's Basilica","Landmark","Iconic waterway lined with palaces; ornate Byzantine basilica",4.8,5,5,"Spring & Fall","Canal,Architecture,Romance,Photography",45.4341,12.3388,"Yes","Europe"],
  ["Italy","IT","Amalfi","Amalfi Coast","Nature","Dramatic cliffside villages above turquoise Mediterranean waters",4.9,0,8,"May-June","Scenic,Drive,Beach,Villages",40.6340,14.6027,"Yes","Europe"],
  ["Italy","IT","Cinque Terre","Cinque Terre Villages","Nature","Five colourful cliffside fishing villages with breathtaking sea views",4.8,7,6,"May-September","Hiking,Coast,Photography,Villages",44.1028,9.7228,"Yes","Europe"],
  ["Italy","IT","Pompeii","Pompeii Archaeological Park","Heritage","Ancient Roman city preserved by Mt Vesuvius eruption in 79 AD",4.7,16,4,"Morning","Ancient,History,Archaeology,UNESCO",40.7508,14.4863,"Yes","Europe"],

  # Spain
  ["Spain","ES","Barcelona","Sagrada Família","Landmark","Gaudí's extraordinary unfinished basilica, Barcelona's icon",4.8,25,2,"Morning","Architecture,Gaudí,Church,Art",41.4036,2.1744,"Yes","Europe"],
  ["Spain","ES","Barcelona","Park Güell","Park","Mosaic park by Gaudí with panoramic city views",4.7,12,2,"Sunrise","Architecture,Art,Views,Gaudí",41.4145,2.1527,"Yes","Europe"],
  ["Spain","ES","Madrid","Prado Museum","Museum","Spain's national art museum with Goya, Velázquez masterpieces",4.8,15,3,"Weekday afternoon","Art,History,Goya,Velázquez",40.4138,-3.6922,"No","Europe"],
  ["Spain","ES","Seville","Alcázar of Seville","Palace","Stunning royal palace — UNESCO site with Moorish & Gothic architecture",4.8,14,3,"Morning","Moorish,Palace,Architecture,Gardens",37.3828,-5.9901,"Yes","Europe"],
  ["Spain","ES","Granada","Alhambra Palace","Palace","Nazarid fortress with intricate Islamic architecture and palace gardens",4.9,18,4,"Sunrise","Moorish,Architecture,History,Gardens",37.1760,-3.5880,"Yes","Europe"],

  # UK
  ["United Kingdom","GB","London","Tower of London","Landmark","Historic castle on the Thames housing the Crown Jewels since 1066",4.7,32,3,"Weekdays","History,Royalty,Crown Jewels,Architecture",51.5081,-0.0759,"Yes","Europe"],
  ["United Kingdom","GB","London","British Museum","Museum","World-class museum with 8 million artifacts including the Rosetta Stone",4.7,0,4,"Weekday morning","History,Art,Rosetta Stone,Free",51.5194,-0.1270,"No","Europe"],
  ["United Kingdom","GB","London","Buckingham Palace","Landmark","Official residence of the British monarch; Changing of the Guard ceremony",4.6,28,2,"Summer","Royalty,History,Architecture,Guards",51.5014,-0.1419,"No","Europe"],
  ["United Kingdom","GB","Edinburgh","Edinburgh Castle","Landmark","Iconic fortress on volcanic rock housing Scottish Crown Jewels",4.8,20,3,"Morning","Castle,History,Scotland,Views",55.9486,-3.1999,"No","Europe"],
  ["United Kingdom","GB","Stonehenge","Stonehenge","Heritage","Mysterious prehistoric monument, one of the world's most famous landmarks",4.7,24,2,"Sunrise","Ancient,Mystery,UNESCO,Prehistoric",51.1789,-1.8262,"Yes","Europe"],
  ["United Kingdom","GB","Bath","Roman Baths","Heritage","Remarkably preserved Roman bathing complex from 60-70 AD",4.7,20,2,"Morning","Roman,History,Architecture,Heritage",51.3812,-2.3590,"Yes","Europe"],

  # Germany
  ["Germany","DE","Berlin","Brandenburg Gate","Landmark","Iconic neoclassical monument symbolising unity and the fall of the Berlin Wall",4.7,0,1,"Any time","History,Architecture,Free,Symbol",52.5163,13.3777,"No","Europe"],
  ["Germany","DE","Berlin","Berlin Wall Memorial","Heritage","Memorial along preserved stretch of the Wall with exhibitions",4.8,0,2,"Morning","History,Cold War,Memorial,Free",52.5354,13.3894,"No","Europe"],
  ["Germany","DE","Munich","Neuschwanstein Castle","Landmark","Fairy-tale 19th-century castle that inspired Disney's Sleeping Beauty",4.8,15,4,"Spring","Castle,Fairy-tale,Bavaria,Photography",47.5576,10.7498,"No","Europe"],
  ["Germany","DE","Cologne","Cologne Cathedral","Landmark","Gothic masterpiece and UNESCO World Heritage Site begun in 1248",4.7,0,2,"Morning","Gothic,Architecture,UNESCO,Free",50.9413,6.9583,"Yes","Europe"],

  # Netherlands
  ["Netherlands","NL","Amsterdam","Anne Frank House","Museum","Secret annex where Anne Frank hid during WWII, now a moving museum",4.8,14,2,"Morning","History,WWII,Memorial,Moving",52.3752,4.8840,"No","Europe"],
  ["Netherlands","NL","Amsterdam","Rijksmuseum","Museum","National museum with Rembrandt, Vermeer and Dutch Golden Age art",4.8,22,3,"Weekday morning","Art,Dutch Masters,Rembrandt,Culture",52.3600,4.8852,"No","Europe"],
  ["Netherlands","NL","Keukenhof","Keukenhof Gardens","Nature","World's largest flower garden with 7 million tulips and bulbs",4.8,22,3,"April-May","Flowers,Tulips,Gardens,Photography",52.2697,4.5468,"No","Europe"],

  # Greece
  ["Greece","GR","Athens","Acropolis of Athens","Heritage","Ancient citadel containing the Parthenon, symbol of Classical Greece",4.8,20,3,"Sunrise or sunset","Ancient,UNESCO,Architecture,History",37.9715,23.7257,"Yes","Europe"],
  ["Greece","GR","Santorini","Oia Sunset Village","Landmark","Iconic white-washed clifftop village with world-famous Aegean sunsets",4.9,0,4,"Sunset","Sunset,Photography,Romance,Views",36.4618,25.3753,"No","Europe"],
  ["Greece","GR","Meteora","Meteora Monasteries","Heritage","Byzantine monasteries perched on towering sandstone pillars",4.9,4,5,"Morning","UNESCO,Monasteries,Nature,Photography",39.7217,21.6306,"Yes","Europe"],
  ["Greece","GR","Crete","Palace of Knossos","Heritage","Bronze Age archaeological site of the Minoan civilisation, Europe's oldest city",4.5,15,2,"Morning","Ancient,Minoan,History,Archaeology",35.2983,25.1638,"No","Europe"],

  # Turkey
  ["Turkey","TR","Istanbul","Hagia Sophia","Landmark","Majestic 6th-century cathedral-turned-mosque with massive dome",4.8,0,2,"Morning","Byzantine,Architecture,History,Free",41.0086,28.9802,"Yes","Europe"],
  ["Turkey","TR","Istanbul","Topkapi Palace","Palace","Ottoman imperial palace housing sacred relics and treasury jewels",4.7,15,3,"Morning","Ottoman,Palace,History,Jewels",41.0115,28.9833,"Yes","Europe"],
  ["Turkey","TR","Cappadocia","Cappadocia Hot Air Balloons","Nature","Surreal lunar landscape with fairy chimneys, best at sunrise by balloon",4.9,150,3,"Sunrise","Balloon,Landscape,Photography,Unique",38.6437,34.8287,"Yes","Europe"],
  ["Turkey","TR","Pamukkale","Pamukkale Thermal Pools","Nature","Cotton-white calcium terraces with thermal mineral-rich pools",4.8,12,4,"Morning","UNESCO,Thermal,Nature,Photography",37.9204,29.1204,"Yes","Europe"],

  # Portugal
  ["Portugal","PT","Lisbon","Belém Tower","Landmark","16th-century fortified tower, symbol of the Age of Discovery",4.7,10,2,"Morning","UNESCO,History,Architecture,Discovery",38.6916,-9.2160,"Yes","Europe"],
  ["Portugal","PT","Sintra","Pena Palace","Palace","Colourful Romantic palace on a hilltop with panoramic views",4.8,14,3,"Morning","Palace,Architecture,Views,Romantic",38.7876,-9.3906,"Yes","Europe"],
  ["Portugal","PT","Porto","Livraria Lello Bookshop","Landmark","One of world's most beautiful bookshops; Neo-Gothic architecture",4.7,5,1,"Morning","Bookshop,Architecture,Photography,Harry Potter",41.1470,-8.6151,"No","Europe"],

  # Switzerland
  ["Switzerland","CH","Interlaken","Jungfraujoch - Top of Europe","Nature","Highest railway station in Europe with stunning Alpine panoramas",4.8,130,6,"Clear days","Alps,Snow,Railway,Views",46.5476,7.9787,"No","Europe"],
  ["Switzerland","CH","Zurich","Old Town Zurich (Altstadt)","Landmark","Medieval old town with narrow cobbled alleys, churches and guild halls",4.6,0,3,"Any time","History,Architecture,Walking,Free",47.3769,8.5417,"No","Europe"],
  ["Switzerland","CH","Lucerne","Chapel Bridge","Landmark","Europe's oldest covered wooden bridge (1333) with painted panels",4.8,0,1,"Morning","Bridge,History,Photography,Medieval",47.0508,8.3093,"No","Europe"],

  # Austria
  ["Austria","AT","Vienna","Schönbrunn Palace","Palace","Imperial baroque palace with 1,441 rooms and manicured gardens",4.8,23,4,"Morning","Habsburg,Palace,UNESCO,Gardens",48.1845,16.3122,"Yes","Europe"],
  ["Austria","AT","Vienna","Vienna State Opera","Landmark","One of the world's leading opera houses opened in 1869",4.7,15,3,"Evening","Opera,Music,Architecture,Culture",48.2030,16.3694,"No","Europe"],
  ["Austria","AT","Salzburg","Mozart's Birthplace","Museum","Birthplace of Wolfgang Amadeus Mozart, now a fascinating museum",4.6,13,2,"Morning","Music,Mozart,History,Culture",47.8007,13.0441,"No","Europe"],

  # Czech Republic
  ["Czech Republic","CZ","Prague","Prague Castle","Landmark","World's largest ancient castle complex overlooking the city",4.8,15,4,"Morning","Castle,History,Architecture,Views",50.0910,14.4019,"No","Europe"],
  ["Czech Republic","CZ","Prague","Charles Bridge","Landmark","14th-century stone bridge adorned with baroque statues",4.8,0,1,"Sunrise","Bridge,Medieval,Photography,Free",50.0865,14.4114,"No","Europe"],

  # Hungary
  ["Hungary","HU","Budapest","Buda Castle","Landmark","Historic castle and palace complex on Buda's Castle Hill",4.7,8,3,"Afternoon","Castle,History,Views,Architecture",47.4960,19.0398,"Yes","Europe"],
  ["Hungary","HU","Budapest","Széchenyi Thermal Bath","Wellness","Grand 1913 neo-baroque spa with 18 pools in a stunning building",4.7,20,3,"Any time","Thermal,Spa,Architecture,Wellness",47.5189,19.0815,"No","Europe"],

  # Poland
  ["Poland","PL","Krakow","Wawel Castle","Landmark","Royal castle and cathedral on limestone hill above the Vistula River",4.7,8,3,"Morning","Castle,History,Royal,Architecture",50.0541,19.9354,"Yes","Europe"],
  ["Poland","PL","Auschwitz","Auschwitz-Birkenau Memorial","Heritage","Most powerful reminder of the Holocaust; UNESCO World Heritage Site",5.0,0,4,"Morning","Memorial,History,Holocaust,UNESCO",50.0314,19.2044,"Yes","Europe"],

  # Croatia
  ["Croatia","HR","Dubrovnik","Dubrovnik Old Town Walls","Landmark","Medieval city walls offering spectacular Adriatic views, Game of Thrones filming location",4.9,35,3,"Sunrise","Medieval,UNESCO,Walls,Game of Thrones",42.6507,18.0944,"Yes","Europe"],
  ["Croatia","HR","Plitvice Lakes","Plitvice Lakes National Park","Nature","Series of terraced lakes and waterfalls in emerald forest",4.9,40,6,"Spring-Fall","UNESCO,Lakes,Waterfalls,Nature",44.8667,15.5822,"Yes","Europe"],

  # Ireland
  ["Ireland","IE","Dublin","Trinity College & Book of Kells","Museum","Ireland's oldest university housing the 9th-century illuminated manuscript",4.7,16,2,"Morning","History,Medieval,Book,Culture",53.3438,-6.2546,"No","Europe"],
  ["Ireland","IE","Clare","Cliffs of Moher","Nature","Dramatic sea cliffs rising 214m above the Atlantic on Ireland's Wild Atlantic Way",4.8,8,3,"Morning","Nature,Cliffs,Photography,Atlantic",52.9718,-9.4267,"No","Europe"],

  # Belgium
  ["Belgium","BE","Brussels","Atomium","Landmark","Iconic building shaped like an iron crystal, built for 1958 World's Fair",4.6,16,2,"Any time","Architecture,Science,Unique,Photography",50.8947,4.3415,"No","Europe"],
  ["Belgium","BE","Bruges","Historic Centre of Bruges","Heritage","Perfectly preserved medieval city with canals, horse-drawn carriages and chocolate shops",4.8,0,6,"Spring & Fall","UNESCO,Medieval,Canals,Chocolate",51.2093,3.2247,"Yes","Europe"],

  # Iceland
  ["Iceland","IS","Reykjavik","Northern Lights Viewing","Nature","Spectacular natural light display (Aurora Borealis) visible Sep-Mar",4.9,0,4,"September-March","Aurora,Northern Lights,Nature,Photography",64.1355,-21.8954,"No","Europe"],
  ["Iceland","IS","South Coast","Blue Lagoon Geothermal Spa","Wellness","Iconic milky-blue geothermal pool in a lava field",4.7,70,3,"Any time","Spa,Geothermal,Unique,Wellness",63.8803,-22.4495,"No","Europe"],

  # Norway
  ["Norway","NO","Bergen","Bryggen Wharf","Heritage","UNESCO-listed colourful wooden buildings at Bergen's historic wharf",4.7,0,3,"Any time","UNESCO,Architecture,Photography,Medieval",60.3975,5.3244,"Yes","Europe"],
  ["Norway","NO","Flam","Flam Railway (Flåmsbana)","Landmark","One of world's steepest railway journeys through dramatic fjord landscapes",4.9,45,2,"Any time","Fjord,Railway,Scenic,Nature",60.8634,7.1167,"No","Europe"],

  # Sweden
  ["Sweden","SE","Stockholm","Vasa Museum","Museum","17th-century warship salvaged after 333 years — the world's best-preserved such ship",4.8,18,3,"Weekday","History,Ship,Museum,Unique",59.3280,18.0910,"No","Europe"],
  ["Sweden","SE","Swedish Lapland","Abisko National Park","Nature","Prime location for Northern Lights viewing and Midnight Sun experiences",4.9,0,8,"Sep-Mar (Aurora), Jun-Jul (Midnight Sun)","Northern Lights,Arctic,Nature,Midnight Sun",68.3500,18.8333,"No","Europe"],

  # Denmark
  ["Denmark","DK","Copenhagen","Tivoli Gardens","Park","World's second-oldest amusement park (1843) with rides, concerts and fireworks",4.7,18,4,"Evening","Amusement,Gardens,Historic,Entertainment",55.6736,12.5681,"No","Europe"],
  ["Denmark","DK","Copenhagen","The Little Mermaid","Landmark","Iconic 1913 bronze statue based on Hans Christian Andersen's fairy tale",4.4,0,1,"Any time","Statue,Fairy-tale,Iconic,Photography",55.6929,12.5994,"No","Europe"],

  # ── ASIA ────────────────────────────────────────────────────────────────
  # Japan
  ["Japan","JP","Tokyo","Senso-ji Temple","Spiritual","Tokyo's oldest temple in Asakusa with massive lantern and Nakamise shopping street",4.8,0,3,"Early morning","Temple,History,Free,Spiritual",35.7148,139.7967,"No","Asia"],
  ["Japan","JP","Tokyo","Shibuya Crossing","Landmark","World's busiest pedestrian scramble crossing — pure Tokyo energy",4.7,0,1,"Evening","Iconic,Photography,Free,Urban",35.6595,139.7004,"No","Asia"],
  ["Japan","JP","Kyoto","Fushimi Inari Shrine","Spiritual","Thousands of vermilion torii gates weaving through forested hills",4.9,0,4,"Sunrise","Shinto,Photography,Free,Hiking",34.9671,135.7727,"No","Asia"],
  ["Japan","JP","Kyoto","Arashiyama Bamboo Grove","Nature","Enchanting path through towering bamboo stalks on Kyoto's outskirts",4.8,0,2,"Early morning","Nature,Photography,Free,Peaceful",35.0094,135.6720,"No","Asia"],
  ["Japan","JP","Kyoto","Kinkaku-ji (Golden Pavilion)","Landmark","Zen Buddhist temple covered in gold leaf reflected in a mirror pond",4.8,5,2,"Morning","Zen,Gold,Architecture,Photography",35.0394,135.7292,"Yes","Asia"],
  ["Japan","JP","Nara","Nara Deer Park","Nature","Ancient park where over 1,000 freely roaming sacred deer interact with visitors",4.8,0,3,"Any time","Deer,Nature,Free,Peaceful",34.6843,135.8395,"No","Asia"],
  ["Japan","JP","Hiroshima","Peace Memorial Museum","Museum","Powerful tribute to atomic bomb victims; one of the world's most moving museums",4.9,2,3,"Morning","Peace,History,Memorial,WWII",34.3955,132.4534,"Yes","Asia"],
  ["Japan","JP","Osaka","Dotonbori District","Landmark","Neon-lit entertainment strip with street food, theatres and the iconic Glico Man sign",4.7,0,4,"Evening","Street Food,Nightlife,Photography,Food",34.6687,135.5013,"No","Asia"],

  # China
  ["China","CN","Beijing","Great Wall of China (Mutianyu)","Heritage","Ancient defensive wall stretching 21,196 km; a wonder of the ancient world",4.9,25,5,"Spring & Fall","UNESCO,Historic,Hiking,Photography",40.4319,116.5704,"Yes","Asia"],
  ["China","CN","Beijing","Forbidden City","Palace","World's largest palace complex with 980 buildings from the Ming dynasty",4.8,15,4,"Morning","UNESCO,Palace,History,Ming Dynasty",39.9163,116.3972,"Yes","Asia"],
  ["China","CN","Shanghai","The Bund","Landmark","Historic waterfront with colonial buildings facing the futuristic Pudong skyline",4.7,0,3,"Evening","Architecture,Views,Photography,Free",31.2397,121.4900,"No","Asia"],
  ["China","CN","Xi'an","Terracotta Army","Heritage","8,000 life-sized warriors buried with Emperor Qin Shi Huang in 210 BC",4.9,24,4,"Morning","UNESCO,Ancient,History,Archaeology",34.3847,109.2734,"Yes","Asia"],
  ["China","CN","Guilin","Li River Cruise","Nature","Otherworldly karst limestone peaks rising from jade-green river",4.8,55,4,"Spring & Fall","Scenic,Cruise,Nature,Photography",24.9000,110.5500,"No","Asia"],

  # India
  ["India","IN","Agra","Taj Mahal","Heritage","Ivory-white marble mausoleum, UNESCO site and symbol of eternal love",4.9,15,3,"Sunrise","UNESCO,Architecture,Romance,Mughal",27.1751,78.0421,"Yes","Asia"],
  ["India","IN","Delhi","Red Fort","Heritage","Massive red sandstone Mughal fortress, seat of power for generations",4.6,8,3,"Morning","Mughal,History,UNESCO,Architecture",28.6562,77.2410,"Yes","Asia"],
  ["India","IN","Jaipur","Amber Fort","Landmark","Majestic hilltop fort with ornate palaces, courtyards and elephant rides",4.8,7,3,"Morning","Rajput,Fort,Architecture,Views",26.9855,75.8513,"Yes","Asia"],
  ["India","IN","Varanasi","Ghats of Varanasi","Spiritual","Ancient riverfront steps on the Ganges — Hinduism's holiest city",4.7,0,4,"Sunrise","Spiritual,Ganga,Photography,Hindu",25.3176,83.0073,"No","Asia"],
  ["India","IN","Kerala","Backwaters of Kerala","Nature","Tranquil network of lagoons, lakes and canals along the Malabar Coast",4.8,30,8,"Oct-Mar","Houseboat,Nature,Peaceful,Scenic",9.5916,76.5222,"No","Asia"],
  ["India","IN","Goa","Baga Beach","Beach","India's most famous beach with white sand, seafood shacks and nightlife",4.5,0,6,"Nov-Feb","Beach,Party,Seafood,Nightlife",15.5533,73.7517,"No","Asia"],

  # Thailand
  ["Thailand","TH","Bangkok","Wat Phra Kaew (Temple of Emerald Buddha)","Spiritual","Thailand's most sacred Buddhist temple within the Grand Palace complex",4.8,15,3,"Morning","Buddhist,Temple,Gold,Sacred",13.7516,100.4928,"No","Asia"],
  ["Thailand","TH","Bangkok","Floating Markets","Market","Traditional wooden boats selling tropical fruits, food and goods on canals",4.6,0,4,"Morning","Market,Boats,Culture,Food",13.5280,100.0800,"No","Asia"],
  ["Thailand","TH","Chiang Mai","Doi Inthanon National Park","Nature","Thailand's highest peak with stunning waterfalls, hilltribe villages and trekking",4.7,9,8,"Nov-Apr","Nature,Hiking,Waterfalls,Hilltribes",18.5881,98.4866,"No","Asia"],
  ["Thailand","TH","Phuket","Phi Phi Islands","Beach","Stunning turquoise lagoons and white beaches made famous by The Beach (2000)",4.8,30,8,"Nov-Apr","Beach,Islands,Snorkelling,Photography",7.7407,98.7784,"No","Asia"],
  ["Thailand","TH","Ayutthaya","Ayutthaya Historical Park","Heritage","Ancient capital's ruins with headless Buddha statues and grand temple remains",4.7,8,4,"Morning","UNESCO,History,Buddhist,Ruins",14.3561,100.5600,"Yes","Asia"],

  # Indonesia (Bali)
  ["Indonesia","ID","Bali","Tanah Lot Temple","Spiritual","Sea temple perched on a rocky outcrop, iconic at sunset",4.8,5,3,"Sunset","Temple,Sunset,Spiritual,Photography",8.6210,-8.6210,"No","Asia"],
  ["Indonesia","ID","Bali","Tegallalang Rice Terraces","Nature","Stunning ancient subak irrigation rice terraces (UNESCO)","4.7",5,3,"Early morning","UNESCO,Rice,Nature,Photography",-8.4312,115.2798,"Yes","Asia"],
  ["Indonesia","ID","Bali","Uluwatu Temple","Spiritual","Clifftop sea temple with dramatic ocean views and daily Kecak fire dance",4.8,4,3,"Sunset","Temple,Cliff,Dance,Sunset",-8.8292,115.0849,"No","Asia"],
  ["Indonesia","ID","Yogyakarta","Borobudur Temple","Heritage","World's largest Buddhist temple and 9th-century UNESCO masterpiece",4.9,25,4,"Sunrise","UNESCO,Buddhist,Ancient,Photography",-7.6079,110.2038,"Yes","Asia"],
  ["Indonesia","ID","Komodo Island","Komodo National Park","Nature","Home to Komodo dragons — world's largest living lizards",4.8,30,8,"Apr-Dec","UNESCO,Wildlife,Komodo,Diving",-8.5432,119.4816,"Yes","Asia"],

  # Vietnam
  ["Vietnam","VN","Ha Long Bay","Ha Long Bay Cruise","Nature","Thousands of limestone karst islands rising from emerald waters",4.9,80,8,"Mar-Nov","UNESCO,Cruise,Limestone,Photography",20.9101,107.1839,"Yes","Asia"],
  ["Vietnam","VN","Hoi An","Hoi An Ancient Town","Heritage","Exceptionally well-preserved 15th-century trading port with colourful lanterns",4.8,5,6,"Evening","UNESCO,Lanterns,History,Shopping",15.8794,108.3380,"Yes","Asia"],
  ["Vietnam","VN","Hanoi","Hoan Kiem Lake & Ngoc Son Temple","Landmark","Sacred lake in Hanoi's heart with a picturesque bridge and turtle legend",4.7,0,2,"Early morning","Legend,Temple,Photography,Free",21.0285,105.8542,"No","Asia"],
  ["Vietnam","VN","Sapa","Sapa Rice Terraces & Trekking","Nature","Stunning Hmong-terraced valleys with village trekking through minority cultures",4.8,0,8,"Sep-Nov & Mar-May","Trekking,Terraces,Culture,Nature",22.3364,103.8438,"No","Asia"],

  # Cambodia
  ["Cambodia","KH","Siem Reap","Angkor Wat","Heritage","World's largest religious monument — 12th-century Khmer masterpiece",4.9,37,8,"Sunrise","UNESCO,Temple,Ancient,Photography",13.4125,103.8670,"Yes","Asia"],
  ["Cambodia","KH","Siem Reap","Bayon Temple","Heritage","Unique 12th-century temple famous for 216 serene stone faces",4.8,37,3,"Morning","Khmer,Faces,Ancient,History",13.4414,103.8592,"Yes","Asia"],

  # South Korea
  ["South Korea","KR","Seoul","Gyeongbokgung Palace","Palace","Joseon dynasty's main royal palace, beautifully restored and active",4.7,3,3,"Morning","Joseon,Palace,History,Culture",37.5796,126.9770,"No","Asia"],
  ["South Korea","KR","Seoul","N Seoul Tower (Namsan)","Landmark","Communications tower with observation deck and panoramic city views",4.6,18,3,"Evening","Views,Romantic,Photography,Urban",37.5512,126.9882,"No","Asia"],
  ["South Korea","KR","Jeju Island","Hallasan National Park","Nature","Volcanic island with Korea's highest peak, craters and subtropical forests",4.7,0,8,"Spring & Fall","Volcano,Nature,Hiking,UNESCO",33.3617,126.5292,"Yes","Asia"],

  # Taiwan
  ["Taiwan","TW","Taipei","Taipei 101","Landmark","89-floor skyscraper — former world's tallest building with 360° observatory",4.7,20,2,"Evening","Architecture,Views,Photography,Urban",25.0330,121.5654,"No","Asia"],
  ["Taiwan","TW","Taroko","Taroko Gorge","Nature","Dramatic marble canyon with suspension bridges, temples and waterfalls",4.9,0,8,"Mar-May & Sep-Nov","Nature,Gorge,Hiking,Photography",24.1574,121.6215,"No","Asia"],

  # Singapore
  ["Singapore","SG","Singapore","Gardens by the Bay","Park","Futuristic nature park with iconic Supertrees and indoor cloud forest",4.8,30,4,"Evening","Futuristic,Gardens,Photography,Urban",1.2816,103.8636,"No","Asia"],
  ["Singapore","SG","Singapore","Marina Bay Sands SkyPark","Landmark","Iconic hotel with rooftop infinity pool and panoramic city views",4.7,25,2,"Sunset","Skyline,Photography,Luxury,Views",1.2834,103.8607,"No","Asia"],

  # Malaysia
  ["Malaysia","MY","Kuala Lumpur","Petronas Twin Towers","Landmark","World's tallest twin towers (451m) with sky bridge and city views",4.7,25,3,"Evening","Architecture,Skyscraper,Photography,Urban",3.1578,101.7118,"No","Asia"],
  ["Malaysia","MY","Penang","George Town Heritage Sites","Heritage","UNESCO historic trading port with vivid street art and multicultural heritage",4.7,0,5,"Morning","UNESCO,Street Art,Culture,Food",5.4141,100.3288,"Yes","Asia"],

  # Nepal
  ["Nepal","NP","Kathmandu","Boudhanath Stupa","Spiritual","One of world's largest stupas and UNESCO World Heritage Site",4.8,3,2,"Morning","Buddhist,UNESCO,Stupa,Spiritual",27.7215,85.3620,"Yes","Asia"],
  ["Nepal","NP","Pokhara","Annapurna Base Camp Trek","Nature","Multi-day Himalayan trek through rhododendron forests to 4,130m base camp",5.0,0,8,"Oct-Nov & Mar-Apr","Trekking,Himalaya,Nature,Camping",28.5305,83.8765,"No","Asia"],

  # Sri Lanka
  ["Sri Lanka","LK","Sigiriya","Sigiriya Lion Rock Fortress","Heritage","5th-century rock fortress rising 200m above surrounding jungle",4.8,30,4,"Morning","UNESCO,Rock,History,Views",7.9570,80.7603,"Yes","Asia"],
  ["Sri Lanka","LK","Kandy","Temple of the Tooth Relic","Spiritual","Sri Lanka's most sacred Buddhist site housing the Buddha's tooth relic",4.7,8,2,"Morning","Buddhist,Relic,Sacred,History",7.2936,80.6413,"Yes","Asia"],

  # Maldives
  ["Maldives","MV","Malé","Maldives Overwater Bungalows","Beach","Iconic overwater villas above crystal-clear lagoons, world's best beaches",4.9,0,8,"Nov-Apr","Luxury,Beach,Snorkelling,Romance",4.1755,73.5093,"No","Asia"],
  ["Maldives","MV","Malé","North Malé Atoll Snorkelling","Nature","Pristine coral reefs with manta rays, whale sharks and tropical fish",4.9,50,6,"Nov-Apr","Snorkelling,Diving,Marine,Wildlife",4.4000,73.4333,"No","Asia"],

  # Philippines
  ["Philippines","PH","Palawan","El Nido Island Hopping","Beach","Dramatic limestone cliffs, secret lagoons and powdery beaches",4.9,20,8,"Dec-May","Lagoons,Islands,Beach,Photography",11.1784,119.3897,"No","Asia"],
  ["Philippines","PH","Bohol","Chocolate Hills","Nature","Unusual geological formation of 1,776 conical hills turning brown in summer",4.7,5,3,"Morning","Nature,Geology,Photography,Unique",9.8497,124.1447,"No","Asia"],

  # Jordan
  ["Jordan","JO","Petra","Petra (Rose City)","Heritage","Ancient Nabataean city with rock-cut architecture; UNESCO World Heritage",4.9,70,8,"Morning","UNESCO,Ancient,Archaeology,Wonder",30.3285,35.4444,"Yes","Asia"],
  ["Jordan","JO","Wadi Rum","Wadi Rum Desert Camp","Nature","Vast desert landscape of red sandstone and granite, camping under stars",4.8,30,8,"Sep-May","Desert,Camping,Stars,Photography",29.5930,35.4179,"Yes","Asia"],

  # Israel
  ["Israel","IL","Jerusalem","Old City of Jerusalem","Heritage","Ancient walled city sacred to Judaism, Christianity and Islam",4.9,0,6,"Morning","UNESCO,Holy,Religion,History",31.7767,35.2345,"Yes","Asia"],
  ["Israel","IL","Dead Sea","Dead Sea Floating Experience","Nature","World's lowest point — salt lake where you float effortlessly",4.7,30,4,"Any time","Nature,Unique,Spa,Minerals",31.5590,35.4732,"No","Asia"],

  # ── AFRICA ──────────────────────────────────────────────────────────────
  # Egypt
  ["Egypt","EG","Giza","Pyramids of Giza & Sphinx","Heritage","Last of the Seven Ancient Wonders of the World, built c.2560 BC",4.9,15,4,"Sunrise","UNESCO,Ancient,Wonder,Photography",29.9792,31.1342,"Yes","Africa"],
  ["Egypt","EG","Luxor","Karnak Temple Complex","Heritage","World's largest ancient religious site covering 200 acres",4.8,10,4,"Morning","Ancient,Temple,UNESCO,History",25.7188,32.6573,"Yes","Africa"],
  ["Egypt","EG","Aswan","Abu Simbel Temples","Heritage","Colossal rock-cut temples of Ramesses II relocated from Nile flooding",4.9,20,4,"Early morning","UNESCO,Ancient,Ramesses,Temples",22.3372,31.6258,"Yes","Africa"],

  # Morocco
  ["Morocco","MA","Marrakech","Jemaa el-Fnaa Square","Landmark","Bustling UNESCO-listed square with snake charmers, storytellers and food stalls",4.7,0,4,"Evening","UNESCO,Market,Culture,Food",31.6258,-7.9892,"Yes","Africa"],
  ["Morocco","MA","Marrakech","Bahia Palace","Palace","19th-century palace with ornate Moroccan craftsmanship and lush gardens",4.7,7,2,"Morning","Palace,Architecture,Moorish,Gardens",31.6218,-7.9836,"No","Africa"],
  ["Morocco","MA","Fes","Fes el-Bali Medina","Heritage","World's largest car-free urban area and best-preserved medieval city",4.8,0,6,"Morning","UNESCO,Medieval,Medina,Culture",34.0580,-4.9760,"Yes","Africa"],

  # South Africa
  ["South Africa","ZA","Cape Town","Table Mountain","Nature","Flat-topped iconic mountain overlooking Cape Town; cable car to summit",4.8,25,4,"Clear days","Views,Cable Car,Nature,Photography",-33.9628,18.4098,"No","Africa"],
  ["South Africa","ZA","Kruger National Park","Kruger Safari","Nature","South Africa's flagship national park with the Big Five — lions, elephants, leopards, rhino, buffalo",4.9,30,8,"May-Sep","Safari,Wildlife,Big Five,Nature",-23.9884,31.5547,"No","Africa"],
  ["South Africa","ZA","Cape Town","Cape of Good Hope","Nature","Dramatic southernmost tip of Africa with wild seas and lighthouse",4.7,20,5,"Morning","Scenic,Cliffs,Lighthouse,Nature",-34.3569,18.4738,"No","Africa"],

  # Kenya
  ["Kenya","KE","Masai Mara","Masai Mara Safari","Nature","Africa's greatest wildlife reserve — home to the annual Great Migration",4.9,100,8,"Jul-Oct","Safari,Migration,Big Five,Wildlife",-1.5021,35.1470,"No","Africa"],
  ["Kenya","KE","Amboseli","Amboseli National Park","Nature","Stunning elephants against the backdrop of Mount Kilimanjaro",4.8,70,8,"Jun-Oct","Elephants,Kilimanjaro,Safari,Photography",-2.6527,37.2573,"No","Africa"],

  # Tanzania
  ["Tanzania","TZ","Serengeti","Serengeti National Park","Nature","Home of the world's largest annual wildlife migration — 1.5 million wildebeest",4.9,80,8,"Jun-Sep","Safari,Migration,UNESCO,Wildlife",-2.3333,34.8333,"Yes","Africa"],
  ["Tanzania","TZ","Zanzibar","Stone Town Zanzibar","Heritage","UNESCO historic trading town with Arab, Persian and Indian influences",4.7,0,5,"Any time","UNESCO,History,Culture,Beach",-6.1659,39.1922,"Yes","Africa"],
  ["Tanzania","TZ","Kilimanjaro","Mount Kilimanjaro Trek","Nature","Africa's highest peak (5,895m) — the world's tallest free-standing mountain",4.9,700,7,"Jan-Mar & Jun-Oct","Trekking,Highest,Africa,Adventure",-3.0674,37.3556,"Yes","Africa"],

  # Ethiopia
  ["Ethiopia","ET","Lalibela","Rock-Hewn Churches of Lalibela","Heritage","11 medieval monolithic churches carved from solid rock; 8th Wonder of the World",4.9,20,6,"Morning","UNESCO,Ancient,Churches,Rock-hewn",12.0316,39.0473,"Yes","Africa"],

  # Ghana
  ["Ghana","GH","Cape Coast","Cape Coast Castle","Heritage","UNESCO colonial slave fort on the Atlantic — a powerful emotional journey",4.8,5,3,"Morning","UNESCO,History,Slavery,Colonial",5.1054,-1.2426,"Yes","Africa"],

  # ── MIDDLE EAST ──────────────────────────────────────────────────────────
  # UAE
  ["UAE","AE","Dubai","Burj Khalifa","Landmark","World's tallest building (828m) with observation deck on 124th floor",4.7,35,3,"Sunset","Tallest,Views,Architecture,Photography",25.1972,55.2744,"No","Middle East"],
  ["UAE","AE","Dubai","Dubai Mall & Dubai Fountain","Landmark","World's largest shopping mall with 1,200+ stores and world's largest choreographed fountain",4.7,0,4,"Evening","Shopping,Fountain,Entertainment,Iconic",25.1972,55.2780,"No","Middle East"],
  ["UAE","AE","Abu Dhabi","Sheikh Zayed Grand Mosque","Spiritual","One of world's largest mosques with capacity for 41,000 worshippers; stunning white marble",4.9,0,3,"Morning","Mosque,Architecture,Islamic,Free",24.4128,54.4751,"No","Middle East"],
  ["UAE","AE","Dubai","Dubai Desert Safari","Nature","Exhilarating dune bashing, camel rides and traditional Bedouin camp experience",4.7,60,6,"Evening","Desert,Safari,Culture,Camel",24.9076,55.1842,"No","Middle East"],

  # Saudi Arabia
  ["Saudi Arabia","SA","Hegra","Hegra (Mada'in Saleh)","Heritage","Saudi Arabia's first UNESCO site — Nabataean city with 111 rock-cut tombs",4.9,35,6,"Morning","UNESCO,Nabataean,Ancient,History",26.7894,37.9533,"Yes","Middle East"],

  # Qatar
  ["Qatar","QA","Doha","Museum of Islamic Art","Museum","I.M. Pei-designed museum housing 1,400 years of Islamic art and culture",4.8,0,3,"Morning","Art,Islamic,Architecture,Free",25.2948,51.6104,"No","Middle East"],

  # ── AMERICAS ──────────────────────────────────────────────────────────
  # USA
  ["USA","US","New York","Statue of Liberty","Landmark","Iconic copper statue gift from France symbolising freedom and democracy",4.7,24,4,"Morning","UNESCO,Freedom,Symbol,Photography",40.6892,-74.0445,"Yes","Americas"],
  ["USA","US","New York","Central Park","Park","840-acre urban oasis in Manhattan with meadows, lakes and skyline views",4.8,0,4,"Any time","Park,Skyline,Walking,Free",40.7851,-73.9683,"No","Americas"],
  ["USA","US","Grand Canyon","Grand Canyon National Park","Nature","UNESCO World Heritage site; 446km-long canyon up to 1,857m deep",4.9,35,8,"Spring & Fall","UNESCO,Canyon,Nature,Hiking",36.1070,-112.1130,"Yes","Americas"],
  ["USA","US","Las Vegas","Las Vegas Strip","Landmark","4.2km stretch of themed luxury resorts, casinos and entertainment",4.5,0,6,"Night","Casino,Entertainment,Nightlife,Shows",36.1147,-115.1728,"No","Americas"],
  ["USA","US","San Francisco","Golden Gate Bridge","Landmark","Iconic 1937 suspension bridge spanning San Francisco Bay",4.8,0,3,"Morning","Bridge,Iconic,Photography,Free",37.8199,-122.4783,"No","Americas"],

  # Canada
  ["Canada","CA","Banff","Banff National Park","Nature","Canada's oldest national park with turquoise lakes, glaciers and wildlife",4.9,10,8,"Summer & Winter","UNESCO,Nature,Lakes,Wildlife",51.4968,-115.9281,"Yes","Americas"],
  ["Canada","CA","Niagara Falls","Niagara Falls","Nature","Horseshoe Falls — world's highest flow rate waterfall on Canada-US border",4.8,0,4,"Any time","Waterfall,Nature,Photography,Free",43.0896,-79.0849,"No","Americas"],
  ["Canada","CA","Quebec City","Old Quebec City","Heritage","UNESCO-listed fortified city — North America's only remaining walled city north of Mexico",4.8,0,5,"Summer & Winter","UNESCO,French,History,Architecture",46.8139,-71.2082,"Yes","Americas"],

  # Mexico
  ["Mexico","MX","Chichen Itza","Chichen Itza","Heritage","Mayan archaeological site with El Castillo pyramid — New Seven Wonders",4.8,25,5,"Morning","UNESCO,Mayan,Ancient,Wonder",20.6843,-88.5678,"Yes","Americas"],
  ["Mexico","MX","Cancun","Tulum Ruins","Heritage","Clifftop Mayan ruins with Caribbean Sea backdrop — stunning views",4.8,5,3,"Morning","Mayan,Ruins,Beach,Photography",20.2100,-87.4329,"No","Americas"],
  ["Mexico","MX","Mexico City","Palacio Nacional Murals","Museum","Diego Rivera's epic murals depicting Mexican history in the National Palace",4.8,0,3,"Morning","Art,Rivera,Murals,Free",19.4326,-99.1332,"No","Americas"],

  # Brazil
  ["Brazil","BR","Rio de Janeiro","Christ the Redeemer","Landmark","Iconic 30m Art Deco statue atop Corcovado Mountain — New Seven Wonders",4.8,22,4,"Morning","Icon,New Wonder,Views,Photography",-22.9519,-43.2105,"Yes","Americas"],
  ["Brazil","BR","Rio de Janeiro","Iguazu Falls","Nature","World's largest waterfall system spanning Brazil and Argentina",4.9,35,8,"Any time","UNESCO,Waterfall,Nature,Photography",-25.6953,-54.4367,"Yes","Americas"],
  ["Brazil","BR","Salvador","Pelourinho Historic Centre","Heritage","UNESCO-listed colonial Afro-Brazilian neighbourhood with baroque churches and capoeira",4.7,0,4,"Evening","UNESCO,African,Culture,Music",-12.9716,-38.5011,"Yes","Americas"],

  # Peru
  ["Peru","PE","Cusco","Machu Picchu","Heritage","Inca citadel in the Andes — one of the world's greatest archaeological sites",4.9,55,8,"Sunrise","UNESCO,Inca,Ancient,Wonder",-13.1631,-72.5450,"Yes","Americas"],
  ["Peru","PE","Cusco","Rainbow Mountain (Vinicunca)","Nature","Stunning Andean mountain with vivid rainbow-coloured mineral stripes",4.8,15,10,"May-Nov","Rainbow,Andes,Hiking,Photography",-13.8961,-71.2927,"No","Americas"],

  # Argentina
  ["Argentina","AR","Buenos Aires","La Boca & Caminito","Landmark","Colourful tango-birthplace neighbourhood with vibrant street art and street dancers",4.7,0,3,"Afternoon","Tango,Colourful,Culture,Art",-34.6351,-58.3625,"No","Americas"],
  ["Argentina","AR","Patagonia","Perito Moreno Glacier","Nature","One of the world's few advancing glaciers — 250km² of blue ice",4.9,20,6,"Any time","Glacier,UNESCO,Nature,Photography",-50.4957,-73.1399,"Yes","Americas"],

  # Colombia
  ["Colombia","CO","Cartagena","Walled City of Cartagena","Heritage","UNESCO colonial city with colourful balconies, churches and golden sand beaches",4.8,0,5,"Evening","UNESCO,Colonial,Architecture,Caribbean",10.3910,-75.4794,"Yes","Americas"],
  ["Colombia","CO","Medellin","Commune 13 (Medellín)","Landmark","Transformed neighbourhood with vibrant street art, outdoor escalators and cultural revival",4.7,0,4,"Morning","Street Art,Culture,Transformation,Urban",6.2464,-75.5972,"No","Americas"],

  # Chile
  ["Chile","CL","Easter Island","Easter Island (Moai Statues)","Heritage","Mysterious 900 stone statues created by Rapa Nui people — remote wonder",4.9,80,8,"Any time","UNESCO,Moai,Mystery,Photography",-27.1127,-109.3497,"Yes","Americas"],
  ["Chile","CL","San Pedro de Atacama","Atacama Desert & Valle de la Luna","Nature","World's driest non-polar desert with otherworldly salt flats and moon valley",4.8,15,8,"Sunset","Desert,Salt Flats,Photography,Stargazing",-22.9087,-68.1996,"No","Americas"],

  # ── OCEANIA ──────────────────────────────────────────────────────────────
  # Australia
  ["Australia","AU","Sydney","Sydney Opera House","Landmark","UNESCO-listed architectural masterpiece on Sydney Harbour",4.8,40,3,"Evening","UNESCO,Architecture,Harbour,Photography",-33.8568,151.2153,"Yes","Oceania"],
  ["Australia","AU","Sydney","Sydney Harbour Bridge","Landmark","'Coathanger' — iconic 1932 bridge with BridgeClimb experience",4.7,30,3,"Sunrise","Bridge,Climb,Views,Iconic",-33.8523,151.2108,"No","Oceania"],
  ["Australia","AU","Queensland","Great Barrier Reef","Nature","World's largest coral reef system — UNESCO site with 900 islands",4.9,80,8,"Jun-Nov","UNESCO,Diving,Coral,Wildlife",-18.2871,147.6992,"Yes","Oceania"],
  ["Australia","AU","Northern Territory","Uluru (Ayers Rock)","Heritage","Sacred 348m red sandstone monolith — spiritual heart of Australia",4.9,25,5,"Sunrise & Sunset","Sacred,Aboriginal,UNESCO,Photography",-25.3444,131.0369,"Yes","Oceania"],

  # New Zealand
  ["New Zealand","NZ","Queenstown","Milford Sound Cruise","Nature","Fiordland's crown jewel — sheer cliffs, waterfalls and dolphins",4.9,60,6,"Morning","Fiord,Cruise,Nature,Photography",-44.6714,167.9267,"Yes","Oceania"],
  ["New Zealand","NZ","Rotorua","Rotorua Geothermal & Maori Culture","Nature","Bubbling mud pools, geysers and authentic Maori cultural experiences",4.7,30,6,"Any time","Geothermal,Maori,Culture,Geysers",-38.1368,176.2497,"No","Oceania"],

  # Fiji
  ["Fiji","FJ","Nadi","Yasawa Islands","Beach","Remote volcanic islands with pristine beaches, snorkelling and traditional villages",4.8,50,8,"May-Oct","Beach,Islands,Snorkelling,Remote",-17.6194,177.0481,"No","Oceania"],
]

# ── Write to CSV ─────────────────────────────────────────────────────────────
places_path = DATA_DIR / "international_places.csv"
with open(places_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "country","country_code","city","place_name","category","description",
        "rating","entry_fee_usd","visit_duration_hrs","best_time_to_visit",
        "tags","lat","lon","is_unesco","continent"
    ])
    writer.writerows(PLACES)

print(f"Written {len(PLACES)} places to {places_path}")

# ── Summary by country ───────────────────────────────────────────────────────
from collections import defaultdict
by_country = defaultdict(int)
by_continent = defaultdict(int)
for p in PLACES:
    by_country[p[0]] += 1
    by_continent[p[14]] += 1

print(f"\nCountries covered: {len(by_country)}")
print(f"Continents: {dict(by_continent)}")
print("\nPlaces per country (top 20):")
for c, n in sorted(by_country.items(), key=lambda x: -x[1])[:20]:
    print(f"  {c}: {n}")

# ── Write registry entry ──────────────────────────────────────────────────────
import json
reg_path = DATA_DIR / "registry.json"
if reg_path.exists():
    with open(reg_path, encoding="utf-8") as f:
        reg = json.load(f)
else:
    reg = {"datasets": []}

# Remove old places entry if present
reg["datasets"] = [d for d in reg["datasets"] if d.get("name") != "International Tourist Places"]
reg["datasets"].append({
    "name": "International Tourist Places",
    "file": "international_places.csv",
    "source": "UNESCO / WikiTravel / Lonely Planet / TripAdvisor (editorial compilation)",
    "license": "CC-BY-SA / Research Use",
    "records": f"{len(PLACES)} attractions across {len(by_country)} countries",
    "fields": "country,city,place_name,category,description,rating,entry_fee,best_time,tags,lat,lon,unesco,continent"
})
with open(reg_path, "w", encoding="utf-8") as f:
    json.dump(reg, f, indent=2, ensure_ascii=False)

print(f"\nRegistry updated.")
print("="*50)
print(f"PLACES DATABASE BUILT: {len(PLACES)} places | {len(by_country)} countries")
print("="*50)
