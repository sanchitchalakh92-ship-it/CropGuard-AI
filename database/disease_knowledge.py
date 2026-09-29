"""
CropGuard AI - Disease Knowledge Base

Standalone disease information module for the model's crop/disease classes.
Import DISEASE_KNOWLEDGE from this file in recommendations.py.

Important:
- The ML model predicts the class; this module supplies explanatory information.
- Broad classes such as Groundnut|Leaf Disease and Ladyfinger (Okra)|Leaf Disease
  intentionally tell the user to confirm the exact disease before selecting a
  disease-specific pesticide.
- Chemical guidance intentionally avoids invented doses/brands. Use products
  registered for the crop/disease in the user's jurisdiction and follow the label.
"""

DISEASE_KNOWLEDGE = {
    'Brinjal|Bacterial Wilt': {
        'description': 'A devastating vascular bacterial disease of eggplant/brinjal that induces rapid, irreversible wilting and vascular browning without prior leaf yellowing, leading to complete plant death within days.',
        'cause': 'Ralstonia solanacearum (bacterial pathogen); highly persistent in soil, favored by high soil temperatures (28-35°C), excess soil moisture, and poor drainage.',
        'symptoms': [
            'Sudden wilting of leaves during warm sunny hours with temporary recovery at night',
            'Leaves remain green or dull green while wilting without prominent chlorosis',
            'Progressive, irreversible whole-plant collapse within 3 to 5 days',
            'Dark brown discoloration of vascular bundles visible upon slicing lower stems',
            'White milky bacterial streaming emerges when infected stem cuts are placed in clean water'
        ],
        'spread': [
            'Infested soil and infected seedling nursery stock',
            'Contaminated irrigation water and surface run-off',
            'Nematode feeding wounds and mechanical root injuries during transplanting or weeding',
            'Contaminated farm implements, footwear, and cultivating machinery'
        ],
        'management': [
            'Rogue and carefully excavate severely wilted plants with roots and surrounding soil; dispose away from fields',
            'Drench planting spots of infected plants with copper oxychloride or bleaching powder solution as per local agricultural recommendations',
            'Avoid cultivating or disturbing soil around infected plant beds to prevent root tearing and disease spread',
            'Improve field drainage and construct raised planting beds to avoid water pooling around root zones'
        ],
        'prevention': [
            'Practice 3 to 4-year crop rotation with non-solanaceous crops (maize, sorghum, rice, or millets)',
            'Plant certified wilt-resistant or grafted eggplant cultivars (e.g., grafted onto Solanum torvum rootstock)',
            'Solarize nursery soil using clear polyethylene sheets for 4 to 6 weeks before sowing',
            'Apply bio-antagonists such as Pseudomonas fluorescens or Bacillus subtilis to seedling roots at transplanting'
        ],
        'urgency': 'High'
    },
    'Brinjal|Cercospora Leaf Spot': {
        'description': 'A common foliar fungal infection of brinjal causing necrotic leaf lesions with concentric rings, leading to premature defoliation, reduced photosynthesis, and sun-scalded fruits.',
        'cause': 'Cercospora melongenae (fungus); favored by warm, humid tropical weather (25-30°C) with relative humidity above 85% and prolonged leaf wetness.',
        'symptoms': [
            'Small, circular to irregular chlorotic spots on older lower leaves initially',
            'Lesions expand into tan or brown spots with greyish-white necrotic centers and dark margins',
            'Concentric rings may develop within older lesions giving a target-board look',
            'Extensive coalescing of spots causing severe leaf yellowing, drying, and premature shedding',
            'Exposed developing fruits suffer from sun-scald and stunted fruit sizing'
        ],
        'spread': [
            'Airborne conidia dispersed by wind currents and turbulent air',
            'Water splash from heavy rainfall or overhead sprinkler irrigation',
            'Overwintering mycelia and conidia on infected crop residues and weed hosts'
        ],
        'management': [
            'Prune and collect heavily spotted lower leaves; destroy them to decrease field inoculum',
            'Avoid working in fields or harvesting when plant foliage is wet to avoid spreading spores',
            'Apply registered protectant or systemic fungicides (e.g., Mancozeb, Chlorothalonil, or Carbendazim) at the onset of lesions as labeled',
            'Spray biological formulations like Trichoderma harzianum or neem seed kernel extract (5%) preventively'
        ],
        'prevention': [
            'Adopt wide plant-to-plant spacing (60x60 cm) to ensure adequate air circulation and rapid canopy drying',
            'Switch from overhead sprinkler systems to drip or furrow irrigation',
            'Clear field borders of volunteer solanaceous weeds (e.g., black nightshade)',
            'Rotate with non-host crops like cereals and legumes for at least two seasons'
        ],
        'urgency': 'Medium'
    },
    'Brinjal|Little Leaf Disease': {
        'description': 'A serious phytoplasma disease of brinjal causing severe hormonal disruption, proliferation of tiny leaves, shortened internodes, bushy appearance, and complete reproductive sterility.',
        'cause': 'Phytoplasma (Candidatus Phytoplasma sp.); transmitted persistently by the leafhopper vector Hishimonus phycitis; favored by warm dry seasons that promote vector reproduction.',
        'symptoms': [
            'Extreme reduction in leaf lamina size, turning leaves into tiny, soft, pale green scales',
            'Severe shortening of petioles and internodes causing excessive axillary shoot sprouting',
            'Plants take on a highly compact, bunched, witches-broom or bushy appearance',
            'Floral parts transform into green vegetative leaf-like structures (phyllody)',
            'Total failure of fruit set; any existing fruits remain small, hard, and unmarketable'
        ],
        'spread': [
            'Primary transmission by phloem-feeding leafhoppers (Hishimonus phycitis)',
            'Infected nursery seedlings and vegetative grafting material',
            'Reservoir weed hosts (such as Datura stramonium, Solanum xanthocarpum, and Cannabis sativa)'
        ],
        'management': [
            'Uproot and burn infected bushy plants immediately upon detection to remove virus source',
            'Monitor leafhopper populations using yellow sticky traps placed at canopy height (10-12 traps/acre)',
            'Spray approved systemic insecticides (such as Dimethoate, Thiamethoxam, or Imidacloprid) according to regional agricultural extension guidelines to control leafhopper vectors',
            'Spray neem-based formulations (Azadirachtin 1500 ppm) to deter vector feeding and oviposition'
        ],
        'prevention': [
            'Eradicate solanaceous and perennial weeds around nursery beds and field boundaries',
            'Raise seedlings under protective insect-proof nylon nets (40-50 mesh) until transplanting',
            'Select tolerant varieties recommended by local agricultural universities',
            'Avoid planting next to aging, abandoned brinjal or potato fields'
        ],
        'urgency': 'High'
    },
    'Brinjal|Phomopsis Blight': {
        'description': 'A destructive fungal disease attacking all aerial parts of brinjal, causing circular leaf spots, stem cankers, collar rot, and devastating soft fruit rots that render harvests unmarketable.',
        'cause': 'Phomopsis vexans (Diaporthe vexans, fungus); seed-borne and residue-borne; favored by warm temperatures (28-32°C), high humidity, and intermittent rainfall.',
        'symptoms': [
            'Circular to irregular brown lesions with light grey centers on leaves, bearing minute black pycnidia',
            'Dark brown to black sunken cankers at the collar region of seedlings, causing seedling damping-off',
            'Stem lesions that can girdle branches, causing sudden dieback and lodging',
            'Water-soaked, pale brown sunken spots on fruits that rapidly expand into large soft rotting areas',
            'Mummified rotting fruits covered with concentric rings of black pycnidia dotting the skin'
        ],
        'spread': [
            'Internally and externally seed-borne in infected brinjal seeds',
            'Splashing rainwater and overhead sprinkler droplets distributing pycnidiospores',
            'Contaminated harvest tools and post-harvest handling crates',
            'Mycelia surviving in decaying crop debris in the soil'
        ],
        'management': [
            'Hand-pick and safely bury infected fruits and blighted twigs; never leave them on the ground',
            'Apply recommended protective fungicides like Mancozeb, Copper oxychloride, or Azoxystrobin following product label recommendations and pre-harvest intervals',
            'Avoid overhead spraying or harvesting during wet periods to minimize spore detachment',
            'Dip seedling roots in Trichoderma viride suspension before transplanting'
        ],
        'prevention': [
            'Source certified disease-free seed; perform hot water seed treatment (50°C for 30 minutes) or seed dressing with Thiram/Carbendazim',
            'Adopt 3-year crop rotations with non-solanaceous crops',
            'Maintain wider row spacing to facilitate rapid foliage drying after rains',
            'Grow resistant varieties (e.g., cultivars bred with Phomopsis resistance by regional research stations)'
        ],
        'urgency': 'Medium'
    },
    'Cabbage|Black Root': {
        'description': 'A soil-borne fungal/oomycete disease that attacks cabbage roots and lower hypocotyls, producing black necrotic taproot decay, severe stunting, nutrient deprivation, and poor head formation.',
        'cause': 'Aphanomyces raphani (or Rhizoctonia/Fusarium complex affecting brassica root systems); favored by cold to moderately warm waterlogged soils and poorly drained seedbeds.',
        'symptoms': [
            'Dark brown to jet-black necrotic discoloration of the primary taproot and secondary lateral roots',
            'Root cortex becomes soft, water-soaked, or brittle, sloughing off easily',
            'Above-ground leaves turn chlorotic, dull purplish, or wilt during midday heat',
            'Severe stunting of cabbage plants with delayed or completely absent head formation',
            'Seedlings in seedbeds damp off or develop wirestem-like constrictions at soil level'
        ],
        'spread': [
            'Oospores surviving in infested soil for multiple years',
            'Movement of contaminated soil on farm implements, boots, and runoff water',
            'Infected nursery transplants planted into clean production fields'
        ],
        'management': [
            'Carefully dig out and destroy stunted, severely root-blackened plants',
            'Improve soil drainage immediately by cutting deep drainage furrows to discharge standing water',
            'Drench nursery beds or plant bases with approved fungicides (e.g., Metalaxyl-Mancozeb or Copper oxychloride) where registered',
            'Apply organic compost enriched with Trichoderma harzianum to suppress soil-borne oospores'
        ],
        'prevention': [
            'Construct raised nursery beds with well-drained, solarized sandy loam soil',
            'Rotate cabbage fields with non-brassica crops (corn, legumes, cereals) for at least 3-4 years',
            'Ensure proper field grading to prevent waterlogging during monsoon or heavy irrigations',
            'Sanitize machinery and tillage tools before moving between farm plots'
        ],
        'urgency': 'High'
    },
    'Cabbage|Alternaria Leaf Spot': {
        'description': 'A prominent fungal foliar disease of cabbage that forms circular target-like necrotic lesions on leaves and wrapper leaves, degrading commercial head quality and seed yields.',
        'cause': 'Alternaria brassicae and Alternaria brassicicola (fungi); seed-borne and air-borne; favored by warm temperatures (20-28°C) accompanied by heavy dew, rainfall, or high relative humidity.',
        'symptoms': [
            'Small circular yellowish-brown spots appearing first on older lower leaves',
            'Spots enlarge with distinct concentric rings creating a target-board pattern',
            'Lesions become covered with dark brown to olivaceous velvety fungal spores in damp weather',
            'Severely infected leaves turn yellow, senesce prematurely, and drop off',
            'Black speckling and blemishes develop on mature cabbage wrapper leaves, spoiling head marketability'
        ],
        'spread': [
            'Airborne fungal conidia blown across long distances by wind',
            'Rain splash and mechanical movement through wet crops',
            'Contaminated seed coats and overwintering spores on brassica debris and wild mustard weeds'
        ],
        'management': [
            'Strip and compost/destroy severely affected outer wrapper leaves',
            'Avoid overhead sprinkler irrigation; irrigate early in the morning so foliage dries quickly',
            'Apply registered foliar fungicides such as Mancozeb, Iprodione, Chlorothalonil, or Azoxystrobin at threshold levels according to label instructions',
            'Spray bio-fungicides like Bacillus subtilis or neem oil formulations early in the disease cycle'
        ],
        'prevention': [
            'Use certified pathogen-free seeds; treat seed with hot water (50°C for 25 minutes) before sowing',
            'Practice minimum 3-year crop rotation avoiding cauliflower, broccoli, radish, and mustard',
            'Plow under or destroy crop residues immediately after harvest to accelerate debris decomposition',
            'Ensure wide plant spacing for optimum canopy aeration'
        ],
        'urgency': 'Medium'
    },
    'Cabbage|Downy Mildew': {
        'description': 'A widespread oomycete disease of cabbage that produces angular yellow leaf lesions with white-grey downy fungal felt on leaf undersides, severely impacting seedling survival and mature head quality.',
        'cause': 'Hyaloperonospora brassicae (syn. Peronospora parasitica, oomycete); favored by cool temperatures (10-18°C), high humidity (>90%), and prolonged canopy leaf wetness.',
        'symptoms': [
            'Pale green to bright yellow angular chlorotic patches on upper leaf surfaces bounded by leaf veins',
            'Fluffy white to purplish-grey downy growth directly underneath the yellow patches on lower leaf surfaces',
            'Lesions turn tan to dark brown with age, causing leaf papery drying and shedding',
            'Seedling cotyledons and early leaves turn yellow and drop, causing seedling death in nurseries',
            'Black internal flecking and speckling inside cabbage heads during cold storage or transit'
        ],
        'spread': [
            'Wind-borne sporangia carried over kilometers during cool, overcast, moist mornings',
            'Splashing rainwater and overhead irrigation',
            'Thick-walled oospores persisting in brassica residues and contaminated seed'
        ],
        'management': [
            'Rogue heavily infected nursery seedlings before transplanting into main fields',
            'Ventilate greenhouse/polyhouse nurseries to lower relative humidity below 80%',
            'Apply targeted downy-mildew registered fungicides (e.g., Metalaxyl-Mancozeb, Fosetyl-Al, Cymoxanil, or Copper Hydroxide) adhering to label doses and safety periods',
            'Switch completely away from evening overhead irrigation'
        ],
        'prevention': [
            'Plant tolerant or resistant hybrid cabbage varieties suited to cool humid seasons',
            'Space plants adequately to facilitate wind movement throughout the crop canopy',
            'Treat seeds with systemic fungicides or hot water prior to planting',
            'Eradicate cruciferous weeds like wild turnip, shepherd’s purse, and wild mustard'
        ],
        'urgency': 'High'
    },
    'Cabbage|Fusarium Yellows': {
        'description': 'A systemic vascular wilt disease of cabbage characterized by one-sided leaf yellowing, lateral head warping, vascular browning, and gradual plant decline.',
        'cause': 'Fusarium oxysporum f. sp. conglutinans (fungus); soil-borne pathogen producing long-lived chlamydospores; favored by warm soil temperatures (24-30°C).',
        'symptoms': [
            'Characteristic asymmetric or one-sided yellowing of leaves or half of the plant',
            'Affected leaves twist, curl sideways, turn brown, and drop prematurely from the bottom up',
            'Stunted, lopsided head development with poor compacting',
            'Distinct yellowish-brown to dark ring of vascular discoloration visible when the stem is cut crosswise',
            'Whole plant wilts and dies under warm afternoon sun conditions'
        ],
        'spread': [
            'Chlamydospores persisting in soil for 10 to 15 years without host crops',
            'Transfer of infested soil via tractors, rototillers, animal hooves, and transplant trays',
            'Irrigation run-off draining from infested fields into uninfected plots'
        ],
        'management': [
            'Remove and destroy symptomatic plants to minimize secondary root zone accumulation',
            'Do not cultivate infested soil into adjacent healthy brassica plots',
            'Apply bio-fungicides like Trichoderma viride or Trichoderma harzianum mixed with farmyard manure into planting pits',
            'Note: Chemical fungicides are generally ineffective against established vascular Fusarium wilt'
        ],
        'prevention': [
            'Grow cabbage varieties with Type A genetic resistance (monogenic dominant resistance to yellows)',
            'Implement long-term crop rotation (minimum 4-5 years) with non-cruciferous crops (cereals, alliums, legumes)',
            'Maintain neutral to slightly alkaline soil pH (6.5-7.0) using agricultural lime',
            'Solarize nursery beds with clear UV-resistant plastic film before sowing'
        ],
        'urgency': 'High'
    },
    'Cabbage|Clubroot': {
        'description': 'A devastating soil-borne protist disease that causes massive, distorted, club-shaped galls on cabbage roots, severely choking water uptake and causing severe wilting and stunting.',
        'cause': 'Plasmodiophora brassicae (obligate biotrophic protist); favored by acidic soils (pH < 6.5), warm soil temperatures (20-25°C), and waterlogged soil conditions.',
        'symptoms': [
            'Characteristic club-shaped, spindle-like, or spherical swollen galls on primary and lateral roots',
            'Root galls rot, crack, and release foul odor as secondary microbes invade',
            'Foliage wilts severely on warm sunny days and temporarily recovers at night or during cloudy weather',
            'Leaves develop purplish or pale yellow tints with stunted outer leaf growth',
            'Severe head stunting or complete failure to form a marketable head'
        ],
        'spread': [
            'Extremely durable resting spores that survive in soil for over 15 to 20 years',
            'Movement of infested mud and soil on farm equipment, tractor tires, boots, and tools',
            'Contaminated seedlings purchased from uncertified commercial nurseries',
            'Drainage and flood water carrying spores across field terraces'
        ],
        'management': [
            'Carefully dig out and incinerate heavily infected plants along with their distorted root systems',
            'Incorporate agricultural lime or hydrated lime into acidic fields to elevate soil pH above 7.2-7.5',
            'Improve field drainage through raised ridges, contour ditches, and subsoiling',
            'Thoroughly wash and disinfect farm machinery with 10% bleach or pressure washers before exiting infested fields'
        ],
        'prevention': [
            'Plant clubroot-resistant cabbage hybrids specifically developed for clubroot-endemic soils',
            'Apply agricultural limestone 6 to 12 weeks before planting to maintain soil pH around 7.3',
            'Strictly use certified disease-free transplants grown in sterile potting substrate',
            'Enforce long crop rotations (minimum 6-8 years) away from all Brassicaceae family crops'
        ],
        'urgency': 'High'
    },
    'Cherry|Bacterial Canker': {
        'description': 'A serious bacterial disease of sweet and sour cherry trees that attacks trunks, branches, buds, and leaves, causing oozing gummosis cankers, spur death, and branch dieback.',
        'cause': 'Pseudomonas syringae pv. syringae and Pseudomonas syringae pv. morsprunorum (bacteria); favored by cool, wet spring weather (15-20°C), frost events, and pruning injuries.',
        'symptoms': [
            'Elliptical sunken cankers on branches and trunks, often exuding copious amber-colored gum (gummosis)',
            'Leaves on girdled limbs suddenly wilt, turn brown, and remain attached to dead branches',
            'Dark brown water-soaked spots on leaves that drop out, creating a "shot-hole" appearance',
            'Blighted dormant buds that fail to open in spring or produce stunted yellow shoots',
            'Brown necrotic spots on developing cherry fruit skins'
        ],
        'spread': [
            'Splashing rain and wind-driven moisture washing epiphytic bacteria into natural openings and wounds',
            'Pruning cuts made during wet or dormant seasons',
            'Frost cracks, hail injuries, and leaf-scar entry points during autumn leaf fall',
            'Contaminated budding wood and nursery grafting knives'
        ],
        'management': [
            'Prune blighted cankered limbs during dry summer months (June-July), cutting 15-20 cm below visible margins',
            'Disinfect pruning shears between every single cut with 70% ethanol or 10% sodium hypochlorite',
            'Cauterize or scrape trunk cankers to clean wood and seal with approved protective tree wound paint',
            'Apply registered copper-based bactericides (e.g., Bordeaux mixture or Copper Hydroxide) at leaf fall in autumn and bud swell in spring'
        ],
        'prevention': [
            'Plant cherry varieties on tolerant rootstocks suited to local soil types (avoiding cold, wet, poorly drained soils)',
            'Paint tree trunks with white latex paint to prevent winter sunscald and frost-induced bark cracking',
            'Avoid heavy autumn nitrogen applications that prolong late succulent growth vulnerable to frost',
            'Maintain orchard floor vegetation and optimize soil drainage'
        ],
        'urgency': 'High'
    },
    'Cherry|Brown Rot': {
        'description': 'A destructive fungal disease of stone fruits affecting blossoms, spurs, and fruits, causing rapid brown fruit decay, tan spore tufts, and hard mummified fruits clinging to branches.',
        'cause': 'Monilinia fructicola and Monilinia laxa (fungi); favored by warm, humid or rainy weather (20-25°C) during bloom and fruit ripening stages.',
        'symptoms': [
            'Blossom blight: blossoms wilt, turn brown, and collapse rapidly, adhering to twigs in gummy clumps',
            'Small circular light brown spots on ripening fruit that rapidly expand to consume the entire fruit within 48 hours',
            'Concentric circles of powdery tan-to-grey spore cushions (coremia) erupting across rotting fruit',
            'Infected fruit shrivels into a dark, wrinkled, hardened "mummy" hanging in the tree canopy or lying on the orchard floor',
            'Small elliptical cankers forming on bearing twigs at the base of blighted blossoms'
        ],
        'spread': [
            'Airborne conidia carried by wind and insects from overwintering fruit mummies and twig cankers',
            'Rain splash distributing spores onto open blossoms and maturing fruit clusters',
            'Insect wounds (curculio, fruit flies, wasps) and bird pecks providing entry portals for fungal hyphae',
            'Fruit-to-fruit contact in dense ripening clusters'
        ],
        'management': [
            'Rake, collect, and burn or bury all mummified fruit from trees and ground during winter pruning',
            'Prune out twig cankers and blighted fruiting spurs during dry weather',
            'Apply registered bloom and pre-harvest fungicides (e.g., Fenbuconazole, Tebuconazole, Boscalid, or Captan) as per local stone fruit spray programs',
            'Handle harvested cherries with extreme care; chill immediately to 0-2°C to prevent post-harvest rot development'
        ],
        'prevention': [
            'Prune tree canopies to open vase or central leader forms that maximize sunlight penetration and airflow',
            'Thin fruit clusters to eliminate fruit touching and promote rapid drying after rain',
            'Implement rigorous orchard floor sanitation and weed mowing',
            'Control fruit-wounding insect pests early in the growing cycle'
        ],
        'urgency': 'High'
    },
    'Cotton|Alternaria Leaf Spot': {
        'description': 'A major foliar fungal disease of cotton that forms brown concentric target spots on leaves and bracts, causing premature defoliation, reduced boll filling, and lower fiber quality.',
        'cause': 'Alternaria macrospora and Alternaria alternata (fungi); favored by warm temperatures (25-30°C), intermittent rains, high humidity, and nutritional potassium stress.',
        'symptoms': [
            'Small circular brown to reddish-brown lesions with distinct purple margins on cotyledons and leaves',
            'Spots enlarge (up to 10-15 mm) with concentric rings forming a characteristic target-like appearance',
            'Centers of old spots become brittle, crack, and fall out, giving a shot-hole appearance',
            'Severe leaf blighting, yellowing, and heavy premature defoliation under high humidity',
            'Lesions on bolls and bracts leading to boll rot, premature boll opening, and fiber staining'
        ],
        'spread': [
            'Wind-borne conidia and rain splash dispersing spores across the canopy',
            'Seed-borne fungal mycelium inside and on cotton seed fuzz',
            'Survival in infected dry crop residues and perennial weed hosts'
        ],
        'management': [
            'Collect and burn or deep-plow infected cotton stalks immediately after the final harvest',
            'Apply foliar sprays of registered fungicides (e.g., Mancozeb, Propiconazole, or Pyraclostrobin) at early symptom detection',
            'Apply balanced potassium fertilization; potassium-deficient cotton plants are highly susceptible to Alternaria blight',
            'Avoid unnecessary late-season irrigation that maintains high canopy humidity'
        ],
        'prevention': [
            'Use acid-delinted and certified fungicide-treated cotton seed',
            'Practice 2 to 3-year crop rotation with non-host crops like cereals, sorghum, or pulses',
            'Maintain optimal plant density and row spacing to ensure adequate canopy air circulation',
            'Grow tolerant cotton cultivars adapted to local agro-climatic conditions'
        ],
        'urgency': 'Medium'
    },
    'Cotton|Bacterial Blight': {
        'description': 'Also known as angular leaf spot, black arm, and boll rot; a destructive bacterial disease causing water-soaked angular leaf lesions, stem cankers, and rotten cotton bolls.',
        'cause': 'Xanthomonas citri pv. malvacearum (syn. Xanthomonas campestris pv. malvacearum, bacterium); favored by warm (28-35°C), wet, windy, and high humidity conditions.',
        'symptoms': [
            'Angular, water-soaked leaf spots bounded by small leaf veinlets on lower leaf surfaces',
            'Spots turn dark reddish-brown to black, coalescing into extensive necrotic blighted patches',
            'Black arm phase: deep black elongated cankers on petioles and stems causing branch snapping',
            'Boll rot phase: circular, water-soaked, dark sunken spots on green bolls causing premature shedding or stained lint',
            'Seedling phase: water-soaked round lesions on cotyledons causing seedling collapse'
        ],
        'spread': [
            'Internally and externally seed-borne in fuzzy or poorly delinted seed',
            'Wind-driven rain, storm splash, and hail injuries facilitating bacterial ingress',
            'Crop residues left on soil surfaces and infected volunteer cotton seedlings',
            'Overhead sprinkler irrigation run-off'
        ],
        'management': [
            'Rogue and burn severely blighted seedlings and branches in early season',
            'Spray copper oxychloride combined with streptomycin sulphate as per regional university IPM recommendations',
            'Avoid field operations (weeding, scouting) while foliage is wet with rain or morning dew',
            'Deep-plow crop stubble immediately after harvest to accelerate decomposition of bacterial sources'
        ],
        'prevention': [
            'Plant certified acid-delinted cotton seeds treated with antibacterial seed dressings',
            'Cultivate bacterial blight-resistant cotton varieties/hybrids containing B-resistance genes',
            'Implement 2-year crop rotations with non-host crops like maize, wheat, or pearl millet',
            'Avoid excessive vegetative growth caused by over-application of nitrogen fertilizers'
        ],
        'urgency': 'High'
    },
    'Cotton|Fusarium Wilt': {
        'description': 'A destructive vascular wilt disease that enters cotton roots from infested soil, blocking xylem vessels, causing leaf chlorosis, severe wilting, and dark vascular ring staining.',
        'cause': 'Fusarium oxysporum f. sp. vasinfectum (fungus); soil-borne pathogen; exacerbated by root-knot nematode (Meloidogyne incognita) infestations and warm sandy-loam soils (25-32°C).',
        'symptoms': [
            'Foliar chlorosis starting at the margins of lower leaves and progressing inward between main veins',
            'Affected leaves wilt, turn brown, dry out, and drop prematurely, leaving bare stems',
            'Marked stunting of plants compared to adjacent healthy cotton stands',
            'Continuous dark brown to black vascular discoloration visible when the stem or taproot is sliced longitudinally',
            'Complete wilting and collapse of young seedlings or bearing adult plants'
        ],
        'spread': [
            'Long-lived chlamydospores surviving in soil for over a decade',
            'Soil movement on cultivation machinery, vehicle tires, irrigation run-off, and livestock hooves',
            'Contaminated gin trash and uncertified fuzzy seed containing microconidia',
            'Synergistic interaction with root-knot nematodes creating root wounds'
        ],
        'management': [
            'Uproot and destroy wilted plants; do not compost infected residues near crop fields',
            'Manage root-knot nematode populations using bio-nematicides (Paecilomyces lilacinus) or crop rotation to prevent root ingress wounds',
            'Apply Trichoderma harzianum or Pseudomonas fluorescens enriched farmyard manure into seed furrows',
            'Provide balanced soil nutrients; ensure adequate potassium levels to enhance vascular resilience'
        ],
        'prevention': [
            'Sow certified Fusarium-resistant or tolerant cotton varieties and hybrids',
            'Practice multi-year crop rotation with non-hosts like sorghum, corn, or small grains',
            'Apply summer deep plowing and solarization to lower pathogen inoculum in the topsoil',
            'Thoroughly sanitize tillage equipment before entering uninfected cotton fields'
        ],
        'urgency': 'High'
    },
    'Cotton|Grey Mildew (Areolate Mildew)': {
        'description': 'A foliar fungal disease causing angular translucent leaf spots with frosty white-to-grey powdery fungal growth underneath, leading to severe premature defoliation and boll opening failure.',
        'cause': 'Ramularia gossypii (syn. Ramulariopsis gossypii, fungus); favored by cool to moderate temperatures (20-28°C), high relative humidity (>80%), and dense, shaded cotton canopies.',
        'symptoms': [
            'Small angular, areolate, pale translucent or yellowish-green spots bounded by leaf veinlets',
            'Frosty, whitish-grey powdery or velvety fungal spore growth forming on the lower leaf surface under lesions',
            'Lesions turn reddish-brown to purplish with age as leaf tissue senesces',
            'Premature shedding of middle and lower leaves, progressing rapidly upward into the canopy',
            'Substantial reduction in boll sizing, poor lint maturity, and premature opening of underdeveloped bolls'
        ],
        'spread': [
            'Airborne conidia transported by wind across fields',
            'High relative humidity and dew condensation inside closed vegetative canopies',
            'Infected cotton crop residues and alternative malvaceous weed hosts'
        ],
        'management': [
            'Prune dense lower vegetative branches to permit sunlight penetration and reduce humidity',
            'Apply registered fungicides (e.g., Carbendazim, Azoxystrobin, Propiconazole, or Wettable Sulphur) at the first sighting of grey areolate lesions on lower leaves',
            'Avoid excessive late-season irrigation and surplus nitrogen that creates thick succulent canopies',
            'Incorporate or burn crop debris after harvest to destroy overwintering mycelia'
        ],
        'prevention': [
            'Maintain recommended row spacing (e.g., 90x60 cm or 120x45 cm) to optimize canopy aeration',
            'Plant tolerant cotton hybrids selected for grey mildew resistance in humid regional belts',
            'Follow balanced NPK fertilization avoiding excessive nitrogen',
            'Keep field borders free of malvaceous weeds (e.g., Abutilon indicum)'
        ],
        'urgency': 'Medium'
    },
    'Cotton|Verticillium Wilt': {
        'description': 'A soil-borne vascular wilt disease of cotton causing mottled interveinal chlorosis (tiger-stripe pattern), defoliation, and brown vascular ring discoloration, especially in cooler irrigated soils.',
        'cause': 'Verticillium dahliae (fungus); persistent soil-borne pathogen producing microsclerotia; favored by cool to moderate air/soil temperatures (20-26°C) and heavy, alkaline soils.',
        'symptoms': [
            'Mottled interveinal chlorosis on leaves creating a characteristic "tiger-stripe" or calico pattern',
            'Marginal leaf necrosis, drying, and premature leaf drop, leaving bare plants with stunted bolls',
            'Stunting of infected plants compared to healthy stands',
            'Vascular cylinder shows continuous brown flecking or streaking when the stem is sliced open',
            'Affected bolls remain small, fail to open normally, or drop prematurely'
        ],
        'spread': [
            'Extremely durable microsclerotia surviving in soil for 15 to 20 years',
            'Movement of infested soil by cultivation equipment, wind, and irrigation water',
            'Contaminated seed and infected dry plant residues',
            'Root-to-root contact in dense planting stands'
        ],
        'management': [
            'Do not return Verticillium-infected cotton stalk residue back into the soil; remove and safely burn',
            'Avoid excessive or late irrigations that cool the soil during boll development',
            'Apply soil amendments with potassium and organic manure inoculated with Trichoderma viride',
            'Note: Foliar fungicides have no curative effect on vascular Verticillium infections'
        ],
        'prevention': [
            'Plant Verticillium-tolerant cotton varieties recommended for infested soils',
            'Rotate with non-host graminaceous crops (corn, sorghum, millets) for at least 3-4 years',
            'Deep summer plowing and soil solarization during hot summer fallow periods',
            'Adopt raised bed planting with managed deficit drip irrigation'
        ],
        'urgency': 'High'
    },
    'Grapes|Anthracnose': {
        'description': 'Also known as "bird\'s eye rot"; a destructive fungal disease affecting all green parts of grapevines, producing sunken shot-hole leaf lesions and circular sunken fruit spots that ruin grape clusters.',
        'cause': 'Elsinoe ampelina (syn. Sphaceloma ampelinum, fungus); overwintering in vine cankers; favored by warm, rainy, humid weather (24-30°C) and persistent free moisture on vine surfaces.',
        'symptoms': [
            'Small, circular reddish-brown spots on young leaves with dark brown to violet borders',
            'Centers of leaf spots turn ash-grey, become brittle, and drop out, creating a "shot-hole" appearance',
            'Deep, elongated, sunken cankers with raised purplish-black margins on young green shoots',
            'Fruit symptoms: circular, sunken spots with dark margins and ash-grey centers resembling a "bird\'s eye"',
            'Infected berries crack, become hard and mummified, or fail to mature'
        ],
        'spread': [
            'Rain splash and wind-blown droplets transporting conidia from overwintered vine cankers',
            'Infected dormant canes, spurs, and pruning wood',
            'Humid microclimates inside dense, unmanaged vine canopies'
        ],
        'management': [
            'Prune out all cankered canes and mummified berry clusters during dormant season; burn pruned wood',
            'Apply a dormant spray of lime sulphur or copper sulphate before bud break to suppress overwintering inocula',
            'Apply registered protective or systemic fungicides (e.g., Mancozeb, Captan, Azoxystrobin, or Difenoconazole) during early shoot growth and pre-bloom',
            'Avoid touching or cultivating vines when foliage is wet'
        ],
        'prevention': [
            'Implement systematic trellis training and canopy shoot thinning to maximize airflow and sun exposure',
            'Install drip irrigation rather than overhead sprinklers to prevent wetting the foliage',
            'Use certified disease-free vine cuttings for planting new vineyard blocks',
            'Maintain regular disease monitoring from early shoot emergence through fruit set'
        ],
        'urgency': 'High'
    },
    'Grapes|Bacterial Leaf Spot': {
        'description': 'A bacterial foliar and cane disease of grapevines causing water-soaked angular leaf spots, vein necrosis, leaf yellowing, and black cankers on young shoots in wet seasons.',
        'cause': 'Xanthomonas campestris pv. viticola (bacterium); favored by warm, humid, windy weather (25-32°C) with persistent rainfall or dew.',
        'symptoms': [
            'Small, water-soaked translucent angular spots on leaf blades bounded by veinlets',
            'Spots turn dark brown to black with yellow chlorotic halos, coalescing into larger necrotic patches',
            'Vein necrosis: blackening of major and secondary leaf veins causing leaf distortion and curling',
            'Elongated, black, slightly raised or cracked cankers on succulent young canes and petioles',
            'Water-soaked spots on young berry skins leading to berry shriveling and cluster drop'
        ],
        'spread': [
            'Wind-driven rain, storm splash, and hail damage facilitating bacterial entry',
            'Infected propagation cuttings and dormant budwood',
            'Pruning shears and vineyard tools carrying bacterial exudate',
            'Survival in infected fallen vine leaves and cane residues'
        ],
        'management': [
            'Prune off and safely destroy infected shoots, cankered canes, and blighted leaves',
            'Sterilize pruning shears between vines using 70% alcohol or 10% sodium hypochlorite solution',
            'Apply bactericidal sprays such as Copper Hydroxide, Copper Oxychloride, or approved Streptomycin combinations at early infection stages as per regional agricultural guidelines',
            'Avoid working in vineyards while the canopy is wet'
        ],
        'prevention': [
            'Procure certified pathogen-free vine rootstocks and scion wood from accredited nurseries',
            'Adopt open canopy training systems (Y-trellis, Bower, or Geneva Double Curtain) for rapid drying',
            'Ensure clean orchard floor management and plow under fallen leaf debris',
            'Avoid excessive nitrogen fertilizers that promote soft, highly vulnerable shoot growth'
        ],
        'urgency': 'Medium'
    },
    'Grapes|Downy Mildew': {
        'description': 'One of the most destructive fungal-like oomycete diseases of grapevines worldwide, producing yellowish "oil spots" on upper leaves and snowy white downy felt underneath, defoliating vines and destroying grape bunches.',
        'cause': 'Plasmopara viticola (oomycete); favored by warm, wet, humid weather (18-25°C) with frequent rainfall or heavy dew; requires at least 10 mm of rain and 10°C temperature for primary infection.',
        'symptoms': [
            'Yellowish, translucent, circular "oil spots" appearing on the upper surface of young leaves',
            'Dense, snowy-white downy fungal-like spore growth on the underside of leaves corresponding to the oil spots',
            'Lesions turn reddish-brown and necrotic with age, causing heavy premature leaf fall and sunburning of fruit',
            'Infected shoot tips curl, turn brown, and become covered in white sporulation',
            'Infected young berries turn greyish-blue, soften, shrivel, turn brown, and drop from clusters'
        ],
        'spread': [
            'Wind-blown and rain-splashed sporangia causing rapid secondary polycyclic infections',
            'Thick-walled sexual oospores overwintering in fallen vineyard leaves and soil',
            'Prolonged leaf wetness and high relative humidity (>85%) in dense canopies'
        ],
        'management': [
            'Ensure timely preventive fungicide sprays before forecast rain events during active shoot growth',
            'Apply registered contact or systemic fungicides (e.g., Bordeaux mixture, Metalaxyl-Mancozeb, Dimethomorph, Cymoxanil, or Fosetyl-Al) following resistance management guidelines',
            'Remove and bury infected vine shoots and fallen leaves',
            'Mow ground cover to decrease relative humidity underneath the vine canopy'
        ],
        'prevention': [
            'Canopy management: perform leaf thinning around fruit zones to maximize air circulation and sunlight exposure',
            'Switch to drip irrigation to prevent artificial foliage wetting',
            'Plant downy mildew-tolerant grape cultivars where commercially viable',
            'Utilize weather-based disease forecasting models (the 10-10-10 rule: 10 mm rain, 10°C, 10 cm shoot growth) for spray timing'
        ],
        'urgency': 'High'
    },
    'Grapes|Grey Mold (Botrytis)': {
        'description': 'A devastating fungal rot disease affecting ripening grape clusters, producing soft brown berry rot covered with dense grey velvety mold that destroys fruit yield and wine quality.',
        'cause': 'Botrytis cinerea (fungus); opportunistic necrotrophic pathogen; favored by cool to moderate temperatures (15-22°C), high humidity (>90%), and rain during veraison and harvest.',
        'symptoms': [
            'Ripening berries turn pale brown, soften, and skins slip easily from pulp (slip-skin symptom)',
            'Dense, smoky-grey velvety carpet of fungal mycelia and conidia envelops infected berry bunches',
            'Rot rapidly spreads throughout the cluster via direct berry-to-berry contact, turning bunches into mushy brown masses',
            'Brown necrotic lesions on leaves with irregular concentric zones during wet spring periods',
            'Dark brown cankers and shoot blight on young green shoots during wet early seasons'
        ],
        'spread': [
            'Airborne conidia transported widely by breezes and atmospheric turbulence',
            'Pre-existing wounds on berries caused by powdery mildew, berry moths, hail, bird pecks, or berry cracking',
            'Sclerotia overwintering on dormant canes, vine bark, and mummified berry clusters',
            'Dense, tightly packed grape clusters with poor air circulation'
        ],
        'management': [
            'Hand-pick and remove infected bunches or cluster sections during early harvest inspections',
            'Apply registered botryticides (e.g., Fenhexamid, Boscalid, Cyprodinil+Fludioxonil, or Iprodione) at bloom, pre-bunch closure, veraison, and pre-harvest complying with pre-harvest intervals',
            'Apply biocontrol agents such as Bacillus subtilis or Trichoderma at bloom to colonize floral debris',
            'Carefully control berry-feeding caterpillars and powdery mildew to prevent fruit skin wounds'
        ],
        'prevention': [
            'Leaf removal (leaf pulling) around grape clusters shortly after fruit set to increase ventilation and sun exposure',
            'Adopt loose-clustered vine clones or rootstocks that minimize berry crowding',
            'Avoid excessive nitrogen fertilization that increases berry skin fragility and vigor',
            'Regulate irrigation to prevent rapid berry swelling and split skins near harvest'
        ],
        'urgency': 'High'
    },
    'Grapes|Powdery Mildew': {
        'description': 'One of the most pervasive fungal diseases of grapevines, producing white powdery or ash-grey fungal patches on leaves, shoots, and fruit, causing berry cracking, russeting, and poor wine quality.',
        'cause': 'Erysiphe necator (syn. Uncinula necator, fungus); favored by warm temperatures (20-28°C), low light/shaded canopies, and moderate humidity; unlike downy mildew, does not require free water to infect.',
        'symptoms': [
            'White, powdery, cobwebby or ash-grey patches on the upper and lower surfaces of leaves',
            'Infected young leaves crinkle, cup upward, distort, and senesce prematurely',
            'Dark brown to black web-like scarring (reticulated russeting) on young green shoots',
            'Fruit symptoms: berries covered in white powder; berry skins lose elasticity and crack open, exposing seeds',
            'Cracked berries become infected secondarily by Botrytis and sour rot pathogens'
        ],
        'spread': [
            'Wind-dispersed conidia traveling long distances throughout the vineyard',
            'Cleistothecia (chasmothecia) overwintering in the crevices of vine bark',
            'Infected dormant buds giving rise to diseased "flag shoots" in early spring'
        ],
        'management': [
            'Prune and discard infected "flag shoots" in early spring to eliminate primary spore factories',
            'Apply registered fungicides (e.g., Wettable Sulphur, Difenoconazole, Tebuconazole, Azoxystrobin, or Fluopyram) starting from early shoot growth (5-10 cm) through fruit set',
            'Rotate fungicide chemical classes (FRAC codes) to prevent fungicide resistance development',
            'Spray potassium bicarbonate or horticultural mineral oils at early powdery colony detection'
        ],
        'prevention': [
            'Prune and train vine canopies for open structure, good light penetration, and excellent air movement',
            'Maintain strict seasonal preventative spray schedules during the critical pre-bloom to pea-sized berry stage',
            'Avoid over-fertilizing with nitrogen to minimize excessive shade and dense vegetative growth',
            'Monitor vineyards closely for initial flag shoots and early leaf patches'
        ],
        'urgency': 'High'
    },
    'Maize (Corn)|Common Rust': {
        'description': 'A widespread airborne fungal disease of corn/maize producing golden-brown to cinnamon-brown pustules on both leaf surfaces, reducing active green leaf area and grain weight.',
        'cause': 'Puccinia sorghi (fungus); favored by cool to moderate temperatures (16-25°C), high relative humidity (>95%), and prolonged overnight dew periods.',
        'symptoms': [
            'Small, circular to elongated, powdery golden-brown to cinnamon-brown pustules (uredinia)',
            'Pustules erupt prominently on both the upper and lower leaf surfaces, scattering powdery spores',
            'Yellowish chlorotic halos commonly encircle older erupting pustules',
            'Pustules coalesce under severe infection, causing large patches of leaf death, drying, and premature senescence',
            'In late season, pustules turn dark brownish-black as teleutospores (overwintering spores) form'
        ],
        'spread': [
            'Urediniospores carried across hundreds of kilometers on prevailing wind currents',
            'High relative humidity and frequent dew condensation providing moisture for spore germination',
            'Volunteer corn plants and alternative oxalis (woodsorrel) hosts supporting sexual stages'
        ],
        'management': [
            'Scout fields regularly from vegetative whorl through silking stages',
            'Apply registered foliar fungicides (e.g., Azoxystrobin, Pyraclostrobin, Propiconazole, or Mancozeb) if pustules appear on upper leaves before silking on susceptible hybrids',
            'Destroy volunteer maize plants and eradicate nearby Oxalis weeds',
            'Incorporate post-harvest corn residues to reduce local spore carryover'
        ],
        'prevention': [
            'Plant commercially available rust-resistant corn hybrids (featuring Rp resistance genes)',
            'Time planting dates early in the season to avoid peak spore migration windows',
            'Maintain balanced crop nutrition; avoid excessive nitrogen that produces lush susceptible tissue',
            'Rotate fields with non-host crops such as soybeans, pulses, or cotton'
        ],
        'urgency': 'Medium'
    },
    'Onion|Downy Mildew': {
        'description': 'A destructive foliar oomycete disease of onions causing elongated pale yellow patches covered with violet-grey downy fungal felt, leading to leaf collapse, reduced bulb sizing, and storage rot.',
        'cause': 'Peronospora destructor (oomycete); favored by cool, moist, foggy or rainy weather (10-18°C) with relative humidity above 90% and overnight dew.',
        'symptoms': [
            'Pale green to yellowish, elongated, oval or cylindrical lesions on older onion leaves',
            'Furry, violet-grey downy fungal growth coats the lesions in early morning hours or humid damp weather',
            'Affected leaf tissue turns pale, water-soaked, collapses, and breaks over at the lesion point',
            'Leaf tips wither and die back rapidly, leaving the plant defoliated and severely weakened',
            'Infected bulbs remain small, neck tissue becomes spongy, and bulbs decay easily during storage'
        ],
        'spread': [
            'Wind-borne sporangia carried over long distances during cool, cloudy, damp mornings',
            'Systemically infected onion seed bulbs, sets, or volunteer onion plants',
            'Thick-walled oospores persisting in infected soil and decayed onion leaf residues for years'
        ],
        'management': [
            'Rogue and safely destroy severely infected plants and volunteer onions',
            'Apply registered fungicides (e.g., Metalaxyl-Mancozeb, Cymoxanil, Dimethomorph, or Copper Hydroxide) at first detection or when weather conditions favor infection',
            'Apply sprays with a non-ionic wetting agent (spreader-sticker) to adhere fungicides to waxy onion foliage',
            'Avoid overhead sprinkler irrigation; switch to drip or furrow irrigation systems'
        ],
        'prevention': [
            'Plant certified disease-free onion seeds and sets inspected for downy mildew freedom',
            'Practice minimum 3 to 4-year crop rotations with non-allium crops',
            'Orient planting rows parallel to prevailing winds to facilitate rapid canopy drying',
            'Do not pile onion culls or waste near cultivated onion fields'
        ],
        'urgency': 'High'
    },
    'Onion|Fusarium Basal Plate Rot': {
        'description': 'A devastating soil-borne fungal disease attacking onion roots and basal stem plates, causing yellow leaf dieback, root decay, brown basal plate necrosis, and total bulb rot.',
        'cause': 'Fusarium oxysporum f. sp. cepae (fungus); persistent soil inhabitant; favored by warm soil temperatures (25-32°C) and root injuries caused by onion maggots or nematodes.',
        'symptoms': [
            'Progressive yellowing, curving, and tip dieback of onion leaves, starting with the oldest outer leaves',
            'Roots turn dark brown, become water-soaked, soften, and rot away completely',
            'Stem basal plate turns brown to reddish-purple, developing a soft, watery or spongy decay',
            'White or pinkish fungal mycelium often visible between scales at the base of affected bulbs',
            'Bulbs rot in the ground or develop insidious dry rot during post-harvest storage'
        ],
        'spread': [
            'Chlamydospores persisting in field soil for more than 10 to 15 years',
            'Infested onion sets, seed cloves, and nursery transplants',
            'Soil movement on plows, cultivators, tractor tires, and irrigation water',
            'Feeding wounds created by onion maggots, wireworms, and root-knot nematodes'
        ],
        'management': [
            'Carefully dig out and destroy infected bulbs; never leave rotting bulbs in the field or cull piles',
            'Control soil insects and maggots using approved granular treatments to eliminate root entry wounds',
            'Incorporate bio-fungicides (Trichoderma viride or Trichoderma harzianum) into planting beds with compost',
            'Cure harvested bulbs thoroughly with good warm dry ventilation before storage'
        ],
        'prevention': [
            'Plant Fusarium-resistant onion cultivars and hybrids',
            'Practice strict 4 to 5-year crop rotations with non-allium crops (wheat, barley, corn, or legumes)',
            'Ensure excellent soil drainage and avoid deep planting of onion sets',
            'Inspect seed sets and discard any sets showing basal discoloration or softness'
        ],
        'urgency': 'High'
    },
    'Onion|Purple Blotch': {
        'description': 'A major fungal foliar disease of onion and garlic characterized by elliptical purplish lesions with dark concentric rings, causing leaf snapping, reduced photosynthesis, and neck bulb rot.',
        'cause': 'Alternaria porri (fungus); favored by warm, humid weather (22-30°C) with prolonged relative humidity (>80%) or frequent rains, often following thrips feeding damage.',
        'symptoms': [
            'Small, water-soaked lesions on leaves and seed stalks that quickly develop white centers',
            'Lesions enlarge into elliptical, zonate patches with characteristic dark purple to reddish-brown centers and yellow halos',
            'Concentric rings of dark brown fungal spores form across the purple lesions in humid conditions',
            'Leaves turn yellow, girdle, collapse, and snap over at the lesion site',
            'Infection enters the bulb neck, causing a semi-watery dark yellow to wine-red rot of internal scales'
        ],
        'spread': [
            'Airborne conidia transported by wind and rain splash from diseased foliage',
            'Mycelia and spores surviving on infected onion crop residues and volunteer plants',
            'Insects, especially onion thrips (Thrips tabaci), creating entry wounds through feeding punctures'
        ],
        'management': [
            'Control onion thrips rigorously with registered insecticides or neem formulations; thrips wounds accelerate infection',
            'Apply registered fungicides (e.g., Mancozeb, Difenoconazole, Tebuconazole, Chlorothalonil, or Azoxystrobin) at the onset of initial lesions',
            'Always incorporate an agricultural surfactant/sticker to ensure fungicide spray adheres to waxy onion foliage',
            'Collect and burn crop residues after harvest to eliminate field inoculum'
        ],
        'prevention': [
            'Maintain 3-year crop rotations away from allium species (onion, garlic, leeks, shallots)',
            'Use certified disease-free seed; perform hot water seed treatment or fungicide seed dressing',
            'Ensure adequate plant spacing to allow rapid drying of leaves after rain or irrigation',
            'Avoid excessive nitrogen fertilization that creates soft, lush, highly susceptible foliage'
        ],
        'urgency': 'High'
    },
    'Onion|Stemphylium Leaf Blight': {
        'description': 'A damaging fungal leaf disease of onions producing yellow-brown to dark lesions covered with olive-brown velvety spores, causing rapid foliar blighting and premature crop maturity.',
        'cause': 'Stemphylium vesicarium (fungus); favored by warm temperatures (18-25°C), high humidity, long periods of leaf wetness (>16 hours), and existing leaf injuries (thrips, hail, or chemical scorch).',
        'symptoms': [
            'Small, oval or elongated, yellowish-to-tan water-soaked spots on leaves and seed scapes',
            'Spots expand into extensive olive-brown to black elongated blighted zones as dark spores develop',
            'Lesions coalesce rapidly, causing complete blighting, drying, and collapse of entire leaf blades',
            'Dieback typically begins on the side of leaves facing prevailing winds or sun-scalded tissue',
            'Significant reduction in bulb size due to early destruction of photosynthetic leaf area'
        ],
        'spread': [
            'Airborne conidia carried across fields by wind currents',
            'Ascospores discharged from pseudothecia surviving on dead onion debris',
            'Rain splash, overhead irrigation, and entry through physical wounds and thrips injuries'
        ],
        'management': [
            'Control thrips and other wounding agents diligently to prevent fungal entry pathways',
            'Apply registered protectant and systemic fungicides (e.g., Mancozeb, Fluopyram, Pyraclostrobin, or Tebuconazole) combined with a surfactant',
            'Avoid sprinkler irrigation; use drip irrigation to keep onion leaves dry',
            'Deep-plow or destroy onion debris immediately post-harvest'
        ],
        'prevention': [
            'Practice 3 to 4-year crop rotation with non-allium crops',
            'Ensure balanced plant nutrition; avoid potassium deficiency and excessive nitrogen',
            'Adopt optimum row spacing to promote canopy ventilation',
            'Plant certified clean seed and inspect seedlings before transplanting'
        ],
        'urgency': 'High'
    },
    'Onion|White Rot': {
        'description': 'A devastating soil-borne fungal disease of allium crops causing progressive yellowing, leaf dieback, fluffy white mycelium around the bulb base, and clusters of tiny black sclerotia.',
        'cause': 'Stromatinia cepivora (syn. Sclerotium cepivorum, fungus); host-specific to alliums; stimulated to germinate exclusively by allium root exudates; favored by cool soil temperatures (10-20°C).',
        'symptoms': [
            'Initial yellowing, wilting, and collapse of foliage starting with older outer leaves',
            'Fluffy, snowy-white fungal mycelium covers the roots and the base of the onion bulb',
            'Numerous tiny, hard, poppy-seed-like black sclerotia form within the white fungal mass',
            'Roots and basal plate decay completely, causing bulbs to be pulled out of the soil with zero resistance',
            'Infected bulbs rot completely into a soft, watery mush in the field or in storage'
        ],
        'spread': [
            'Sclerotia surviving dormant in field soil for more than 20 to 30 years without allium hosts',
            'Movement of contaminated soil on tractor tires, plows, footwear, and harvest equipment',
            'Infested onion sets, garlic cloves, and nursery transplants',
            'Irrigation run-off and drainage water flowing from infested fields'
        ],
        'management': [
            'Carefully dig out and incinerate infected plants along with surrounding soil; never leave in the field',
            'Strictly quarantine infested field sections; pressure-wash and disinfect all machinery and boots before leaving',
            'In small plots, apply garlic oil or diallyl disulfide (DADS) to fallow soil to trigger "suicidal" sclerotia germination in the absence of hosts',
            'Apply registered fungicides (e.g., Tebuconazole or Boscalid) as furrow or transplant drenches where recommended'
        ],
        'prevention': [
            'Strictly avoid planting alliums in fields with a known history of white rot',
            'Use only certified disease-free onion sets, seeds, and transplants from guaranteed clean nurseries',
            'Practice long-term sanitation protocols to prevent soil transfer between fields',
            'Maintain strict equipment hygiene across all production blocks'
        ],
        'urgency': 'High'
    },
    'Rice|Bacterial Leaf Blight': {
        'description': 'One of the most destructive bacterial diseases of rice in Asia and Africa, causing wavy water-soaked lesions along leaf margins that turn straw-colored, leading to severe blighting and poor grain filling.',
        'cause': 'Xanthomonas oryzae pv. oryzae (bacterium); favored by high temperatures (25-34°C), high humidity (>70%), heavy monsoons, and high nitrogen fertilization.',
        'symptoms': [
            'Tiny water-soaked stripes along the margins of leaf blades that turn yellow to straw-colored with wavy edges',
            'Lesions expand and coalesce, blighting entire leaf blades from the tip downward',
            'Milky, opaque bacterial dew-like exudate droplets appear on young lesions in early morning, drying into yellow crusty beads',
            'Kresek phase: acute wilting and death of entire young tillers within 1-3 weeks after transplanting',
            'Severely blighted hills produce chaffy, partially filled, discolored grains with high yield loss'
        ],
        'spread': [
            'Rain storms, wind-driven rain, and turbulent monsoon winds blowing bacteria onto leaf wounds',
            'Deep irrigation water and continuous field-to-field flooding transferring bacterial cells',
            'Infected rice stubble, volunteer rice seedlings, and wild graminaceous weed hosts (Leersia hexandra)',
            'Handling seedlings during pulling and transplanting'
        ],
        'management': [
            'Drain standing water from infected fields for 3-4 days to arrest bacterial proliferation',
            'Immediately suspend further top-dressing of chemical nitrogenous fertilizers',
            'Apply balanced potash (potassium) fertilizer to strengthen cell walls against bacterial penetration',
            'Spray copper oxychloride combined with streptomycin sulphate or bronopol as per regional agricultural guidelines'
        ],
        'prevention': [
            'Plant certified bacterial leaf blight-resistant rice varieties carrying Xa-resistance genes',
            'Avoid excessive nitrogen applications; split nitrogen into multiple smaller doses matching crop demand',
            'Maintain clean irrigation channels and avoid continuous field-to-field overflow watering',
            'Eradicate weed hosts and plow under rice stubble immediately after harvest'
        ],
        'urgency': 'High'
    },
    'Rice|Blast': {
        'description': 'The most devastating fungal disease of rice globally, attacking leaves, collars, nodes, and panicle necks, producing diamond-shaped leaf lesions and "neck blast" that causes total yield loss.',
        'cause': 'Magnaporthe oryzae (anamorph Pyricularia oryzae, fungus); favored by cool nights (18-22°C), warm days (25-28°C), high humidity (>90%), long dew periods, and excessive nitrogen.',
        'symptoms': [
            'Leaf blast: spindle-shaped or diamond-shaped lesions with grey or whitish centers and brown to reddish borders',
            'Lesions enlarge, coalesce, and rapidly desiccate entire leaf blades, giving fields a scorched or burnt look',
            'Collars develop dark brown necrosis leading to leaf blade detachment from the sheath',
            'Node blast: blackening and rotting of stem nodes causing stems to snap easily',
            'Neck blast: dark brown to black rot of the panicle neck/base; panicles break, droop, and grains remain completely empty and white ("whiteheads")'
        ],
        'spread': [
            'Airborne conidia released in massive quantities during nighttime hours and transported by wind',
            'Infected rice seeds carrying dormant mycelia and conidia',
            'Infected rice straw, crop residues, and alternative grassy weeds'
        ],
        'management': [
            'Avoid excessive nitrogen applications; apply silicon fertilizers to toughen leaf epidermis',
            'Apply registered blast fungicides (e.g., Tricyclazole, Isoprothiolane, Azoxystrobin, or Kasugamycin) at early foliar symptom onset and preventively at 5% panicle emergence to block neck blast',
            'Maintain optimal water levels in paddies; do not allow the field to dry out completely during vegetative growth',
            'Collect and destroy infected straw after harvest'
        ],
        'prevention': [
            'Grow blast-resistant rice cultivars recommended by local rice research stations; rotate resistant varieties to prevent pathotype breakdown',
            'Perform seed treatment with Tricyclazole or Carbendazim prior to sowing in nursery beds',
            'Adopt optimal seedling spacing and avoid overcrowded nursery beds',
            'Eradicate grassy weeds around nursery perimeters and bunds'
        ],
        'urgency': 'High'
    },
    'Rice|Brown Spot': {
        'description': 'A major fungal disease of rice producing oval brown spots with yellow halos on leaves and glumes, strongly associated with nutrient-deficient, stressed, or poorly managed soils.',
        'cause': 'Bipolaris oryzae (syn. Helminthosporium oryzae, fungus); seed-borne and air-borne; favored by warm temperatures (25-30°C), high humidity (>85%), and soils deficient in silicon, potassium, or nitrogen.',
        'symptoms': [
            'Small, circular to oval sesame-seed-like brown spots uniformly scattered across leaf blades',
            'Fully developed spots have light brown or greyish centers surrounded by dark reddish-brown margins and yellow halos',
            'Infection on glumes causes dark brown to black discolored patches, reducing seed germination and milling quality ("pecky rice")',
            'Heavy infection causes leaves to wither, dry up, and die prematurely',
            'Seedlings from infected seeds exhibit brown coleoptile lesions and damping-off'
        ],
        'spread': [
            'Internally and externally seed-borne via infected grain lots',
            'Airborne conidia dispersed by wind and rain splash across fields',
            'Survival in infected crop residues, volunteer rice, and wild grass hosts'
        ],
        'management': [
            'Correct underlying soil fertility problems; apply balanced NPK along with zinc and silicon amendments',
            'Maintain proper field irrigation to avoid soil drought and root stress',
            'Apply registered foliar fungicides (e.g., Mancozeb, Propiconazole, or Edifenphos) if disease pressure is high during tillering and panicle initiation',
            'Plow under rice stubble and straw after harvest'
        ],
        'prevention': [
            'Treat seed with hot water (53-54°C for 10-12 minutes) or dress with Carbendazim/Thiram before nursery sowing',
            'Plant brown spot-tolerant rice varieties suited to local soil types',
            'Apply balanced fertilizers based on soil testing; never starve plants of potassium or micronutrients',
            'Rotate paddies with leguminous green manure crops (Dhaincha/Sesbania)'
        ],
        'urgency': 'Medium'
    },
    'Rice|Sheath Blight': {
        'description': 'A destructive soil-borne fungal disease of rice that forms water-soaked, snake-skin-like oval lesions on leaf sheaths near the water line, rapidly climbing up the canopy and causing extensive lodging.',
        'cause': 'Rhizoctonia solani (fungus); soil-borne pathogen producing durable sclerotia; favored by high temperatures (28-32°C), high humidity (85-100%), dense planting, and heavy nitrogen use.',
        'symptoms': [
            'Greenish-grey, oval or oblong water-soaked lesions on leaf sheaths just above the water line',
            'Lesions enlarge with irregular brownish-red margins and bleached white to straw-colored centers ("snake-skin" pattern)',
            'Lesions coalesce and spread upward onto upper leaf sheaths, flag leaves, and panicles',
            'Entire tillers blight, turn brown, and lodge flat in the water in circular patches across the field',
            'Globular white fungal sclerotia form on lesions, turning dark brown to black as they mature'
        ],
        'spread': [
            'Sclerotia that float on irrigation water and attach to rice tillers during transplanting and tillering',
            'Plant-to-plant mycelial contact through dense, lush, overcrowded canopies',
            'Sclerotia surviving in field soil and levees for over two years',
            'Alternative grassy weed hosts along field bunds'
        ],
        'management': [
            'Skim and collect floating sclerotia and crop debris during field puddling before transplanting',
            'Avoid excessive nitrogen applications; split nitrogen into smaller, well-timed top-dressings',
            'Apply registered fungicides (e.g., Hexaconazole, Validamycin, Azoxystrobin, or Thifluzamide) targeted at the base of tillers at initial symptom appearance',
            'Drain fields periodically to allow soil surface aeration and suppress humidity'
        ],
        'prevention': [
            'Adopt wider spacing between hills (20x15 cm or 20x20 cm) to improve airflow through the lower canopy',
            'Avoid over-flooding; maintain recommended shallow water depth during vegetative growth',
            'Keep bunds and irrigation channels clean of wild grasses and weeds',
            'Apply Trichoderma viride or Pseudomonas fluorescens formulations into nursery beds and transplant roots'
        ],
        'urgency': 'High'
    },
    'Rice|Tungro Disease': {
        'description': 'A serious viral disease complex of rice causing conspicuous orange-yellow leaf discoloration, severe plant stunting, reduced tillering, and delayed or incomplete panicle emergence.',
        'cause': 'Rice tungro bacilliform virus (RTBV) and Rice tungro spherical virus (RTSV); transmitted semi-persistently by green leafhoppers (Nephotettix virescens and Nephotettix nigropictus).',
        'symptoms': [
            'Conspicuous yellow to orange-yellow discoloration of leaves starting from leaf tips and margins',
            'Severe stunting of affected rice hills with marked reduction in tiller number',
            'Young leaves often show mottled interveinal chlorosis, rust-colored speckling, and leaf spiraling',
            'Delayed flowering and incomplete exertion of panicles; panicles are small with sterile, discolored grains',
            'Root systems are severely stunted and turn dark brown with few active feeder rootlets'
        ],
        'spread': [
            'Green leafhopper vectors acquiring and transmitting both viruses within minutes of feeding on infected plants',
            'Infected volunteer rice plants, ratoon crops, and grassy weeds (Echinochloa, Leersia) serving as virus reservoirs',
            'Vector migration between overlapping sequential plantings'
        ],
        'management': [
            'Rogue and destroy infected hills in early vegetative stages to minimize field virus reservoirs',
            'Monitor green leafhopper populations using light traps and sweep nets (threshold: 1 leafhopper/hill)',
            'Spray registered insecticides (e.g., Thiamethoxam, Dinotefuran, or Imidacloprid) targeting leafhopper vectors to halt virus transmission',
            'Plow under ratoon growth and stubble immediately after harvest'
        ],
        'prevention': [
            'Plant tungro-resistant or tolerant rice cultivars recommended by national rice institutes',
            'Practice synchronous planting over large contiguous blocks to break vector life cycles',
            'Establish a 1-month crop-free fallow period between rice seasons to starve leafhopper vectors',
            'Eradicate alternative host weeds along irrigation channels and field borders'
        ],
        'urgency': 'High'
    },
    'Sugarcane|Grassy Shoot Disease': {
        'description': 'A major phytoplasma disease of sugarcane causing profuse sprouting of thin, chlorotic tillers at the stool base, turning the cane clump into a dense, unproductive, grass-like bush.',
        'cause': 'Candidatus Phytoplasma sacchari; transmitted by aphid and leafhopper vectors and contaminated seed setts; favored by continuous ratoon cropping and hot dry conditions.',
        'symptoms': [
            'Profuse proliferation of slender, thin, stunted tillers from the base of the stool giving a bushy grassy appearance',
            'Leaves are narrow, completely chlorotic, pale yellow, or creamy-white without normal green chlorophyll',
            'Failure of cane stalks to elongate or form normal millable joints',
            'Premature sprouting of lateral buds all along existing cane stalks',
            'Complete yield failure; ratoon crops suffer progressive deterioration and stool death'
        ],
        'spread': [
            'Use of infected seed cane setts taken from diseased fields',
            'Insect vectors including the black sugarcane aphid (Melanaphis sacchari) and planthoppers',
            'Harvesting knives and cutting blades moving sap from diseased stools to healthy setts'
        ],
        'management': [
            'Uproot and burn diseased stools completely; do not allow diseased ratoon crops to continue',
            'Treat seed setts with Moist Hot Air Treatment (MHAT at 54°C for 2.5 hours) or Hot Water Treatment (50°C for 2 hours) to eliminate internal phytoplasmas',
            'Spray approved insecticides (e.g., Dimethoate or Imidacloprid) to control vector aphid colonies',
            'Disinfect sett-cutting knives regularly in a 5% lysol or bleach solution'
        ],
        'prevention': [
            'Source certified disease-free three-tier seed cane nursery material',
            'Grow tolerant sugarcane varieties recommended for the regional mill command area',
            'Avoid taking planting setts from ratoon crops showing any grassy shoot symptoms',
            'Maintain strict roguing of infected stools during the first 3 to 4 months of crop growth'
        ],
        'urgency': 'High'
    },
    'Sugarcane|Pokkah Boeng (Top Rot)': {
        'description': 'A fungal disease of sugarcane causing chlorotic leaf bases, mechanical twisting and crumpling of young leaves, knife-cut stem lesions, and fatal terminal top rot.',
        'cause': 'Fusarium fujikuroi species complex (Fusarium moniliforme / Gibberella fujikuroi, fungus); airborne pathogen; favored by warm, humid, rainy monsoon conditions (25-32°C) following a hot dry spell.',
        'symptoms': [
            'Chlorotic or whitish patches developing at the base of young unfolding spindle leaves',
            'Deformed, crumpled, wrinkled, and twisted leaves failing to unfold normally ("pokkah boeng" means twisted top)',
            'Transverse reddish-brown necrotic cracks and "knife-cut" lesions developing on the leaf sheath and stalk',
            'Top rot phase: growing point rots away completely, exuding a foul odor and causing terminal stalk death',
            'Excessive sprouting of lateral buds below the dead top, resulting in stunted, worthless canes'
        ],
        'spread': [
            'Airborne microconidia dispersed widely by wind currents and turbulent air during monsoon storms',
            'Rain splash washing spores into the open leaf spindle and leaf whorl',
            'Infected seed cane setts and surviving fungal inoculum on dry cane residues'
        ],
        'management': [
            'Cut and safely dispose of blighted top sections exhibiting early knife-cut symptoms',
            'Apply registered systemic fungicides (e.g., Carbendazim, Copper Oxychloride, or Mancozeb) directed into the central leaf spindle at the onset of monsoon showers',
            'Avoid excessive nitrogen top-dressings during the grand growth monsoon phase',
            'Provide balanced potash fertilization to strengthen spindle tissue'
        ],
        'prevention': [
            'Plant sugarcane cultivars demonstrating field resistance to Pokkah Boeng',
            'Select clean seed setts from disease-free seed nurseries',
            'Dip seed setts in a Carbendazim (0.1%) solution for 15 minutes prior to planting',
            'Ensure adequate field drainage to prevent high stagnant relative humidity'
        ],
        'urgency': 'Medium'
    },
    'Sugarcane|Red Rot': {
        'description': 'Known as the "cancer of sugarcane"; the most destructive fungal disease of sugarcane, causing internal reddening of stalk tissues with white transverse patches, alcoholic sour odor, and complete clump drying.',
        'cause': 'Colletotrichum falcatum (teleomorph Glomerella tucumanensis, fungus); favored by waterlogged soils, high temperatures (28-35°C), intermittent heavy rains, and susceptible monoculture varieties.',
        'symptoms': [
            'Third or fourth leaf from top shows yellowing and withering along margins, followed by drying of the entire crown',
            'Internal stalk shows deep red discoloration interrupted by diagnostic white crosswise patches or bands across split canes',
            'Cavities form inside affected stalks filled with greyish-white cottony fungal mycelium',
            'Stalks emit a distinct sour, alcoholic, fermentation odor when split open',
            'Stalks lose weight, hollow out, shrivel, lodge easily, and sugar recovery drops to near zero'
        ],
        'spread': [
            'Primary transmission through infected seed cane setts carrying dormant nodal mycelia',
            'Irrigation and flood waters carrying conidia from diseased fields to healthy plots',
            'Borer insect tunnels, cultivation wounds, and root primordia serving as fungal entry doors',
            'Infected crop debris and trash left in the field'
        ],
        'management': [
            'Immediately uproot and burn all dried clumps; never crush or leave red-rot infected stalks in the field',
            'Do not take ratoon crops from red-rot affected fields; plow up and burn stubble',
            'Avoid passing irrigation water through infected fields to uninfected cane plots',
            'Soak planting setts in Carbendazim (0.1%) or Trichoderma viride suspension before furrow placement'
        ],
        'prevention': [
            'Plant red rot-resistant sugarcane varieties released by sugarcane breeding institutes',
            'Strictly adopt certified disease-free nursery seed setts (heat-treated three-tier seed program)',
            'Practice 2 to 3-year crop rotation with wetland paddy, green manures, or pulses to break soil inoculum',
            'Maintain effective field drainage and manage stalk borer populations vigorously'
        ],
        'urgency': 'High'
    },
    'Sugarcane|Smut': {
        'description': 'A severe systemic fungal disease of sugarcane characterized by the emergence of a long, black, whip-like, curved structure from the terminal shoot, causing spindly tillers and total sugar loss.',
        'cause': 'Sporisorium scitamineum (syn. Ustilago scitaminea, fungus); favored by hot, dry weather (25-35°C) with low humidity that promotes teliospore wind dissemination.',
        'symptoms': [
            'Emergence of a long, unbranched, curved, black whip-like structure (whip smut) from the terminal apex of the stalk',
            'Whip structure is initially covered by a thin silvery membrane that ruptures to release billions of black powdery teliospores',
            'Affected stalks become exceptionally thin, elongated, and spindly with small, narrow leaves',
            'Profuse sprouting of lateral buds into thin, grassy, broom-like shoots along the stalk',
            'Severe stunting and complete failure of millable cane formation; ratoon crops are decimated'
        ],
        'spread': [
            'Wind-borne black teliospores carried over vast distances across the sugarcane belt',
            'Infected seed setts harboring dormant systemic mycelium in nodal buds',
            'Contaminated irrigation water, harvesting tools, and handling implements'
        ],
        'management': [
            'Carefully rogue infected stools before the silvery membrane ruptures; enclose whip in a polythene bag, cut stalk at base, and burn',
            'Do not ratoon smut-infected cane fields; plow under and destroy stubble',
            'Disinfect harvesting knives in 5% disinfectant solution',
            'Treat seed setts with Hot Water (52°C for 30 minutes) or dip in Triadimefon / Carbendazim (0.1%) solution'
        ],
        'prevention': [
            'Plant smut-resistant sugarcane cultivars recommended by regional research stations',
            'Procure seed setts exclusively from certified disease-free seed nurseries',
            'Practice 2 to 3-year crop rotations with non-graminaceous crops (legumes, cotton, vegetables)',
            'Avoid moisture stress during formative crop stages'
        ],
        'urgency': 'High'
    },
    'Sugarcane|Wilt': {
        'description': 'A devastating fungal vascular disease causing gradual yellowing, crown drying, pith hollowing, dirty red internal stalk discoloration, and severe cane weight loss.',
        'cause': 'Cephalosporium sacchari (and Fusarium sacchari complex, fungi); favored by prolonged drought followed by waterlogging, root borer damage, and nematode stress.',
        'symptoms': [
            'Leaves lose turgidity, turn dull pale yellow, wither, and dry out completely from the crown downward',
            'Canes shrink, lose moisture, wrinkle, become lightweight, and hollow out internally',
            'Splitting the cane reveals dull reddish to purple-brown vascular discoloration with boat-shaped cavities filled with white mycelium',
            'Distinct absence of the transverse white bands that characterize Red Rot',
            'Entire clumps dry up and lodge, causing severe tonnage reduction and juice quality deterioration'
        ],
        'spread': [
            'Use of infected seed setts taken from wilt-affected fields',
            'Soil-borne inoculum entering through root injuries and subterranean pest wounds (root borer, termites)',
            'Contaminated drainage and flood waters'
        ],
        'management': [
            'Uproot and burn wilted clumps; do not allow ratoon crops from affected stools',
            'Control soil-borne pests (root borers, termites, white grubs) using approved biological or chemical treatments to prevent entry wounds',
            'Apply Trichoderma viride or Trichoderma harzianum enriched farmyard manure into planting furrows',
            'Avoid alternating extremes of severe drought and prolonged water stagnation'
        ],
        'prevention': [
            'Plant certified wilt-resistant sugarcane varieties',
            'Dip seed setts in Carbendazim (0.1%) or Benomyl solution for 15-20 minutes before planting',
            'Practice minimum 2-year crop rotation with wetland paddy or non-host green manure crops',
            'Maintain balanced irrigation scheduling and provide deep drainage furrows'
        ],
        'urgency': 'High'
    },
    'Sugarcane|Stalk Rot': {
        'description': 'A complex fungal decay of mature sugarcane stalks causing internal tissue softening, dark discolored pith, lodging, and significant reduction in commercial cane sugar recovery.',
        'cause': 'Fungal stalk-rotting complex (including Phoma, Colletotrichum, and Fusarium species); favored by stalk wounds from borers or lodging, over-maturity, drought, or frost.',
        'symptoms': [
            'Internal stalk tissues become soft, spongy, water-soaked, and discolor to dull brown, grey, or dark red',
            'Cavities develop within the pith of internodes, often containing fungal mycelial mats',
            'Affected stalks become brittle and snap or lodge easily during windstorms',
            'Leaves on affected stalks turn chlorotic, dry prematurely, and die back from the tips',
            'Severe drop in juice brix, sucrose content, and purity, causing high post-harvest milling losses'
        ],
        'spread': [
            'Fungal entrance through mechanical wounds, frost cracks, stalk borer exit holes, and wind-snap injuries',
            'Infected stalk cuttings used as planting material',
            'Decaying crop trash and residues left in the field'
        ],
        'management': [
            'Harvest mature canes promptly without delaying past peak sucrose maturity',
            'Remove and safely dispose of lodged, borer-riddled, and rotting stalks before milling',
            'Control stalk borers and rodents diligently to prevent structural rind wounds',
            'Avoid over-irrigation or water stagnation near harvest'
        ],
        'prevention': [
            'Plant sturdy, lodging-resistant sugarcane cultivars with tough rinds',
            'Select healthy, sound seed setts free from internal discoloration or borer pinholes',
            'Provide balanced fertilizer nutrition; avoid excessive nitrogen that weakens stalk rind firmness',
            'Trash-mulch furrows properly and deep-plow old stubbles post-harvest'
        ],
        'urgency': 'High'
    },
    'Tomato|Bacterial Spot': {
        'description': 'A widespread bacterial disease affecting tomato leaves, stems, and fruits, causing small dark water-soaked spots with yellow halos, defoliation, and scabby unmarketable fruit spots.',
        'cause': 'Xanthomonas perforans, Xanthomonas euvesicatoria, and Xanthomonas gardneri (bacteria); favored by warm temperatures (24-30°C), driving rains, high humidity, and overhead irrigation.',
        'symptoms': [
            'Small, dark brown to black circular or angular water-soaked lesions on leaves, often encircled by yellow halos',
            'Lesions coalesce on foliage, giving leaves a blighted, scorched appearance followed by severe leaf drop',
            'Leaves at plant tops appear ragged and blighted, exposing developing fruit to sunscald',
            'Fruit lesions start as tiny black raised blisters, expanding into dark brown, sunken, scabby, rough spots with pale margins',
            'Elongated dark canker-like spots on stems and petioles'
        ],
        'spread': [
            'Contaminated commercial tomato seed and infected nursery transplants',
            'Wind-driven rain, sprinkler droplets, and splashing moisture from soil',
            'Farm workers and equipment moving through wet fields',
            'Survival in volunteer tomato plants and solanaceous weeds (black nightshade)'
        ],
        'management': [
            'Apply registered copper-based bactericides (e.g., Copper Hydroxide) tank-mixed with Mancozeb to enhance bacterial kill and manage copper resistance',
            'Spray biologicals like Bacillus subtilis or bacteriophages formulated for Xanthomonas spot',
            'Avoid handling, staking, or pruning tomato plants when the foliage is wet',
            'Immediately rogue and destroy heavily spotted seedlings in nursery trays'
        ],
        'prevention': [
            'Use certified pathogen-free, hot water-treated seed (50°C for 25 minutes)',
            'Plant bacterial spot-resistant tomato varieties where adapted',
            'Implement 2 to 3-year crop rotations away from peppers and tomatoes',
            'Utilize drip irrigation and plastic mulch to eliminate soil splash onto lower foliage'
        ],
        'urgency': 'High'
    },
    'Tomato|Late Blight': {
        'description': 'An extremely destructive and rapidly progressing oomycete disease that can decimate entire tomato fields within days, causing large water-soaked greasy lesions, white spore mold, and firm brown fruit rot.',
        'cause': 'Phytophthora infestans (oomycete); favored by cool to moderate temperatures (12-22°C), high humidity (>90%), persistent rainfall, heavy morning fogs, and dew.',
        'symptoms': [
            'Large, irregular, water-soaked, pale green to greasy brownish-black lesions on leaves and stems',
            'Delicate, snowy-white downy fungal growth appears on the undersides of leaves and around lesion margins in humid conditions',
            'Stems develop dark brown to greasy black girdling lesions, causing rapid vine collapse',
            'Fruit symptoms: large, firm, greasy olive-brown to bronze sunken lesions with rough surfaces',
            'Entire fields can turn black, shrivel, rot, and emit a distinct foul decay odor within 3 to 7 days'
        ],
        'spread': [
            'Airborne sporangia transported across dozens of kilometers on cool, cloudy, humid wind currents',
            'Infected potato tubers and infected tomato transplants introduced into clean areas',
            'Rain splash and run-off spreading zoospores between adjacent plants'
        ],
        'management': [
            'Act immediately: apply targeted late-blight fungicides (e.g., Metalaxyl-Mancozeb, Cymoxanil, Dimethomorph, Mandipropamid, or Fluopicolide) upon first regional disease warnings',
            'Remove and securely bag heavily infected plants and fruits; burn or deep-bury them immediately',
            'Never compost late-blight infected plant material',
            'Destroy nearby volunteer potatoes and cull piles which serve as primary disease incubators'
        ],
        'prevention': [
            'Plant late-blight resistant tomato cultivars carrying Ph-2 and Ph-3 resistance genes',
            'Ensure wide plant spacing and trellising to promote rapid drying of foliage after rain',
            'Avoid overhead sprinkler irrigation; always use drip irrigation under plastic mulch',
            'Monitor regional late-blight forecasting and advisory alerts closely during cool wet seasons'
        ],
        'urgency': 'Critical'
    },
    'Tomato|Early Blight': {
        'description': 'A very common fungal disease of tomatoes attacking foliage, stems, and fruits, producing distinctive dark concentric target-board rings, yellow halos, lower leaf defoliation, and fruit stem-end rot.',
        'cause': 'Alternaria solani and Alternaria alternata (fungi); favored by warm temperatures (24-29°C), heavy dews, frequent rain, and plants under heavy fruit load or nutrient stress.',
        'symptoms': [
            'Small, dark brown to black spots appearing first on older lower leaves closest to the ground',
            'Spots enlarge (up to 15 mm) and develop distinct concentric rings resembling a target board or tree growth rings',
            'A vibrant yellow chlorotic halo surrounds each lesion; adjacent lesions merge, causing yellowing and drying of entire leaves',
            'Severe leaf defoliation progresses from the bottom upward, exposing fruits to solar sunscald',
            'Dark, sunken, leathery lesions with concentric rings at the stem-end calyx attachment on green and ripe fruit'
        ],
        'spread': [
            'Airborne conidia transported by wind currents and rain splash from soil debris',
            'Contaminated tomato seed and infected nursery transplants',
            'Fungal mycelium and spores overwintering on decaying tomato, potato, and nightshade residues'
        ],
        'management': [
            'Prune and remove infected lower leaves as soon as target lesions appear; destroy all cuttings',
            'Apply registered fungicides (e.g., Chlorothalonil, Mancozeb, Azoxystrobin, Difenoconazole, or Boscalid) as per label instructions',
            'Stake and trellis tomato plants to keep foliage off the ground and improve airflow',
            'Apply balanced fertilizer; avoid nitrogen deficiency which triggers early foliage senescence'
        ],
        'prevention': [
            'Apply thick straw or black plastic mulch around plants to create a physical barrier against rain-splashed soil spores',
            'Practice 3-year crop rotation avoiding all solanaceous crops (tomatoes, potatoes, eggplants, peppers)',
            'Water plants at ground level using drip irrigation early in the day',
            'Select certified disease-free seeds and vigorous resistant hybrid cultivars'
        ],
        'urgency': 'High'
    },
    'Tomato|Leaf Mold': {
        'description': 'A high-humidity fungal disease of tomatoes, especially destructive in greenhouses and polyhouses, causing pale yellow spots on upper leaf surfaces and velvety olive-green to brown mold underneath.',
        'cause': 'Passalora fulva (syn. Cladosporium fulvum, fungus); favored by high relative humidity (>85%) and moderate temperatures (20-25°C); rarely severe in dry outdoor climates.',
        'symptoms': [
            'Pale green to vibrant yellow chlorotic spots with indefinite margins on the upper leaf surface of older lower leaves',
            'Dense, velvety, olive-green to chocolate-brown fungal mold growth directly underneath the spots on lower leaf surfaces',
            'Infected leaves curl, wither, turn golden-brown, desiccate, and drop prematurely',
            'Defoliation moves upward, stunting plant development and drastically reducing fruit size and yield',
            'Rarely, black leathery stem-end rot on green or ripe fruits'
        ],
        'spread': [
            'Massive numbers of dry conidia transported easily by air currents, clothing, and tools',
            'High relative humidity and stagnant air trapped inside greenhouses and high tunnels',
            'Conidia and sclerotia surviving on greenhouse frames, wooden stakes, and dry plant residues'
        ],
        'management': [
            'Increase greenhouse ventilation immediately; operate exhaust fans and horizontal airflow fans to reduce humidity below 80%',
            'Prune lower leaves to improve canopy ventilation and allow light penetration',
            'Apply registered fungicides (e.g., Copper Hydroxide, Chlorothalonil, Mancozeb, or Difenoconazole) ensuring thorough coverage of leaf undersides',
            'Spray bio-fungicides like Bacillus amyloliquefaciens or Trichoderma harzianum preventively'
        ],
        'prevention': [
            'Grow tomato varieties possessing Cf resistance genes (Cf-4, Cf-9, etc.) bred for greenhouse production',
            'Space plants adequately; prune suckers regularly to prevent dense tangled canopies',
            'Heat and ventilate greenhouses before sunset to prevent condensation and dew on leaves overnight',
            'Thoroughly sanitize greenhouse structures, trellising strings, and pots between cropping cycles'
        ],
        'urgency': 'High'
    },
    'Tomato|Septoria Leaf Spot': {
        'description': 'A very destructive foliar fungal disease of tomatoes causing numerous small circular spots with dark borders and grey centers speckled with tiny black fruiting bodies, leading to rapid defoliation.',
        'cause': 'Septoria lycopersici (fungus); favored by warm temperatures (20-26°C), persistent wet weather, heavy rainfall, high humidity, and dense unpruned canopies.',
        'symptoms': [
            'Numerous tiny, water-soaked circular spots (2-3 mm) appearing on the lowest leaves first after fruit set',
            'Spots develop dark brown margins with pale grey or tan centers',
            'Diagnostic feature: tiny, black, pepper-like specks (pycnidia) clearly visible inside the grey centers of lesions',
            'Individual leaves may harbor hundreds of spots, turning yellow, curling, withering, and dropping off',
            'Plant becomes stripped of foliage from the ground up, leaving bare stems and sun-scalded fruits'
        ],
        'spread': [
            'Rain splash and splashing overhead sprinkler water propelling pycnidiospores upward onto leaves',
            'Insects, farm implements, and workers handling wet foliage',
            'Fungal pycnidia overwintering in dead tomato debris and solanaceous weeds (horsenettle, nightshade)'
        ],
        'management': [
            'Strip and discard severely spotted lower leaves; do not allow infected leaves to touch the soil',
            'Apply registered protective fungicides (e.g., Chlorothalonil, Mancozeb, Copper Oxychloride, or Pyraclostrobin) at first symptom appearance',
            'Avoid working in tomato fields when leaves are wet with dew or rain',
            'Stake, cage, and prune tomato plants to elevate all foliage well above the soil surface'
        ],
        'prevention': [
            'Apply organic or plastic mulch around the base of plants to block soil-splash spore dispersal',
            'Practice 3-year crop rotation avoiding tomatoes, potatoes, and eggplants',
            'Water exclusively via drip irrigation under the mulch layer',
            'Plow under or remove and burn all tomato crop debris immediately following harvest'
        ],
        'urgency': 'Medium'
    },
    'Tur (Pigeon Pea)|Phytophthora Blight': {
        'description': 'A devastating soil-borne and water-borne oomycete disease of pigeon pea / tur causing sudden wilting, dark water-soaked stem girdling cankers, and rapid plant death following heavy monsoon rains.',
        'cause': 'Phytophthora cajani (oomycete); favored by waterlogged soil, poor drainage, warm humid weather (25-30°C), and continuous heavy rainfall during early vegetative growth.',
        'symptoms': [
            'Water-soaked lesions on young leaves that turn brown, shrivel, and dry rapidly',
            'Dark brown to purplish-black necrotic cankers on the main stem and branches, particularly near the soil line',
            'Stem lesions girdle the stem; the stem swells slightly above the canker and breaks easily in wind',
            'Foliage above the girdling canker wilts suddenly, turns dull brown, and dies while remaining attached to branches',
            'Whole patches of pigeon pea plants wilt, collapse, and die in field depressions within days after heavy rain'
        ],
        'spread': [
            'Motile biflagellate zoospores swimming through waterlogged, saturated soils',
            'Splashing rainwater and surface runoff washing spores across field contours',
            'Thick-walled oospores persisting in infested field soil and crop residues for multiple seasons'
        ],
        'management': [
            'Improve field drainage immediately by digging deep drainage trenches to discharge standing water',
            'Rogue and burn dead or dying blighted plants to prevent zoospore multiplication',
            'Drench soil around affected patches with Metalaxyl-Mancozeb or Copper Oxychloride where registered',
            'Avoid cultivating or disturbing soil while fields are saturated'
        ],
        'prevention': [
            'Plant pigeon pea on raised broad beds and furrows (BBF system) or ridge-and-furrow systems to prevent waterlogging',
            'Grow Phytophthora blight-resistant cultivars (e.g., varieties released by ICRISAT and national programs)',
            'Treat seeds with Metalaxyl (e.g., Apron 35 SD at 3 g/kg seed) or Trichoderma viride before sowing',
            'Rotate pigeon pea with non-host crops such as sorghum, pearl millet, or maize'
        ],
        'urgency': 'Critical'
    },
    'Tur (Pigeon Pea)|Fusarium Wilt': {
        'description': 'A major vascular wilt disease of pigeon pea causing progressive leaf yellowing, flaccidity, irreversible wilting, and a diagnostic purple-brown band on the main stem extending upward from soil level.',
        'cause': 'Fusarium udum (fungus); soil-borne vascular pathogen; favored by warm soil temperatures (20-25°C) and plants entering the reproductive and pod-filling stages.',
        'symptoms': [
            'Foliar yellowing and loss of turgidity, starting on lower leaves and moving up to terminal branches',
            'A diagnostic, prominent, continuous purple-brown vertical band or strip running upward along the stem from ground level',
            'When the stem bark is peeled back or split, dark brown to black vascular discoloration of the xylem is revealed',
            'Partial wilt: one side or single branch of the plant wilts and dies while the other side remains temporarily green',
            'Total wilting and death of the entire plant with dry brown leaves remaining attached to dead branches'
        ],
        'spread': [
            'Long-lived chlamydospores surviving in field soil for 3 to 5 years',
            'Movement of infested soil on tillage tools, boots, and irrigation water',
            'Infected crop roots and stubble remaining in the soil after harvest',
            'Synergistic interaction with pigeon pea cyst nematodes (Heterodera cajani)'
        ],
        'management': [
            'Uproot and burn wilted plants including root systems; do not leave dead stems in fields',
            'Apply Trichoderma viride or Trichoderma harzianum enriched farmyard manure into seed furrows',
            'Avoid root damage during intercultural weeding operations',
            'Note: Foliar and chemical sprays are ineffective against established vascular Fusarium wilt'
        ],
        'prevention': [
            'Sow wilt-resistant pigeon pea varieties (e.g., Asha / ICPL 87119, BSMR 736, Maruti / ICP 8863)',
            'Practice 3 to 4-year crop rotations with non-host crops; intercropping with sorghum or corn significantly suppresses wilt',
            'Perform deep summer plowing during hot dry months to expose pathogen resting spores to solar heat',
            'Dress seeds with Carbendazim + Thiram (1:1 at 2 g/kg seed) or Trichoderma viride (10 g/kg seed)'
        ],
        'urgency': 'High'
    },
    'Wheat|Leaf Rust': {
        'description': 'Also known as brown rust; the most common fungal rust of wheat, producing small round orange-brown pustules scattered randomly across leaf blades, reducing grain size and photosynthetic capacity.',
        'cause': 'Puccinia triticina (fungus); macrocyclic heteroecious rust; favored by moderate temperatures (15-25°C), high relative humidity, and at least 6-8 hours of free leaf moisture/dew.',
        'symptoms': [
            'Small, circular to oval, bright orange-brown to reddish pustules (uredinia) scattered randomly on upper leaf surfaces',
            'Pustules rupture the leaf epidermis, releasing powdery orange spores that rub off easily on fingers or clothing',
            'Chlorotic halos encircle individual pustules as infection progresses',
            'Heavy infection causes extensive leaf yellowing, desiccation, premature leaf death, and shriveled grains',
            'Late in the season, pustules turn dark brown to black (telia) as plants mature'
        ],
        'spread': [
            'Urediniospores carried across thousands of kilometers on high-altitude wind currents ("Puccinia pathways")',
            'Heavy overnight dew and rainfall providing free water for spore germination',
            'Volunteer wheat plants and susceptible grassy weeds sustaining green bridges between seasons'
        ],
        'management': [
            'Scout wheat fields weekly starting from tillering through boot and grain-fill stages',
            'Apply registered triazole or strobilurin fungicides (e.g., Propiconazole, Tebuconazole, or Azoxystrobin) if rust pustules appear on flag leaves before flowering',
            'Destroy volunteer wheat plants and wild grasses along field edges before the main season',
            'Avoid excessive late-season nitrogen applications that keep leaf tissues succulent and vulnerable'
        ],
        'prevention': [
            'Plant rust-resistant wheat varieties recommended for the regional agro-climatic zone (bearing Lr resistance genes)',
            'Sow wheat at the optimal regional planting window; avoid delayed late sowings that expose crops to warm rust weather',
            'Maintain balanced NPK fertilization with adequate potash to enhance disease tolerance',
            'Participate in regional varietal deployment to avoid large monoculture blocks of identical susceptibility'
        ],
        'urgency': 'Medium'
    },
    'Wheat|Fusarium Head Blight': {
        'description': 'Also known as scab; a devastating fungal disease of wheat heads causing premature bleaching of spikelets, pink/orange spore masses, shriveled "tombstone" kernels, and harmful mycotoxin (DON) accumulation.',
        'cause': 'Fusarium graminearum species complex (fungus); favored by warm, humid or rainy weather (20-30°C) with persistent fog or heavy dew during wheat flowering (anthesis).',
        'symptoms': [
            'Premature bleaching or whitening of individual spikelets or entire head sections while the rest of the head remains green',
            'Salmon-pink to orange spore masses (sporodochia) visible along the base and margins of infected glumes in damp weather',
            'Infected rachis turns brown and purplish, choking water and nutrient supply to all spikelets above the infection point',
            'Grains produced are shriveled, lightweight, bleached-white or chalky-pink ("tombstone" kernels)',
            'Grains contain dangerous mycotoxins including deoxynivalenol (DON/vomitoxin), making grain unfit for human or animal consumption'
        ],
        'spread': [
            'Airborne ascospores and rain-splashed conidia blown from infected corn stubble and small grain residues',
            'Direct infection of exposed anthers and florets during anthesis (flowering stage)',
            'Corn-wheat rotations without residue management providing vast local spore reservoirs'
        ],
        'management': [
            'Monitor weather forecasts closely at the onset of flowering (Feekes 10.5.1)',
            'Apply targeted triazole fungicides (e.g., Prothioconazole, Tebuconazole, or Metconazole) specifically during early flowering; note: strobilurins must NOT be used as they can increase mycotoxin levels',
            'Calibrate sprayers with forward-and-backward angled nozzles to coat both sides of wheat heads',
            'Clean harvested grain thoroughly with gravity separators to blow out lightweight infected tombstone kernels'
        ],
        'prevention': [
            'Avoid planting wheat directly into unmanaged corn stubble; chop and deep-plow corn residues',
            'Grow moderately resistant wheat varieties containing Fhb1 or other scab-resistance QTLs',
            'Practice 2-year crop rotations with non-cereal crops (soybeans, canola, or pulses)',
            'Stagger planting dates or use varieties with differing flowering dates to minimize peak weather vulnerability'
        ],
        'urgency': 'Critical'
    },
    'Wheat|Powdery Mildew': {
        'description': 'A common foliar fungal disease of wheat producing white fluffy to powdery colonies on leaves and stems, turning grey with tiny black specks, causing leaf yellowing, lodging, and reduced head filling.',
        'cause': 'Blumeria graminis f. sp. tritici (fungus); obligate parasite; favored by cool to moderate temperatures (15-22°C), high relative humidity (85-100%), dense canopies, and heavy nitrogen fertilization.',
        'symptoms': [
            'White, fluffy, cottony fungal colonies appearing on the upper surface of lower leaves and leaf sheaths',
            'Colonies expand and merge into a thick, powdery white-to-grey mat coating entire leaf blades',
            'Yellow chlorotic patches develop on the reverse side of leaves beneath the powdery colonies',
            'Infected leaves turn brown, senesce, and die prematurely from the bottom upward',
            'Tiny, dark brown to black spherical resting structures (chasmothecia) dot the aging grey powdery mats'
        ],
        'spread': [
            'Wind-borne conidia produced in millions and transported over regional wheat fields',
            'High relative humidity and stagnant air trapped inside dense, heavily fertilized wheat canopies',
            'Chasmothecia overwintering on dry crop debris and volunteer wheat plants'
        ],
        'management': [
            'Apply registered fungicides (e.g., Propiconazole, Tebuconazole, or Azoxystrobin) if mildew spreads to the upper two leaves before heading',
            'Avoid excessive nitrogen fertilizer; split applications to prevent dense, succulent, susceptible vegetative growth',
            'Ensure optimal seed rates to avoid overly dense, crowded plant populations',
            'Destroy volunteer wheat plants in fallow borders before sowing'
        ],
        'prevention': [
            'Sow powdery mildew-resistant wheat cultivars containing Pm resistance genes',
            'Maintain balanced crop nutrition with adequate potassium and silica to strengthen cell wall barriers',
            'Adopt recommended row spacing to ensure adequate light and air circulation through the canopy',
            'Rotate crops with non-graminaceous species'
        ],
        'urgency': 'Medium'
    },
    'Wheat|Septoria Leaf Blotch': {
        'description': 'A major fungal leaf blotch disease of wheat producing irregular brown to tan blotches packed with tiny diagnostic black pycnidia, causing severe leaf blighting, premature senescence, and shriveled grains.',
        'cause': 'Zymoseptoria tritici (syn. Septoria tritici, fungus); favored by cool, wet, windy weather (15-20°C) with persistent rains, splashing water droplets, and high canopy humidity.',
        'symptoms': [
            'Small, chlorotic, water-soaked oval spots appearing first on lower leaves in contact with the ground',
            'Spots elongate into irregular, parallel-sided, tan to reddish-brown necrotic blotches bounded by leaf veins',
            'Diagnostic feature: numerous tiny, black, pimple-like pycnidia clearly visible inside the mature blotches',
            'Blotches coalesce to cover large portions of the leaf blade, killing leaves prematurely',
            'Under continuous wet conditions, disease climbs upward onto the critical flag leaf and upper canopy'
        ],
        'spread': [
            'Rain splash and splashing water droplets catapulting pycnidiospores upward from lower leaves to upper leaves',
            'Wind-borne ascospores discharged from pseudothecia on decomposing wheat stubble',
            'Overwintering mycelium on volunteer wheat seedlings and wheat straw left on the soil surface'
        ],
        'management': [
            'Scout upper leaves carefully between jointing and flag leaf emergence stages',
            'Apply registered fungicides (e.g., Prothioconazole, Propiconazole, or Pyraclostrobin) at flag leaf emergence (Feekes 8-9) if weather is wet and lesions are present on lower leaves',
            'Rotate fungicide modes of action to manage fungicide resistance in Septoria populations',
            'Incorporate crop residues by deep tillage to accelerate breakdown of infected stubble'
        ],
        'prevention': [
            'Plant Septoria-resistant wheat cultivars suited to high-rainfall environments',
            'Practice minimum 2-year crop rotation avoiding continuous back-to-back wheat plantings',
            'Avoid excessively high seeding rates that create dense, slow-drying leaf canopies',
            'Time nitrogen applications carefully to avoid over-luxuriant early vegetative growth'
        ],
        'urgency': 'High'
    },
    'Wheat|Stripe Rust': {
        'description': 'Also known as yellow rust; one of the most destructive cold-weather fungal diseases of wheat, producing bright yellow-orange pustules arranged in distinctive narrow stripes along leaf veins.',
        'cause': 'Puccinia striiformis f. sp. tritici (fungus); favored by cool temperatures (10-18°C), high humidity, frequent rainfall, and heavy dew; arrested when temperatures rise above 25°C.',
        'symptoms': [
            'Bright yellow to orange-yellow powdery pustules (uredinia) neatly arranged in long, linear, parallel stripes along leaf veins',
            'Pustules form on both sides of leaf blades, leaf sheaths, stems, and glumes of wheat heads',
            'Epidermis ruptures, shedding copious yellow powdery spores onto boots, clothing, and field implements',
            'Severe infections cause complete leaf yellowing, scorch, drying, and total leaf death',
            'Heavily infected fields appear yellow and scorched from a distance; grain is severely shriveled with up to 80-100% yield loss'
        ],
        'spread': [
            'Airborne urediniospores carried hundreds of kilometers on cool, moist wind currents',
            'Cool nights with dew and daytime temperatures between 10-18°C promoting rapid cycling (7-10 days)',
            'Overwintering and oversummering mycelium on volunteer wheat and wild grasses at higher elevations or cool valleys'
        ],
        'management': [
            'Act immediately: stripe rust is fast-moving; scout fields during tillering, jointing, and flag leaf stages',
            'Apply registered triazole fungicides (e.g., Propiconazole, Tebuconazole, or Difenoconazole) upon finding the first focal patches of yellow stripe pustules',
            'Ensure complete spray coverage of flag leaves and upper canopies using adequate water volumes (200 L/ha)',
            'Destroy volunteer wheat plants in offseason fallows'
        ],
        'prevention': [
            'Plant yellow rust-resistant wheat varieties carrying effective Yr resistance genes (e.g., adult plant resistance genes)',
            'Diversify wheat varieties across farming tracts to prevent rapid emergence of virulent new rust races',
            'Avoid very early sowings in areas prone to autumn stripe rust infections',
            'Apply balanced fertilizers and avoid excessive nitrogen which delays maturity and promotes succulent tissue'
        ],
        'urgency': 'High'
    },
    'Bajra (Pearl Millet)|Anthracnose': {
        'description': 'A damaging fungal disease of pearl millet attacking leaves, leaf sheaths, and stems, producing circular to elongated reddish-brown lesions that coalesce, cause leaf blight, and reduce fodder/grain yield.',
        'cause': 'Colletotrichum graminicola (and Colletotrichum sublineolum, fungi); favored by warm, humid weather (26-32°C), intermittent monsoon showers, and dense crop canopies.',
        'symptoms': [
            'Small, circular to elliptical, reddish-brown or purple-bordered lesions on leaf blades and sheaths',
            'Lesions enlarge with straw-colored or tan centers bearing tiny black fruiting bodies (acervuli) with dark bristles (setae)',
            'Adjacent lesions merge into large necrotic stripes, causing extensive foliar blighting and drying',
            'Stem lesions cause internal stalk rot, weakening stalks and predisposing plants to lodging',
            'Poor grain formation and premature drying of the head'
        ],
        'spread': [
            'Wind-blown conidia and rain splash dispersing spores across the crop canopy',
            'Seed-borne fungal inoculum and survival in infected crop stubble left on the soil surface',
            'Alternative grassy hosts and volunteer pearl millet seedlings'
        ],
        'management': [
            'Remove and burn heavily infected crop residues after harvest to reduce overwintering acervuli',
            'Apply registered protectant or systemic fungicides (e.g., Mancozeb or Carbendazim) if early lesions threaten seed production fields',
            'Ensure adequate plant spacing and field ventilation',
            'Practice balanced fertilization; avoid excess nitrogen'
        ],
        'prevention': [
            'Plant anthracnose-resistant pearl millet cultivars and hybrids',
            'Treat seeds with Thiram or Carbendazim (2 g/kg seed) before sowing',
            'Rotate with non-graminaceous crops (pulses, legumes, oilseeds) for at least 2 years',
            'Maintain weed-free field borders to eliminate wild grass hosts'
        ],
        'urgency': 'Medium'
    },
    'Bajra (Pearl Millet)|Downy Mildew': {
        'description': 'Also known as "green ear disease"; the most devastating disease of pearl millet, causing systemic chlorosis, stunted tillers, and bizarre floral transformation of grain heads into leafy green tufts.',
        'cause': 'Sclerospora graminicola (oomycete); soil-borne and seed-borne; favored by warm temperatures (20-28°C), high relative humidity (>90%), and wet monsoon soil conditions.',
        'symptoms': [
            'Systemic chlorosis: yellow or white streaks running parallel along young leaf blades, starting from the leaf base',
            'Downy white fungal growth visible on the lower surfaces of chlorotic leaf areas during cool, humid mornings',
            'Leaves become chlorotic, twisted, crinkled, shredded, and dry into longitudinal brown ribbons',
            'Green ear symptom: floral parts of the earhead are transformed into green leafy structures (phyllody), making the ear look like a green bottle-brush',
            'Severely infected plants are stunted, produce excessive tillers, and yield zero grain'
        ],
        'spread': [
            'Thick-walled oospores persisting in soil for 5 to 8 years and contaminating seed surfaces',
            'Airborne sporangia released at night in humid conditions causing secondary leaf infections',
            'Infected crop residues and volunteer seedlings'
        ],
        'management': [
            'Rogue out and destroy systemically infected chlorotic seedlings and green-ear plants before sporangia form',
            'Apply registered foliar fungicides (e.g., Metalaxyl-Mancozeb) at 20-25 days after sowing if downy symptoms appear',
            'Deep-plow crop residues immediately after harvest to bury oospores deeply into the soil',
            'Avoid collecting seed from fields showing any downy mildew incidence'
        ],
        'prevention': [
            'Grow downy mildew-resistant pearl millet hybrids released by agricultural research institutes (ICRISAT)',
            'Treat seeds with Metalaxyl (e.g., Apron 35 SD at 4-6 g/kg seed) or biological formulations before sowing',
            'Practice 3-year crop rotation with non-host crops (pulses, cotton, groundnut)',
            'Transplant healthy seedlings from clean nursery beds where transplanting is practiced'
        ],
        'urgency': 'High'
    },
    'Bajra (Pearl Millet)|Leaf Rust': {
        'description': 'A foliar fungal disease of pearl millet producing reddish-brown to orange-brown pustules on both leaf surfaces, causing premature drying of foliage and reducing fodder and grain yield.',
        'cause': 'Puccinia substriata (syn. Puccinia penniseti, fungus); favored by warm temperatures (22-30°C), intermittent rains, high humidity, and prolonged morning dews.',
        'symptoms': [
            'Small, circular to elongated, bright reddish-brown to cinnamon pustules (uredinia) scattered on both leaf surfaces',
            'Pustules erupt through the leaf surface, shedding powdery brownish spores when touched',
            'Chlorosis develops around pustules; severe infections coalesce into extensive dry necrotic zones',
            'Leaves dry up prematurely, progressing from lower leaves to the flag leaf',
            'Late in the season, pustules turn dark brown to black (telia); grains remain small and shriveled'
        ],
        'spread': [
            'Airborne urediniospores carried across fields by wind currents',
            'High relative humidity and surface dew providing moisture for spore germination',
            'Alternative hosts (such as Solanum species including Solanum melongena) supporting the sexual cycle'
        ],
        'management': [
            'Apply registered foliar fungicides (e.g., Mancozeb or Wettable Sulphur) at the first sighting of rust pustules in seed production blocks',
            'Harvest early for fodder if rust is severe during late vegetative growth to salvage forage quality',
            'Destroy volunteer pearl millet plants and weed hosts',
            'Incorporate crop residues post-harvest'
        ],
        'prevention': [
            'Sow rust-resistant or rust-tolerant pearl millet hybrids',
            'Plant early in the season to allow crops to mature before peak rust spore buildup in late monsoon',
            'Maintain optimal plant density and balanced fertilization',
            'Rotate fields with non-host leguminous crops'
        ],
        'urgency': 'Medium'
    },
    'Bajra (Pearl Millet)|Leaf Spot': {
        'description': 'A common foliar fungal spot disease of pearl millet causing oval to irregular brown lesions with chlorotic borders, leading to blighting of functional leaf area and lowered fodder quality.',
        'cause': 'Bipolaris setariae and Pyricularia grisea (fungi); favored by warm temperatures (25-32°C), high humidity, and overcast rainy monsoon weather.',
        'symptoms': [
            'Small, oval to oblong water-soaked spots on leaves that turn greyish-brown with dark brown margins',
            'Spots expand, coalesce, and form large irregular necrotic blighted patches across the leaf lamina',
            'Extensive leaf yellowing and premature leaf drying from bottom to top',
            'Lesions on leaf sheaths and peduncles causing stalk weakness and reduced grain filling',
            'Seedlings suffer from seedling blight and damping-off when infected seeds are sown'
        ],
        'spread': [
            'Airborne conidia dispersed by wind and splashing rainwater',
            'Internally and externally seed-borne on infected grain',
            'Fungal survival on infected millet crop residues and wild graminaceous weeds'
        ],
        'management': [
            'Apply registered protectant fungicides (e.g., Mancozeb or Ziram) at early disease onset if economically justified',
            'Remove and bury infected crop residues after harvest to eliminate overwintering conidia',
            'Maintain balanced plant nutrition with adequate potassium',
            'Avoid dense overcrowding of seedlings'
        ],
        'prevention': [
            'Use certified disease-free seed treated with Thiram or Captan (2 g/kg seed)',
            'Select leaf spot-tolerant pearl millet cultivars',
            'Practice 2-year crop rotation with non-cereal crops (mungbean, cowpea, groundnut)',
            'Ensure good field drainage to avoid stagnant high humidity'
        ],
        'urgency': 'Medium'
    },
    'Groundnut|Leaf Disease': {
        'description': 'A broad diagnostic classification indicating foliar disease symptoms on groundnut (peanut), most commonly representing Early Leaf Spot (Cercospora arachidicola), Late Leaf Spot (Phaeoisariopsis personata), or Rust (Puccinia arachidis). Confirm exact symptoms before selecting a specific fungicide.',
        'cause': 'Foliar fungal pathogen complex; typically Cercospora arachidicola (early spot), Phaeoisariopsis personata (late spot), or Puccinia arachidis (rust); favored by warm temperatures (24-30°C) and high humidity.',
        'symptoms': [
            'Early leaf spot: circular reddish-brown spots with prominent bright yellow halos on upper leaf surfaces',
            'Late leaf spot: smaller, darker brown to jet-black circular spots mostly on lower leaf surfaces without distinct halos',
            'Groundnut rust: small orange-brown powdery pustules on leaf undersides accompanied by yellowing on upper surfaces',
            'Extensive leaf yellowing, chlorosis, and severe premature defoliation leaving bare stems',
            'Substantial reduction in pod number, pod filling, seed weight, and haulm quality'
        ],
        'spread': [
            'Airborne conidia and urediniospores carried by wind currents across peanut tracts',
            'Rain splash distributing spores from soil and lower foliage upward',
            'Overwintering fungal mycelium and conidia on infected crop residues and volunteer groundnut plants'
        ],
        'management': [
            'Confirm the exact causal disease (early spot vs. late spot vs. rust) before selecting a specific chemical treatment',
            'Apply registered broad-spectrum fungicides (e.g., Mancozeb, Chlorothalonil, Tebuconazole, or Carbendazim) covering both upper and lower leaf surfaces according to label recommendations',
            'Apply neem seed kernel extract (NSKE 5%) or Trichoderma formulations for biological suppression',
            'Ensure timely application at the 40-45 day and 60-65 day crop stages when leaf diseases typically appear'
        ],
        'prevention': [
            'Plant foliar disease-resistant or tolerant groundnut varieties recommended by agricultural universities',
            'Practice crop rotation with non-leguminous crops (sorghum, pearl millet, maize) for 2 seasons',
            'Perform seed dressing with Thiram + Carbendazim (1:1 at 2 g/kg seed) before sowing',
            'Plow under crop residues immediately after harvest to speed up organic decomposition'
        ],
        'urgency': 'Confirm diagnosis'
    },
    'Jowar (Sorghum)|Leaf Spot': {
        'description': 'A foliar fungal disease complex of grain and fodder sorghum producing circular to elliptical brown or purple-bordered lesions, causing leaf blighting, premature drying, and reduced grain/forage quality.',
        'cause': 'Bipolaris sorghicola, Cercospora sorghi, or Exserohilum turcicum (fungal leaf spot pathogens); favored by warm, humid, overcast weather (25-30°C) with intermittent rains.',
        'symptoms': [
            'Small, circular to elongated brown, tan, or reddish-purple lesions on leaf blades',
            'Lesions expand and coalesce into extensive necrotic blotches along leaf veins',
            'Chlorosis and yellowing around lesion margins progressing to complete leaf blighting and drying',
            'Lesions on leaf sheaths and midribs weakening structural support',
            'Lower leaves dry prematurely, reducing active green leaf area during grain filling'
        ],
        'spread': [
            'Airborne conidia carried by wind currents and turbulent storm fronts',
            'Rain splash dislodging spores from crop residues into the lower canopy',
            'Seed-borne fungal propagules and infected sorghum stubble left in fields'
        ],
        'management': [
            'Confirm the specific leaf spot type before selecting targeted chemical interventions',
            'Apply registered protectant fungicides (e.g., Mancozeb or Propiconazole) if lesions threaten seed crops before heading',
            'Incorporate or burn infected crop residues after harvest to eliminate field inoculum',
            'Maintain balanced crop nutrition; avoid excess nitrogen and potassium deficiency'
        ],
        'prevention': [
            'Plant leaf spot-resistant sorghum hybrids and varieties',
            'Dress seed with Thiram or Carbendazim (2-3 g/kg seed) before sowing',
            'Practice 2-year crop rotation with pulses (pigeon pea, chickpea) or oilseeds',
            'Maintain optimal plant spacing to allow sunlight penetration and air circulation'
        ],
        'urgency': 'Medium'
    },
    'Jowar (Sorghum)|Anthracnose': {
        'description': 'A major fungal disease of sorghum affecting leaves, stalks, and panicles, producing small circular to elongated reddish-purple lesions with black fruiting centers, causing lodging and panicle blasting.',
        'cause': 'Colletotrichum sublineolum (syn. Colletotrichum graminicola, fungus); favored by warm, humid, rainy monsoon conditions (25-32°C) with prolonged relative humidity (>85%).',
        'symptoms': [
            'Small, circular to elliptical spots with defined reddish, purple, or tan margins on leaves',
            'Centers of mature spots become bleached straw-colored and bear tiny black bristly cushions (acervuli)',
            'Lesions merge into large necrotic stripes, causing rapid leaf death and scorched foliage',
            'Stalk rot phase: internal stalk tissues develop red discoloration with dark fungal patches, causing severe stalk lodging',
            'Panicle phase: panicles produce discolored, lightweight, chalky, or shriveled grains'
        ],
        'spread': [
            'Wind-borne and rain-splashed conidia dispersing rapidly throughout the crop canopy',
            'Infected sorghum seed harboring internal and external fungal mycelia',
            'Survival in infected crop stubble, stalks, and wild sorghum grass (Sorghum halepense / Johnson grass)'
        ],
        'management': [
            'Apply registered foliar fungicides (e.g., Mancozeb, Carbendazim, or Propiconazole) if lesions appear before boot stage on valuable seed plots',
            'Collect and destroy infected crop residues and avoid leaving standing stubble over winter',
            'Eradicate wild Johnson grass and weed hosts along field boundaries',
            'Avoid high planting densities that generate stagnant humidity in the canopy'
        ],
        'prevention': [
            'Grow anthracnose-resistant sorghum hybrids and cultivars recommended for the production zone',
            'Treat seed with certified fungicides (e.g., Thiram + Carbendazim at 2 g/kg seed)',
            'Adopt 2 to 3-year crop rotations with non-host crops (soybeans, cotton, groundnuts)',
            'Provide balanced fertilizer nutrition; avoid high nitrogen top-dressings'
        ],
        'urgency': 'High'
    },
    'Jowar (Sorghum)|Leaf Rust': {
        'description': 'A widespread foliar fungal disease of sorghum producing reddish-brown to purple rust pustules on both leaf surfaces, reducing green photosynthetic area, forage quality, and grain yield.',
        'cause': 'Puccinia purpurea (fungus); favored by warm, humid weather (22-30°C), frequent monsoonal rains, and dense crop canopies.',
        'symptoms': [
            'Small, elongated, powdery reddish-brown to purple pustules (uredinia) erupting on both leaf surfaces',
            'Pustules are surrounded by distinct reddish, purple, or brown discolored halos depending on plant pigmentation',
            'Ruptured pustules shed powdery rust spores that leave colored stains when touched',
            'Coalescence of pustules causes large leaf sections to turn purple-brown, desiccate, and die prematurely',
            'Late in the season, dark purplish-black overwintering pustules (telia) appear across the leaf blade'
        ],
        'spread': [
            'Airborne urediniospores transported across long distances by wind currents',
            'High relative humidity and morning dew providing essential moisture for spore germination',
            'Alternative weed hosts and volunteer sorghum plants sustaining the fungus during offseason periods'
        ],
        'management': [
            'Apply registered fungicides (e.g., Mancozeb, Propiconazole, or Wettable Sulphur) if rust begins early and threatens flag leaves',
            'Harvest early for fodder if rust pressure is high during late grain filling to preserve forage nutrition',
            'Remove and plow under crop stubble after harvest',
            'Eradicate volunteer sorghum and wild grasses around fields'
        ],
        'prevention': [
            'Plant rust-resistant or rust-tolerant sorghum varieties and hybrids',
            'Sow early in the season to escape peak rust buildup in late monsoon',
            'Maintain optimal plant population to ensure good canopy ventilation',
            'Rotate fields with non-host pulse crops (pigeon pea, chickpea, cowpea)'
        ],
        'urgency': 'Medium'
    },
    'Ladyfinger (Okra)|Leaf Disease': {
        'description': 'A broad diagnostic classification for okra/ladyfinger foliage diseases, most frequently indicating Cercospora Leaf Spot, Powdery Mildew, Alternaria Blight, or Yellow Vein Mosaic Virus. Confirm the exact symptoms and cause before choosing a specific pesticide.',
        'cause': 'Foliar disease complex; can be fungal (Cercospora malayensis, Erysiphe cichoracearum, Alternaria) or viral (Bhendi Yellow Vein Mosaic Virus transmitted by whiteflies); favored by warm humid weather.',
        'symptoms': [
            'Cercospora spot: brown circular to irregular leaf spots with grey centers and dark margins',
            'Powdery mildew: white talcum-like powdery patches on upper and lower leaf surfaces',
            'Yellow vein mosaic: bright golden-yellow vein clearing and network pattern on leaf blades with stunted, pale green fruits',
            'Alternaria spot: dark brown circular spots with concentric target rings',
            'Severe leaf curling, yellowing, defoliation, and stunted fruit production'
        ],
        'spread': [
            'Fungal spores dispersed by wind, rain splash, and crop residues',
            'Viral pathogens transmitted by insect vectors, primarily the silverleaf whitefly (Bemisia tabaci)',
            'Infected seed, contaminated tools, and nearby solanaceous/malvaceous weed hosts'
        ],
        'management': [
            'Confirm the exact disease before selecting a fungicide or insecticide: viral diseases require vector control, while fungal spots require fungicides',
            'For fungal leaf spots, apply registered fungicides (e.g., Mancozeb, Copper Oxychloride, or Wettable Sulphur) according to label recommendations and harvest intervals',
            'For yellow vein mosaic, spray approved insecticides (e.g., Acetamiprid, Thiamethoxam, or neem oil) to control whitefly vector populations',
            'Rogue out and destroy virus-infected plants immediately to protect nearby healthy okra stands'
        ],
        'prevention': [
            'Plant YVMV-resistant okra hybrids (e.g., Parbhani Kranti, Arka Anamika, or regional resistant hybrids)',
            'Install yellow sticky traps (15-20 traps/acre) to monitor and catch whitefly vectors',
            'Practice 2-year crop rotation with non-malvaceous crops (cereals, pulses)',
            'Keep field borders free of weeds such as wild mallow and Abutilon'
        ],
        'urgency': 'Confirm diagnosis'
    },
    'Turmeric|Leaf Anthracnose': {
        'description': 'A destructive fungal leaf disease of turmeric producing elliptical to oblong brown spots with grey centers and dark margins, leading to rapid leaf drying and reduced rhizome yield.',
        'cause': 'Colletotrichum curcumae (and Colletotrichum gloeosporioides, fungi); favored by warm, humid, rainy monsoon conditions (25-30°C) with persistent moisture on foliage.',
        'symptoms': [
            'Small, circular to oval, water-soaked spots on young leaves starting near leaf margins or tips',
            'Spots enlarge into elliptical brown lesions with light grey or ash-colored centers and dark brown borders',
            'Numerous tiny black dots (acervuli) appear in concentric rings within the grey center of lesions',
            'Lesions coalesce, causing extensive blighting, yellowing, and drying of leaf blades',
            'Severely affected plants lose active foliage, resulting in stunted, poorly developed rhizomes'
        ],
        'spread': [
            'Rain splash and wind-driven rain droplets dispersing conidia from leaf to leaf',
            'Infected seed rhizomes carrying dormant fungal mycelium',
            'Fungal survival on infected turmeric leaf trash and crop residues in the soil'
        ],
        'management': [
            'Cut and burn severely blighted leaves to reduce secondary spread of acervular conidia',
            'Apply registered fungicides (e.g., Mancozeb, Carbendazim, or Azoxystrobin) at 15-day intervals starting from early disease onset during the monsoon',
            'Ensure adequate field drainage; avoid stagnant waterlogging in turmeric beds',
            'Spray biological formulations of Pseudomonas fluorescens or Trichoderma viride'
        ],
        'prevention': [
            'Select certified disease-free, plump seed rhizomes from healthy parent crops',
            'Treat seed rhizomes with Carbendazim (0.1%) or Mancozeb (0.3%) for 30 minutes before planting',
            'Grow turmeric on raised broad beds with organic mulch to prevent rain splash of soil spores',
            'Practice 3-year crop rotation with non-host crops (maize, pulses, paddy)'
        ],
        'urgency': 'Medium'
    },
    'Turmeric|Leaf Blight': {
        'description': 'A major foliar disease of turmeric causing large water-soaked expanding lesions that turn brown, coalesce, and cause extensive leaf drying and premature defoliation.',
        'cause': 'Rhizoctonia solani and Alternaria species (fungal pathogens); favored by warm temperatures (26-32°C), heavy rainfall, high relative humidity, and dense shaded canopies.',
        'symptoms': [
            'Water-soaked, irregular or circular brown lesions appearing on the leaf blade and margins',
            'Lesions expand rapidly with concentric zoning and yellow chlorotic margins',
            'Adjacent lesions merge to cover the entire leaf surface, causing complete foliar drying and necrosis',
            'Leaf sheaths develop water-soaked rotting lesions leading to premature leaf detachment',
            'Significant reduction in photosynthetic leaf area, resulting in small, fibrous, poorly developed rhizomes'
        ],
        'spread': [
            'Rain splash, wind currents, and plant-to-plant contact through dense canopies',
            'Sclerotia and mycelia surviving in soil and crop debris',
            'Infected planting rhizomes and contaminated irrigation water'
        ],
        'management': [
            'Remove and safely dispose of blighted leaves at early symptom stages',
            'Apply registered fungicides (e.g., Mancozeb, Propiconazole, or Copper Oxychloride) ensuring thorough spray coverage on both leaf surfaces',
            'Improve field drainage and avoid overhead sprinkler irrigation',
            'Apply Trichoderma-enriched compost to the root zone'
        ],
        'prevention': [
            'Perform rhizome seed treatment with approved fungicide solutions prior to planting',
            'Adopt recommended row-to-row and plant-to-plant spacing to facilitate good canopy aeration',
            'Practice 2 to 3-year crop rotation with non-allied crops',
            'Maintain regular field scouting during the peak monsoon months'
        ],
        'urgency': 'High'
    },
    'Turmeric|Leaf Blotch': {
        'description': 'A very common foliar fungal disease of turmeric producing hundreds of small, rectangular, brownish-yellow blotches along leaf veins, making leaves look scorched and reducing rhizome tonnage.',
        'cause': 'Taphrina maculans (fungus); favored by warm, humid weather (24-30°C) with persistent fog, cloudiness, heavy dew, and monsoon rainfall.',
        'symptoms': [
            'Small, oval, rectangular, or irregular yellowish-brown spots appearing on both sides of the leaf',
            'Spots appear in large numbers, closely packed in rows along leaf veins',
            'Spots turn dirty yellow to dark brown, coalescing to give the leaf a scorched or burnt appearance',
            'Heavily infected leaves turn completely yellow, curl, dry up, and wither prematurely',
            'Rhizome yield is severely reduced due to the early loss of photosynthetic capacity'
        ],
        'spread': [
            'Airborne ascospores discharged from leaf asci and dispersed by wind currents',
            'Rain splash distributing spores from lower leaves to upper leaves',
            'Fungal survival on infected fallen turmeric leaves and plant debris in the field'
        ],
        'management': [
            'Collect and burn severely affected leaves to minimize ascospore discharge',
            'Apply registered fungicides (e.g., Mancozeb, Copper Oxychloride, or Carbendazim) at the first sighting of yellow blotches and repeat at 15-day intervals during wet weather',
            'Avoid excessive shade; thin overhead shade trees in intercropped turmeric plantations',
            'Provide balanced potash fertilization to increase leaf epidermal resistance'
        ],
        'prevention': [
            'Select healthy, sound seed rhizomes from disease-free seed production plots',
            'Dip seed rhizomes in Mancozeb (0.3%) or Carbendazim (0.1%) solution for 30 minutes before planting',
            'Plant on raised beds with proper spacing to facilitate rapid drying of foliage',
            'Destroy crop debris after harvest and rotate fields with non-host crops'
        ],
        'urgency': 'Medium'
    },
    'Turmeric|Leaf Spot': {
        'description': 'A foliar disease of turmeric causing distinct circular to irregular brown necrotic spots on leaves, which enlarge, merge, and cause premature leaf drying and reduced rhizome development.',
        'cause': 'Colletotrichum capsici and Phoma species (fungal leaf-spot pathogens); favored by warm temperatures (25-30°C), high humidity (>85%), and frequent monsoon rains.',
        'symptoms': [
            'Small, circular to irregular brown spots appearing on the upper surface of leaves',
            'Spots enlarge with light brown or greyish centers and dark reddish-brown margins',
            'A chlorotic yellow halo typically encircles individual lesions',
            'Spots coalesce, causing extensive foliar drying, edge scorching, and premature senescence',
            'Rhizome size and curcumin content are reduced due to impaired photosynthetic activity'
        ],
        'spread': [
            'Rain splash and wind-blown droplets carrying fungal conidia across the canopy',
            'Infected seed rhizomes harboring latent fungal mycelia',
            'Survival in infected crop residues and decaying mulch material'
        ],
        'management': [
            'Remove and safely dispose of severely spotted leaves to reduce spore pressure',
            'Spray registered fungicides (e.g., Mancozeb, Carbendazim, or Difenoconazole) at 14-day intervals upon noticing spots',
            'Maintain good field drainage and avoid water stagnation around beds',
            'Spray bio-agents like Pseudomonas fluorescens (0.5%) preventively'
        ],
        'prevention': [
            'Use certified disease-free seed rhizomes; treat rhizomes with fungicide solution before planting',
            'Maintain optimal spacing between plants (30x15 cm or 45x15 cm) on raised beds',
            'Apply organic mulch (paddy straw or green leaves) to prevent soil splash onto foliage',
            'Rotate crops with non-host species every 2-3 years'
        ],
        'urgency': 'Medium'
    },
    'Turmeric|Rhizoctonia Leaf Blight': {
        'description': 'A severe fungal blight of turmeric causing large water-soaked lesions that start near the leaf base and collar region, rapidly spreading upward and causing rotting and lodging of the pseudostem.',
        'cause': 'Rhizoctonia solani (fungus); soil-borne pathogen; favored by high temperatures (28-32°C), waterlogged soils, high relative humidity (90-100%), and dense, poorly drained plantings.',
        'symptoms': [
            'Water-soaked, greenish-brown elliptical lesions appearing near the base of leaves and pseudostems',
            'Lesions expand rapidly upward onto the leaf lamina, turning into large, irregular, bleached blighted patches with dark margins',
            'Basal leaf sheaths rot and soften, causing affected leaves to collapse and detach from the pseudostem',
            'Brown irregular fungal sclerotia form on rotting leaf sheaths and collar tissues',
            'Severe blight causes complete foliage death and predisposing rhizomes to secondary soft rot'
        ],
        'spread': [
            'Soil-borne sclerotia and mycelia surviving in the soil and floating in irrigation water',
            'Plant-to-plant contact through dense, overcrowded, humid foliage',
            'Infected seed rhizomes and contaminated crop residues'
        ],
        'management': [
            'Improve field drainage immediately; ensure no standing water accumulates between turmeric beds',
            'Remove and burn severely infected leaves and rotting pseudostems',
            'Drench the collar region and spray foliage with registered fungicides (e.g., Validamycin, Carbendazim, or Hexaconazole)',
            'Apply Trichoderma harzianum enriched neem cake/manure to the base of plants'
        ],
        'prevention': [
            'Treat seed rhizomes with Trichoderma viride (10 g/kg) or Carbendazim (1 g/L) before planting',
            'Plant on well-drained raised beds (15-20 cm high) with deep inter-bed furrows',
            'Maintain optimum plant density to prevent excessive microclimate humidity',
            'Practice 3-year crop rotation avoiding other Rhizoctonia-susceptible host crops'
        ],
        'urgency': 'High'
    }
}

