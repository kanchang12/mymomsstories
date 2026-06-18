"""
services/content.py — the five "stops" (alphabet, words, lines, customs,
stories) for each of the thirteen launch languages.

IMPORTANT — this is STARTER content, not a finished curriculum:
  * Alphabet sets are a representative first 5-6 letters, not the full
    script. Expand LANGUAGES[code]["alphabet"] as more letters are taught.
  * Words/lines/customs are simple, common, and (to the best of this
    pass's knowledge) correct — but none of this has been reviewed by a
    native speaker per language. Before this goes in front of real
    families, have someone fluent in each language check it — especially
    Tamil, Telugu, Kannada, Malayalam, and Ukrainian, where this pass's
    confidence is lowest.
  * The two stories per language are titles + a one-line, original,
    simplified synopsis — not transcriptions of any existing book or
    translation. They're meant as a placeholder hook; swap in a properly
    written/reviewed short retelling per language before launch.

Each item carries: the script text, a Latin transliteration (for the
parent, who may not read the script either), and an English gloss.
"""

LANGUAGES = {
    "bn": {
        "name": "Bengali",
        "alphabet": [
            {"char": "অ", "translit": "o",  "hint": "as in 'pot'"},
            {"char": "আ", "translit": "aa", "hint": "as in 'father'"},
            {"char": "ই", "translit": "i",  "hint": "as in 'sit'"},
            {"char": "ক", "translit": "ka", "hint": ""},
            {"char": "খ", "translit": "kha","hint": ""},
            {"char": "গ", "translit": "ga", "hint": ""},
        ],
        "words": [
            {"text": "মা",    "translit": "maa",     "gloss": "mother"},
            {"text": "বাবা",  "translit": "baba",    "gloss": "father"},
            {"text": "জল",    "translit": "jol",     "gloss": "water"},
            {"text": "ভাত",   "translit": "bhat",    "gloss": "rice"},
            {"text": "আকাশ",  "translit": "akash",   "gloss": "sky"},
        ],
        "lines": [
            {"text": "আমার নাম রিয়া।",        "translit": "amar naam Riya.",          "gloss": "My name is Riya."},
            {"text": "মা ভালোবাসেন।",          "translit": "maa bhalobashen.",          "gloss": "Mother loves [us]."},
            {"text": "আকাশ নীল।",              "translit": "akash neel.",               "gloss": "The sky is blue."},
        ],
        "customs": [
            {"key": "poila_boishakh", "title": "Poila Boishakh",
             "text": "The Bengali new year, celebrated in mid-April with new clothes, sweets, and visits to family."},
        ],
        "stories": [
            {"key": "thakurmar_jhuli", "title": "ঠাকুরমার ঝুলি", "translit": "Thakurmar Jhuli",
             "gloss": "Grandmother's Bag of Tales",
             "synopsis": "একদিন এক রাজার মেয়ে জঙ্গলে একটি কথা বলা পাখির সাথে দেখা করল।  পাখিটি তাকে একটি গোপন কথা বলল।"},
            {"key": "kak_o_shial", "title": "কাক ও শিয়াল", "translit": "Kak o Shial",
             "gloss": "The Crow and the Fox",
             "synopsis": "একটি কাক মুখে রুটি নিয়ে গাছে বসেছিল। একটি শিয়াল তাকে গান গাইতে বলে রুটিটা কেড়ে নিল।"},
        ],
    },
    "hi": {
        "name": "Hindi",
        "alphabet": [
            {"char": "अ", "translit": "a",  "hint": "as in 'about'"},
            {"char": "आ", "translit": "aa", "hint": "as in 'father'"},
            {"char": "इ", "translit": "i",  "hint": "as in 'sit'"},
            {"char": "क", "translit": "ka", "hint": ""},
            {"char": "ख", "translit": "kha","hint": ""},
            {"char": "ग", "translit": "ga", "hint": ""},
        ],
        "words": [
            {"text": "माँ",     "translit": "maa",     "gloss": "mother"},
            {"text": "पानी",   "translit": "paani",   "gloss": "water"},
            {"text": "घर",     "translit": "ghar",    "gloss": "house"},
            {"text": "सूरज",   "translit": "sooraj",  "gloss": "sun"},
            {"text": "किताब",  "translit": "kitaab",  "gloss": "book"},
        ],
        "lines": [
            {"text": "मेरा नाम आर्या है।",        "translit": "mera naam Aarya hai.",      "gloss": "My name is Aarya."},
            {"text": "सूरज पूर्व से उगता है।",     "translit": "sooraj poorv se ugta hai.", "gloss": "The sun rises from the east."},
            {"text": "माँ मुझे कहानी सुनाती है।",  "translit": "maa mujhe kahaani sunaati hai.", "gloss": "Mother tells me a story."},
        ],
        "customs": [
            {"key": "diwali", "title": "Diwali",
             "text": "The festival of lights — homes are lit with small oil lamps, and families share sweets over several days."},
        ],
        "stories": [
            {"key": "panchatantra", "title": "पंचतंत्र", "translit": "Panchatantra",
             "gloss": "The Panchatantra fables",
             "synopsis": "एक बंदर और एक मगरमच्छ अच्छे दोस्त थे। एक दिन मगरमच्छ ने बंदर को धोखा देने की कोशिश की, लेकिन बंदर बहुत चालाक था।"},
            {"key": "akbar_birbal", "title": "अकबर और बीरबल", "translit": "Akbar aur Birbal",
             "gloss": "Akbar and Birbal",
             "synopsis": "राजा अकबर ने एक कठिन सवाल पूछा। उनके चतुर मंत्री बीरबल ने एक बहुत आसान और चतुर जवाब दिया।"},
        ],
    },
    "mr": {
        "name": "Marathi",
        "alphabet": [
            {"char": "अ", "translit": "a",  "hint": "as in 'about'"},
            {"char": "आ", "translit": "aa", "hint": "as in 'father'"},
            {"char": "इ", "translit": "i",  "hint": "as in 'sit'"},
            {"char": "क", "translit": "ka", "hint": ""},
            {"char": "ख", "translit": "kha","hint": ""},
            {"char": "ग", "translit": "ga", "hint": ""},
        ],
        "words": [
            {"text": "आई",     "translit": "aai",    "gloss": "mother"},
            {"text": "पाणी",   "translit": "paani",  "gloss": "water"},
            {"text": "घर",     "translit": "ghar",   "gloss": "house"},
            {"text": "सूर्य",  "translit": "surya",  "gloss": "sun"},
            {"text": "पुस्तक", "translit": "pustak", "gloss": "book"},
        ],
        "lines": [
            {"text": "माझे नाव साई आहे।",       "translit": "maze naav Sai aahe.",        "gloss": "My name is Sai."},
            {"text": "आई मला गोष्ट सांगते।",    "translit": "aai mala gosht saangte.",    "gloss": "Mother tells me a story."},
            {"text": "सूर्य पूर्वेला उगवतो।",   "translit": "surya poorvela ugavto.",     "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "gudi_padwa", "title": "Gudi Padwa",
             "text": "The Marathi new year — families raise a decorated gudi flag outside the home for good luck."},
        ],
        "stories": [
            {"key": "isapniti", "title": "इसापनीती", "translit": "Isapniti",
             "gloss": "Aesop's fables, the Marathi way",
             "synopsis": "एका कावळ्याला खूप तहान लागली होती. त्याने एका भांड्यात थोडे पाणी पाहिले आणि एक हुशार उपाय शोधला."},
            {"key": "sasa_ani_kasav", "title": "ससा आणि कासव", "translit": "Sasa Ani Kasav",
             "gloss": "The Hare and the Tortoise",
             "synopsis": "ससा कासवाची शर्यतीत चेष्टा करतो आणि वेगात पुढे जातो, पण थोडी झोप घेण्याची चूक करतो."},
        ],
    },
    "ta": {
        "name": "Tamil",
        "alphabet": [
            {"char": "அ", "translit": "a",   "hint": "as in 'about'"},
            {"char": "ஆ", "translit": "aa",  "hint": "as in 'father'"},
            {"char": "இ", "translit": "i",   "hint": "as in 'sit'"},
            {"char": "க", "translit": "ka",  "hint": ""},
            {"char": "ங", "translit": "nga", "hint": ""},
            {"char": "ச", "translit": "cha", "hint": ""},
        ],
        "words": [
            {"text": "அம்மா",    "translit": "amma",      "gloss": "mother"},
            {"text": "தண்ணீர்",  "translit": "thanneer",  "gloss": "water"},
            {"text": "வீடு",     "translit": "veedu",     "gloss": "house"},
            {"text": "சூரியன்",  "translit": "sooriyan",  "gloss": "sun"},
            {"text": "புத்தகம்", "translit": "puthagam",  "gloss": "book"},
        ],
        "lines": [
            {"text": "என் பெயர் மீரா.",          "translit": "en peyar Meera.",            "gloss": "My name is Meera."},
            {"text": "அம்மா எனக்கு கதை சொல்வாள்.", "translit": "amma enakku kathai solvaal.", "gloss": "Mother tells me a story."},
            {"text": "சூரியன் கிழக்கில் உதிக்கும்.", "translit": "sooriyan kizhakkil udhikkum.", "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "pongal", "title": "Pongal",
             "text": "A harvest festival — a sweet rice dish is cooked outdoors and shared with family and cattle are honoured."},
        ],
        "stories": [
            {"key": "silappathikaram", "title": "சிலப்பதிகாரம்", "translit": "Silappathikaram",
             "gloss": "The great Tamil epic of the anklet",
             "synopsis": "கண்ணகி என்ற பெண் தனது கணவனுக்கு நேர்ந்த அநீதிக்கு எதிராக துணிவுடன் நின்றாள்."},
            {"key": "aamaiyum_muyalum", "title": "ஆமையும் முயலும்", "translit": "Aamaiyum Muyalum",
             "gloss": "The Tortoise and the Hare",
             "synopsis": "முயல் ஆமையை பந்தயத்தில் கேலி செய்தது, ஆனால் தூங்கிவிட்டதால் தோற்றுப்போனது."},
        ],
    },
    "te": {
        "name": "Telugu",
        "alphabet": [
            {"char": "అ", "translit": "a",   "hint": "as in 'about'"},
            {"char": "ఆ", "translit": "aa",  "hint": "as in 'father'"},
            {"char": "ఇ", "translit": "i",   "hint": "as in 'sit'"},
            {"char": "క", "translit": "ka",  "hint": ""},
            {"char": "ఖ", "translit": "kha", "hint": ""},
            {"char": "గ", "translit": "ga",  "hint": ""},
        ],
        "words": [
            {"text": "అమ్మ",    "translit": "amma",     "gloss": "mother"},
            {"text": "నీరు",    "translit": "neeru",    "gloss": "water"},
            {"text": "ఇల్లు",   "translit": "illu",     "gloss": "house"},
            {"text": "సూర్యుడు","translit": "suryudu",  "gloss": "sun"},
            {"text": "పుస్తకం", "translit": "pustakam", "gloss": "book"},
        ],
        "lines": [
            {"text": "నా పేరు అనిత.",            "translit": "naa peru Anitha.",            "gloss": "My name is Anitha."},
            {"text": "అమ్మ నాకు కథ చెబుతుంది.",  "translit": "amma naaku katha chebutundi.", "gloss": "Mother tells me a story."},
            {"text": "సూర్యుడు తూర్పున ఉదయిస్తాడు.", "translit": "suryudu thoorpuna udayistaadu.", "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "ugadi", "title": "Ugadi",
             "text": "The Telugu new year — families eat ugadi pachadi, a dish mixing six tastes to represent a balanced year ahead."},
        ],
        "stories": [
            {"key": "tenali_ramakrishna", "title": "తెనాలి రామకృష్ణ కథలు", "translit": "Tenali Ramakrishna Kathalu",
             "gloss": "The wit of Tenali Ramakrishna",
             "synopsis": "రాజు ఒక గమ్మత్తైన పరీక్ష పెట్టాడు. తెనాలి రామకృష్ణ తన తెలివితో అందరినీ ఆశ్చర్యపరిచాడు."},
            {"key": "kundelu_tabelu", "title": "కుందేలు మరియు తాబేలు", "translit": "Kundelu Mariyu Tabelu",
             "gloss": "The Hare and the Tortoise",
             "synopsis": "కుందేలు తాబేలును వేగంలో ఎగతాళి చేసింది, కానీ మధ్యలో నిద్రపోయి పందెం ఓడిపోయింది."},
        ],
    },
    "kn": {
        "name": "Kannada",
        "alphabet": [
            {"char": "ಅ", "translit": "a",   "hint": "as in 'about'"},
            {"char": "ಆ", "translit": "aa",  "hint": "as in 'father'"},
            {"char": "ಇ", "translit": "i",   "hint": "as in 'sit'"},
            {"char": "ಕ", "translit": "ka",  "hint": ""},
            {"char": "ಖ", "translit": "kha", "hint": ""},
            {"char": "ಗ", "translit": "ga",  "hint": ""},
        ],
        "words": [
            {"text": "ಅಮ್ಮ",    "translit": "amma",    "gloss": "mother"},
            {"text": "ನೀರು",    "translit": "neeru",   "gloss": "water"},
            {"text": "ಮನೆ",     "translit": "mane",    "gloss": "house"},
            {"text": "ಸೂರ್ಯ",   "translit": "surya",   "gloss": "sun"},
            {"text": "ಪುಸ್ತಕ",  "translit": "pustaka", "gloss": "book"},
        ],
        "lines": [
            {"text": "ನನ್ನ ಹೆಸರು ಅಮೃತ.",          "translit": "nanna hesaru Amrutha.",         "gloss": "My name is Amrutha."},
            {"text": "ಅಮ್ಮ ನನಗೆ ಕಥೆ ಹೇಳುತ್ತಾಳೆ.", "translit": "amma nanage kathe heLuttaaLe.", "gloss": "Mother tells me a story."},
            {"text": "ಸೂರ್ಯ ಪೂರ್ವದಲ್ಲಿ ಉದಯಿಸುತ್ತಾನೆ.", "translit": "surya poorvadalli udayisuttaane.", "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "ugadi_kn", "title": "Ugadi",
             "text": "The Kannada new year — homes are decorated with mango-leaf garlands, and a mixed-taste dish marks the day."},
        ],
        "stories": [
            {"key": "punyakoti", "title": "ಪುಣ್ಯಕೋಟಿ", "translit": "Punyakoti",
             "gloss": "Punyakoti, the cow who kept her word",
             "synopsis": "ಒಂದು ಹಸು ಹುಲಿಗೆ ಮಾತು ಕೊಟ್ಟಿತು — ತನ್ನ ಕರುವನ್ನು ನೋಡಿ ಮರಳಿ ಬರುವುದಾಗಿ. ಅದು ತನ್ನ ಮಾತನ್ನು ಉಳಿಸಿಕೊಂಡಿತು."},
            {"key": "aame_mola", "title": "ಆಮೆ ಮತ್ತು ಮೊಲ", "translit": "Aame Mattu Mola",
             "gloss": "The Tortoise and the Hare",
             "synopsis": "ಮೊಲ ಆಮೆಯನ್ನು ಓಟದಲ್ಲಿ ಗೇಲಿ ಮಾಡಿತು, ಆದರೆ ನಿದ್ದೆ ಮಾಡಿ ಪಂದ್ಯ ಸೋತಿತು."},
        ],
    },
    "ml": {
        "name": "Malayalam",
        "alphabet": [
            {"char": "അ", "translit": "a",   "hint": "as in 'about'"},
            {"char": "ആ", "translit": "aa",  "hint": "as in 'father'"},
            {"char": "ഇ", "translit": "i",   "hint": "as in 'sit'"},
            {"char": "ക", "translit": "ka",  "hint": ""},
            {"char": "ഖ", "translit": "kha", "hint": ""},
            {"char": "ഗ", "translit": "ga",  "hint": ""},
        ],
        "words": [
            {"text": "അമ്മ",     "translit": "amma",      "gloss": "mother"},
            {"text": "വെള്ളം",   "translit": "vellam",    "gloss": "water"},
            {"text": "വീട്",     "translit": "veedu",     "gloss": "house"},
            {"text": "സൂര്യൻ",   "translit": "sooryan",   "gloss": "sun"},
            {"text": "പുസ്തകം",  "translit": "pusthakam", "gloss": "book"},
        ],
        "lines": [
            {"text": "എന്റെ പേര് മായ.",           "translit": "ente per Maya.",              "gloss": "My name is Maya."},
            {"text": "അമ്മ എനിക്ക് കഥ പറയും.",     "translit": "amma enikku katha parayum.",  "gloss": "Mother tells me a story."},
            {"text": "സൂര്യൻ കിഴക്ക് ഉദിക്കുന്നു.", "translit": "sooryan kizhakku udikkunnu.", "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "onam", "title": "Onam",
             "text": "A harvest festival — homes lay flower carpets (pookalam) on the floor and families share a big feast."},
        ],
        "stories": [
            {"key": "aithihyamala", "title": "ഐതിഹ്യമാല", "translit": "Aithihyamala",
             "gloss": "Garland of Legends",
             "synopsis": "ഒരു ബുദ്ധിമാനായ മനുഷ്യൻ തന്റെ സമയോചിത ബുദ്ധി ഉപയോഗിച്ച് ഒരു വലിയ പ്രശ്നം പരിഹരിച്ച കഥയാണിത്."},
            {"key": "muyalum_aamayum", "title": "മുയലും ആമയും", "translit": "Muyalum Aamayum",
             "gloss": "The Hare and the Tortoise",
             "synopsis": "മുയൽ ആമയെ ഓട്ടത്തിൽ കളിയാക്കി, പക്ഷേ ഉറങ്ങിപ്പോയതിനാൽ മത്സരത്തിൽ തോറ്റു."},
        ],
    },
    "ar": {
        "name": "Arabic",
        "alphabet": [
            {"char": "ا", "translit": "alif", "hint": ""},
            {"char": "ب", "translit": "ba",   "hint": ""},
            {"char": "ت", "translit": "ta",   "hint": ""},
            {"char": "ث", "translit": "tha",  "hint": ""},
            {"char": "ج", "translit": "jim",  "hint": ""},
            {"char": "ح", "translit": "ha",   "hint": ""},
        ],
        "words": [
            {"text": "أمي",   "translit": "ummi",  "gloss": "my mother"},
            {"text": "بيت",   "translit": "bayt",  "gloss": "house"},
            {"text": "ماء",   "translit": "maa'",  "gloss": "water"},
            {"text": "شمس",   "translit": "shams", "gloss": "sun"},
            {"text": "كتاب",  "translit": "kitab", "gloss": "book"},
        ],
        "lines": [
            {"text": "اسمي ليلى.",              "translit": "ismi Layla.",                  "gloss": "My name is Layla."},
            {"text": "أمي تحكي لي قصة.",        "translit": "ummi tahki li qissa.",         "gloss": "My mother tells me a story."},
            {"text": "الشمس تشرق من الشرق.",    "translit": "ash-shams tashruq min ash-sharq.", "gloss": "The sun rises from the east."},
        ],
        "customs": [
            {"key": "eid", "title": "Eid",
             "text": "A festival marked with new clothes, sweets, and visits to family — children often receive small gifts of money."},
        ],
        "stories": [
            {"key": "alf_layla", "title": "ألف ليلة وليلة", "translit": "Alf Layla wa Layla",
             "gloss": "One Thousand and One Nights",
             "synopsis": "كانت شهرزاد تحكي قصة جديدة كل ليلة، قصة مليئة بالمغامرات والحكمة."},
            {"key": "asad_faar", "title": "الأسد والفأر", "translit": "Al-Asad wal-Fa'r",
             "gloss": "The Lion and the Mouse",
             "synopsis": "فأر صغير ساعد أسدًا كبيرًا ذات يوم، وعندما احتاج الأسد للمساعدة، تذكّر معروف الفأر."},
        ],
    },
    "es": {
        "name": "Spanish",
        "alphabet": [
            {"char": "a", "translit": "a", "hint": "as in 'father'"},
            {"char": "e", "translit": "e", "hint": "as in 'bed'"},
            {"char": "i", "translit": "i", "hint": "as in 'machine'"},
            {"char": "o", "translit": "o", "hint": "as in 'note'"},
            {"char": "u", "translit": "u", "hint": "as in 'rule'"},
            {"char": "ñ", "translit": "ny","hint": "as in 'canyon'"},
        ],
        "words": [
            {"text": "mamá",  "translit": "mamá",  "gloss": "mother"},
            {"text": "agua",  "translit": "agua",  "gloss": "water"},
            {"text": "casa",  "translit": "casa",  "gloss": "house"},
            {"text": "sol",   "translit": "sol",   "gloss": "sun"},
            {"text": "libro", "translit": "libro", "gloss": "book"},
        ],
        "lines": [
            {"text": "Me llamo Sofía.",                 "translit": "Me llamo Sofía.",                 "gloss": "My name is Sofía."},
            {"text": "Mi mamá me cuenta un cuento.",     "translit": "Mi mamá me cuenta un cuento.",     "gloss": "My mother tells me a story."},
            {"text": "El sol sale por el este.",         "translit": "El sol sale por el este.",         "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "dia_de_reyes", "title": "Día de Reyes",
             "text": "Three Kings' Day, January 6th — children leave shoes out and receive small gifts, celebrated across much of the Spanish-speaking world."},
        ],
        "stories": [
            {"key": "cucarachita_martina", "title": "La Cucarachita Martina", "translit": "La Cucarachita Martina",
             "gloss": "The little cockroach who chose wisely",
             "synopsis": "Martina encontró una moneda y tuvo que elegir con quién casarse entre varios animales que la visitaron."},
            {"key": "liebre_tortuga", "title": "La Liebre y la Tortuga", "translit": "La Liebre y la Tortuga",
             "gloss": "The Hare and the Tortoise",
             "synopsis": "La liebre se burló de la tortuga por ser lenta, pero se durmió a mitad de la carrera y la tortuga ganó."},
        ],
    },
    "ja": {
        "name": "Japanese",
        "alphabet": [
            {"char": "あ", "translit": "a", "hint": ""},
            {"char": "い", "translit": "i", "hint": ""},
            {"char": "う", "translit": "u", "hint": ""},
            {"char": "え", "translit": "e", "hint": ""},
            {"char": "お", "translit": "o", "hint": ""},
            {"char": "か", "translit": "ka","hint": ""},
        ],
        "words": [
            {"text": "お母さん", "translit": "okaasan", "gloss": "mother"},
            {"text": "水",      "translit": "mizu",    "gloss": "water"},
            {"text": "家",      "translit": "ie",      "gloss": "house"},
            {"text": "本",      "translit": "hon",     "gloss": "book"},
            {"text": "太陽",    "translit": "taiyou",  "gloss": "sun"},
        ],
        "lines": [
            {"text": "わたしの名前はゆきです。",        "translit": "watashi no namae wa Yuki desu.",  "gloss": "My name is Yuki."},
            {"text": "お母さんがお話をしてくれる。",     "translit": "okaasan ga ohanashi o shitekureru.", "gloss": "Mother tells me a story."},
            {"text": "太陽は東から昇る。",              "translit": "taiyou wa higashi kara noboru.",   "gloss": "The sun rises from the east."},
        ],
        "customs": [
            {"key": "kodomo_no_hi", "title": "こどもの日 (Children's Day)",
             "text": "Celebrated May 5th — families fly carp-shaped koinobori streamers to wish children strength and health."},
        ],
        "stories": [
            {"key": "momotaro", "title": "桃太郎", "translit": "Momotaro",
             "gloss": "Momotaro, the Peach Boy",
             "synopsis": "ある日、おばあさんが川で大きな桃を見つけました。その桃から元気な男の子が生まれました。"},
            {"key": "urashima_taro", "title": "うらしまたろう", "translit": "Urashima Tarou",
             "gloss": "Urashima Tarō",
             "synopsis": "漁師の浦島太郎は、助けた亀に連れられて、海の底にある美しい竜宮城を訪れました。"},
        ],
    },
    "ru": {
        "name": "Russian",
        "alphabet": [
            {"char": "А", "translit": "a",  "hint": "as in 'father'"},
            {"char": "Б", "translit": "b",  "hint": ""},
            {"char": "В", "translit": "v",  "hint": ""},
            {"char": "Г", "translit": "g",  "hint": ""},
            {"char": "Д", "translit": "d",  "hint": ""},
            {"char": "Е", "translit": "ye", "hint": ""},
        ],
        "words": [
            {"text": "мама",   "translit": "mama",    "gloss": "mother"},
            {"text": "вода",   "translit": "voda",    "gloss": "water"},
            {"text": "дом",    "translit": "dom",     "gloss": "house"},
            {"text": "солнце", "translit": "solntse", "gloss": "sun"},
            {"text": "книга",  "translit": "kniga",   "gloss": "book"},
        ],
        "lines": [
            {"text": "Меня зовут Соня.",              "translit": "Menya zovut Sonya.",              "gloss": "My name is Sonya."},
            {"text": "Мама рассказывает мне сказку.", "translit": "Mama rasskazyvaet mne skazku.",   "gloss": "Mother tells me a story."},
            {"text": "Солнце встаёт на востоке.",     "translit": "Solntse vstayot na vostoke.",     "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "maslenitsa", "title": "Maslenitsa",
             "text": "A week-long pre-spring festival — families cook and share bliny (thin pancakes) and say goodbye to winter with bonfires."},
        ],
        "stories": [
            {"key": "repka", "title": "Репка", "translit": "Repka",
             "gloss": "The Turnip",
             "synopsis": "Дед посадил репку, и она выросла огромной. Вся семья — один за другим — тянула репку, пока не вытянула её вместе."},
            {"key": "masha_medved", "title": "Маша и Медведь", "translit": "Masha i Medved",
             "gloss": "Masha and the Bear",
             "synopsis": "Маша заблудилась в лесу и попала в дом медведя. Своей хитростью она нашла способ вернуться домой к дедушке и бабушке."},
        ],
    },
    "uk": {
        "name": "Ukrainian",
        "alphabet": [
            {"char": "А", "translit": "a",  "hint": "as in 'father'"},
            {"char": "Б", "translit": "b",  "hint": ""},
            {"char": "В", "translit": "v",  "hint": ""},
            {"char": "Г", "translit": "h",  "hint": "softer than Russian Г"},
            {"char": "Д", "translit": "d",  "hint": ""},
            {"char": "Е", "translit": "e",  "hint": ""},
        ],
        "words": [
            {"text": "мама",   "translit": "mama",   "gloss": "mother"},
            {"text": "вода",   "translit": "voda",   "gloss": "water"},
            {"text": "дім",    "translit": "dim",    "gloss": "house"},
            {"text": "сонце",  "translit": "sontse", "gloss": "sun"},
            {"text": "книга",  "translit": "knyha",  "gloss": "book"},
        ],
        "lines": [
            {"text": "Мене звати Софія.",                "translit": "Mene zvaty Sofiya.",                "gloss": "My name is Sofiya."},
            {"text": "Мама розповідає мені казку.",       "translit": "Mama rozpovidaye meni kazku.",      "gloss": "Mother tells me a story."},
            {"text": "Сонце сходить на сході.",          "translit": "Sontse skhodyt na skhodi.",         "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "vyshyvanka_day", "title": "Vyshyvanka Day",
             "text": "Celebrated in May — people of all ages wear vyshyvanka, traditionally embroidered shirts, to honour Ukrainian heritage."},
        ],
        "stories": [
            {"key": "rukavychka", "title": "Рукавичка", "translit": "Rukavychka",
             "gloss": "The Mitten",
             "synopsis": "Дідусь упустив рукавичку в лісі. Одна за одною туди залізли звірята, аж доки рукавичка не стала затісною для всіх."},
            {"key": "ivasyk_telesyk", "title": "Івасик-Телесик", "translit": "Ivasyk-Telesyk",
             "gloss": "Ivasyk-Telesyk",
             "synopsis": "Хлопчик Івасик-Телесик випливав на човнику до батьків, але мусив бути обережним і не довіряти голосу відьми."},
        ],
    },
    "ro": {
        "name": "Romanian",
        "alphabet": [
            {"char": "A", "translit": "a", "hint": "as in 'father'"},
            {"char": "Ă", "translit": "ă", "hint": "as in 'about'"},
            {"char": "Â", "translit": "â", "hint": "close to î"},
            {"char": "B", "translit": "b", "hint": ""},
            {"char": "C", "translit": "c", "hint": ""},
            {"char": "D", "translit": "d", "hint": ""},
        ],
        "words": [
            {"text": "mamă",  "translit": "mamă",  "gloss": "mother"},
            {"text": "apă",   "translit": "apă",   "gloss": "water"},
            {"text": "casă",  "translit": "casă",  "gloss": "house"},
            {"text": "soare", "translit": "soare", "gloss": "sun"},
            {"text": "carte", "translit": "carte", "gloss": "book"},
        ],
        "lines": [
            {"text": "Mă numesc Ana.",                 "translit": "Mă numesc Ana.",                 "gloss": "My name is Ana."},
            {"text": "Mama îmi spune o poveste.",      "translit": "Mama îmi spune o poveste.",      "gloss": "Mother tells me a story."},
            {"text": "Soarele răsare la est.",         "translit": "Soarele răsare la est.",         "gloss": "The sun rises in the east."},
        ],
        "customs": [
            {"key": "martisor", "title": "Mărțișor",
             "text": "On March 1st, small red-and-white string trinkets are given as gifts to mark the start of spring."},
        ],
        "stories": [
            {"key": "capra_trei_iezi", "title": "Capra cu trei iezi", "translit": "Capra cu trei iezi",
             "gloss": "The Goat and Her Three Kids",
             "synopsis": "O capră își avertizează cei trei iezi să nu deschidă ușa nimănui cât ea e plecată — dar un lup viclean le imită vocea."},
            {"key": "punguta_doi_bani", "title": "Punguța cu doi bani", "translit": "Punguța cu doi bani",
             "gloss": "The Little Purse with Two Coins",
             "synopsis": "Un cocoș cinstit găsește doi bani și, după multe încercări, ajunge cu bine acasă la baba și moșneagul lui."},
        ],
    },
}

STOPS = ["alphabet", "words", "lines", "customs", "story"]


def list_languages():
    """[(code, name), ...] for sign-up dropdowns."""
    return [(code, data["name"]) for code, data in LANGUAGES.items()]


def get_language(code):
    return LANGUAGES.get(code)


def pick_item(language_code, stop):
    """Return one content item for a given language + stop, cycling
    through the pool. 'story' returns from the stories list (2 items)."""
    import random
    lang = LANGUAGES.get(language_code)
    if not lang:
        return None
    key = "stories" if stop == "story" else stop
    pool = lang.get(key, [])
    if not pool:
        return None
    return random.choice(pool)