# Duplicate dataset aliases from the model training dataset to ensure 100% resolution
DISEASE_KNOWLEDGE.update({
    'Bajra (Pearl Millet)|Anthracnose - Copy': DISEASE_KNOWLEDGE['Bajra (Pearl Millet)|Anthracnose'],
    'Bajra (Pearl Millet)|Anthracnose - Copy (2)': DISEASE_KNOWLEDGE['Bajra (Pearl Millet)|Anthracnose'],
    'Bajra (Pearl Millet)|Anthracnose - Copy - Copy': DISEASE_KNOWLEDGE['Bajra (Pearl Millet)|Anthracnose'],
    'Jowar (Sorghum)|Anthracnose - Copy': DISEASE_KNOWLEDGE['Jowar (Sorghum)|Anthracnose'],
})

# Complete alias dictionary mapping raw class labels to canonical knowledge keys
RAW_CLASS_TO_KEY = {
    'Brinjal_Bacterial_wilt': 'Brinjal|Bacterial Wilt',
    'Brinjal_Cercospora_leaf_spot': 'Brinjal|Cercospora Leaf Spot',
    'Brinjal_little leaf_disease': 'Brinjal|Little Leaf Disease',
    'Brinjal_phomopsis_Blight': 'Brinjal|Phomopsis Blight',
    'CabbageBlack_root': 'Cabbage|Black Root',
    'Cabbage_Alternaria_Leaf_Spot': 'Cabbage|Alternaria Leaf Spot',
    'Cabbage_Downy_mildew': 'Cabbage|Downy Mildew',
    'Cabbage_Fusarium_Yellows': 'Cabbage|Fusarium Yellows',
    'Cabbage_club_root': 'Cabbage|Clubroot',
    'Cherry_Bacterial_Canker': 'Cherry|Bacterial Canker',
    'Cherry_brown_rot': 'Cherry|Brown Rot',
    'Cotton_Alternaria_Leaf_Spot': 'Cotton|Alternaria Leaf Spot',
    'Cotton_Bacterial_Blight': 'Cotton|Bacterial Blight',
    'Cotton_Fusarium_Wilt': 'Cotton|Fusarium Wilt',
    'Cotton_Grey_Mildew_(Areolate Mildew)': 'Cotton|Grey Mildew (Areolate Mildew)',
    'Cotton_Verticillium_Wilt': 'Cotton|Verticillium Wilt',
    'Grapes_Anthracnose': 'Grapes|Anthracnose',
    'Grapes_Bacterial_leaf_spot': 'Grapes|Bacterial Leaf Spot',
    'Grapes_Downy_Mildew': 'Grapes|Downy Mildew',
    'Grapes_Grey_Mold_(Botrytis)': 'Grapes|Grey Mold (Botrytis)',
    'Grapes_Powdery_mildew': 'Grapes|Powdery Mildew',
    'Maize(Corn)_common_rust_in_maize': 'Maize (Corn)|Common Rust',
    'maize_commonrust': 'Maize (Corn)|Common Rust',
    'Onion_Downy_Mildew — Peronospora destructor': 'Onion|Downy Mildew',
    'Onion_Downy_Mildew - Peronospora destructor': 'Onion|Downy Mildew',
    'Onion_Fusarium_Basal_Plate_Rot': 'Onion|Fusarium Basal Plate Rot',
    'Onion_Purple_Blotch': 'Onion|Purple Blotch',
    'Onion_Stemphylium_Leaf_Blight — Stemphylium vesicarium': 'Onion|Stemphylium Leaf Blight',
    'Onion_Stemphylium_Leaf_Blight - Stemphylium vesicarium': 'Onion|Stemphylium Leaf Blight',
    'Onion_White_Rot — Sclerotium cepivorum': 'Onion|White Rot',
    'Onion_White_Rot - Sclerotium cepivorum': 'Onion|White Rot',
    'Rice_Bacterial_leaf_Blight': 'Rice|Bacterial Leaf Blight',
    'Rice_Blast': 'Rice|Blast',
    'Rice_Brown_spots': 'Rice|Brown Spot',
    'Rice_Sheath_Blight': 'Rice|Sheath Blight',
    'Rice_tungro_disease': 'Rice|Tungro Disease',
    'Sugarcane_Grassy_Shoot_Disease': 'Sugarcane|Grassy Shoot Disease',
    'Sugarcane_Pokkah_Boeng_(Top Rot)': 'Sugarcane|Pokkah Boeng (Top Rot)',
    'Sugarcane_Red_root': 'Sugarcane|Red Rot',
    'Sugarcane_Smut': 'Sugarcane|Smut',
    'Sugarcane_Wilt': 'Sugarcane|Wilt',
    'Sugarcane_stalk_rot': 'Sugarcane|Stalk Rot',
    'Tomato_Bacterial_Spot': 'Tomato|Bacterial Spot',
    'Tomato_Late_blight': 'Tomato|Late Blight',
    'Tomato_Leaf_Early_Blight': 'Tomato|Early Blight',
    'Tomato_Leaf_Mold': 'Tomato|Leaf Mold',
    'Tomato_Spectoria_Leaf_Spot': 'Tomato|Septoria Leaf Spot',
    'Tur_Phytophthora Bligh': 'Tur (Pigeon Pea)|Phytophthora Blight',
    'Tur__Fusarium Wilt': 'Tur (Pigeon Pea)|Fusarium Wilt',
    'Wheat _Leaf_rust': 'Wheat|Leaf Rust',
    'Wheat_Fusarium_Head_Blight': 'Wheat|Fusarium Head Blight',
    'Wheat_Powdery_Mildew_disease': 'Wheat|Powdery Mildew',
    'Wheat_Septoria_Leaf_Blotch': 'Wheat|Septoria Leaf Blotch',
    'Wheat_stripe_rust': 'Wheat|Stripe Rust',
    'bajra_anthracnose_disease': 'Bajra (Pearl Millet)|Anthracnose',
    'bajra_anthracnose_disease - Copy': 'Bajra (Pearl Millet)|Anthracnose',
    'bajra_anthracnose_disease - Copy (2)': 'Bajra (Pearl Millet)|Anthracnose',
    'bajra_anthracnose_disease - Copy - Copy': 'Bajra (Pearl Millet)|Anthracnose',
    'bajra_downy_lmildew_eaf_disease': 'Bajra (Pearl Millet)|Downy Mildew',
    'bajra_leaf_rust_disease': 'Bajra (Pearl Millet)|Leaf Rust',
    'bajra_leaf_spot_disease': 'Bajra (Pearl Millet)|Leaf Spot',
    'groundnut_diseases': 'Groundnut|Leaf Disease',
    'jowar__leaf_spot_disease': 'Jowar (Sorghum)|Leaf Spot',
    'jowar_antharcnose_disease': 'Jowar (Sorghum)|Anthracnose',
    'jowar_antharcnose_disease - Copy': 'Jowar (Sorghum)|Anthracnose',
    'jowar_leaf_rust_disease': 'Jowar (Sorghum)|Leaf Rust',
    'jowar_mydis_leaf_spot': 'Jowar (Sorghum)|Leaf Spot',
    'ladyfinger_diseases': 'Ladyfinger (Okra)|Leaf Disease',
    'turmeric_leaf_anthracnose_diseas': 'Turmeric|Leaf Anthracnose',
    'turmeric_leaf_blight': 'Turmeric|Leaf Blight',
    'turmeric_leaf_blotch_diseas': 'Turmeric|Leaf Blotch',
    'turmeric_leaf_spot_diseas': 'Turmeric|Leaf Spot',
    'turmeric_rhizoctonia_leaf_blight_disease': 'Turmeric|Rhizoctonia Leaf Blight'
}


def get_disease_info(crop, disease):
    """Return detailed information using case-insensitive exact crop+disease matching."""
    if not crop or not disease:
        return None
    key = f"{str(crop).strip()}|{str(disease).strip()}".lower()
    for stored_key, info in DISEASE_KNOWLEDGE.items():
        if stored_key.lower() == key:
            return info

    # Check without extra parentheses/brackets
    clean_crop = str(crop).split('(')[0].strip().lower()
    clean_disease = str(disease).split('(')[0].strip().lower()
    for stored_key, info in DISEASE_KNOWLEDGE.items():
        sk_lower = stored_key.lower()
        if clean_crop in sk_lower and clean_disease in sk_lower:
            return info

    return None


def get_disease_info_by_key(key):
    """Return detailed information for a canonical 'Crop|Disease' key or raw class name."""
    if not key:
        return None

    str_key = str(key).strip()

    # Direct match
    for stored_key, info in DISEASE_KNOWLEDGE.items():
        if stored_key.lower() == str_key.lower():
            return info

    # Raw model label mapping
    if str_key in RAW_CLASS_TO_KEY:
        canonical = RAW_CLASS_TO_KEY[str_key]
        return DISEASE_KNOWLEDGE.get(canonical)

    for raw, canonical in RAW_CLASS_TO_KEY.items():
        if raw.lower() == str_key.lower():
            return DISEASE_KNOWLEDGE.get(canonical)

    # If "Crop|Disease" format
    if '|' in str_key:
        crop_part, disease_part = str_key.split('|', 1)
        return get_disease_info(crop_part, disease_part)

    return None
