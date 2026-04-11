import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

TOKEN = "8222684433:AAGl7T3wcl3ix-K-yaLcHLtkWOeWZd4EaUA"

logging.basicConfig(level=logging.INFO)

GLOSSARY = [
    {
        "term": "Port",
        "ru": "Левый борт",
        "file_id": "CQACAgIAAxkBAAMdadW4TGAhwHmzRyXnJbqSv6ewVBIAAnqeAAIXELFKZX9-mXLEUkU7BA"
    },
    {
        "term": "Starboard",
        "ru": "Правый борт",
        "file_id": "CQACAgIAAxkBAAMbadW4TDgWnvdPf7qq_scWI_yFRCYAanieAAIXELFK3uGIBiPuSII7BA"
    },
    {
        "term": "Underway",
        "ru": "На ходу",
        "file_id": "CQACAgIAAxkBAAMeadW4TCirSAABQzFKQNCrorYwPCkXAAJ7ngACFxCxSpL8H-CBi_BbOwQ"
    },
    {
        "term": "Overtaking",
        "ru": "Обгон",
        "file_id": "CQACAgIAAxkBAAMZadW4TIR3oU6eb7cE-mpWYAI66DkAAnaeAAIXELFKX4lLnsLEOug7BA"
    },
    {
        "term": "Stand-on vessel",
        "ru": "Привилегированное судно",
        "file_id": "CQACAgIAAxkBAAMcadW4TNDISQVB_rkXQg18rBXIs10AAnmeAAIXELFKWToEjKf_myY7BA"
    },
    {
        "term": "Give-way vessel",
        "ru": "Уступающее судно",
        "file_id": "CQACAgIAAxkBAAMfadW4TD_GyIjTekzxb5SXQYE-ZRwAAnyeAAIXELFKIMD_bOWOVTE7BA"
    },
    {
        "term": "Rules of the Road",
        "ru": "Правила плавания",
        "file_id": "CQACAgIAAxkBAAMaadW4TGT9JISiKDuFDptjii8tCGsAAneeAAIXELFKiytUC_no1GE7BA"
    },
]

QUESTIONS = [
    {
        "en_q": "INLAND ONLY. Your vessel is meeting another vessel head to head. To comply with the steering and sailing rules, you should:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Ваше судно встречается с другим судном нос к носу. Согласно правилам маневрирования, вы должны:",
        "en_options": ["A) Sound the danger signal", "B) Sound one prolonged and two short blasts", "C) Exchange two short blasts", "D) Exchange one short blast"],
        "ru_options": ["A) Подать сигнал опасности", "B) Один продолжительный и два коротких", "C) Обменяться двумя короткими", "D) Обменяться одним коротким"],
        "correct": 3,
        "en_explain": "Inland Rule 34: vessels meeting head-on exchange ONE short blast, each vessel turns right and passes port-to-port.",
        "ru_explain": "Правило 34: суда обмениваются ОДНИМ коротким сигналом, каждый берёт вправо и расходятся левыми бортами.",
        "audio_q": "CQACAgIAAxkBAAICGmnZ25vY7CxTnS1blnADTRC-nv6FAAKBoQACZJzJSqFTUbMNj0qBOwQ",
        "audio_a": "CQACAgIAAxkBAAICHGnZ26-25tlg94FOi4c234gV_eFNAAKCoQACZJzJSgXLPSVZHLiAOwQ",
    },
    {
        "en_q": "INLAND ONLY. What is the whistle signal for a power-driven vessel leaving a dock?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Какой сигнал подаёт моторное судно при отходе от причала?",
        "en_options": ["A) One short blast", "B) Three short blasts", "C) One prolonged blast", "D) Three prolonged blasts"],
        "ru_options": ["A) Один короткий", "B) Три коротких", "C) Один продолжительный", "D) Три продолжительных"],
        "correct": 2,
        "en_explain": "Inland Rules: a vessel leaving a dock sounds ONE prolonged blast (4-6 sec) to warn nearby vessels.",
        "ru_explain": "Внутренние воды: судно, отходящее от причала, подаёт ОДИН продолжительный сигнал (4-6 сек).",
        "audio_q": "CQACAgIAAxkBAAIByWnZmIedRlHZ5ShXdf4jCKpRh7tNAAJSmQAC5ebISstKaG5UP-4xOwQ",
        "audio_a": "CQACAgIAAxkBAAIBy2nZnTp77Cb62yudny_7dG-PF875AAJbmQAC5ebISrZIXYwr2tzQOwQ",
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to overtake on her PORT side. You sound:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете судно в узком канале и хотите обогнать его с ЛЕВОГО борта. Вы подаёте:",
        "en_options": ["A) One short blast", "B) Two short blasts", "C) Two prolonged + one short", "D) Two prolonged + two short"],
        "ru_options": ["A) Один короткий", "B) Два коротких", "C) Два продолжительных + один короткий", "D) Два продолжительных + два коротких"],
        "correct": 1,
        "en_explain": "Inland Rule 34: overtaking on PORT side = TWO short blasts. Overtaken vessel responds with same signal to confirm.",
        "ru_explain": "Правило 34: обгон с левого (PORT) борта = ДВА коротких сигнала. Обгоняемое судно отвечает тем же сигналом.",
        "audio_q": "CQACAgIAAxkBAAIBzWnZo6J3FL7oyhUxsy20C2QhrntjAAJ8mQAC5ebISlN3aprgKd7POwQ",
        "audio_a": "CQACAgIAAxkBAAIBz2nZo9otkbPV12PrZ4Q4EkinzXitAAJ9mQAC5ebISoDLTOefFwSYOwQ",
    },
    {
        "en_q": "INLAND ONLY. You agreed by radio to pass ASTERN of a vessel on your starboard. You MUST:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. По радио договорились пройти за кормой судна справа. Вы ОБЯЗАНЫ:",
        "en_options": ["A) Sound one short blast", "B) Sound two short blasts", "C) Change course to starboard", "D) None of the above"],
        "ru_options": ["A) Один короткий сигнал", "B) Два коротких сигнала", "C) Изменить курс вправо", "D) Ничего из вышеперечисленного"],
        "correct": 3,
        "en_explain": "Inland Rule 34(h): agreement by radiotelephone is sufficient. No additional whistle signals required.",
        "ru_explain": "Правило 34(h): соглашение по радио достаточно. Дополнительных звуковых сигналов не требуется.",
        "audio_q": "CQACAgIAAxkBAAIB0WnZ0YTWElrxD7oG8n99sTgVB0lBAAIMoQACZJzJSm8XTE6UjF91OwQ",
        "audio_a": "CQACAgIAAxkBAAIB02nZ0dA1z_kjvXrQhKLSsIYveCvjAAIPoQACZJzJSrWIjBqimgK7OwQ",
    },
    {
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to pass on her STARBOARD side. You may:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете судно в узком канале и хотите обойти его с ПРАВОГО борта. Вы можете:",
        "en_options": ["A) Contact her by radio to arrange passage", "B) Overtake without whistle signals", "C) Sound five short blasts", "D) All of the above"],
        "ru_options": ["A) Связаться по радио для согласования", "B) Обогнать без сигналов", "C) Подать пять коротких", "D) Всё вышеперечисленное"],
        "correct": 0,
        "en_explain": "Inland Rules: overtaking on STARBOARD side is non-standard. Only permitted after radio agreement.",
        "ru_explain": "Обгон с правого борта — нестандартный манёвр. Разрешён только после согласования по радио.",
        "audio_q": "CQACAgIAAxkBAAIB1WnZ0fJ2q2uUhYYAAUzC9JPg9RTynwACEqEAAmScyUrEEFRaNP81fjsE",
        "audio_a": "CQACAgIAAxkBAAIB12nZ0gi3BdawU0h_wGD9ElUXl4VoAAIToQACZJzJStz-qqatYazmOwQ",
    },
    {
        "en_q": "Another vessel is crossing your course starboard to port and you doubt her intentions. You:",
        "ru_q": "Другое судно пересекает ваш курс справа налево, вы сомневаетесь в его намерениях. Вы:",
        "en_options": ["A) Must sound the danger signal", "B) Must back down", "C) May sound the danger signal", "D) Sound one short blast"],
        "ru_options": ["A) Обязаны подать сигнал опасности", "B) Обязаны дать задний ход", "C) Можете подать сигнал опасности", "D) Подать один короткий"],
        "correct": 0,
        "en_explain": "Rule 34(d): in doubt about another vessel's intentions — MUST sound danger signal (5+ short blasts). Mandatory.",
        "ru_explain": "Правило 34(d): при сомнении в намерениях — ОБЯЗАНЫ подать сигнал опасности (5+ коротких). Обязательно.",
        "audio_q": "CQACAgIAAxkBAAIB2WnZ03t6mNFdCcoXemBLQj6g4Xt0AAIdoQACZJzJSjQFdZnogdN2OwQ",
        "audio_a": "CQACAgIAAxkBAAIB22nZ04rk7NByXOTZxxNX4isbqlp2AAIfoQACZJzJSqZG5tu8PtJlOwQ",
    },
    {
        "en_q": "INLAND ONLY. Maneuvering signals on inland waters are sounded by:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Манёвренные сигналы на внутренних водах подаются:",
        "en_options": ["A) All vessels meeting/crossing/overtaking in sight", "B) All vessels within half a mile, not in sight", "C) Power-driven vessels overtaking in sight / crossing within half a mile in sight", "D) Power-driven vessels crossing within half a mile, NOT in sight"],
        "ru_options": ["A) Всеми судами при встрече/пересечении/обгоне в видимости", "B) Всеми судами в пределах полумили вне видимости", "C) Моторными: при обгоне в видимости / пересечении в полумиле и в видимости", "D) Моторными при пересечении в полумиле вне видимости"],
        "correct": 2,
        "en_explain": "Inland Rules: maneuvering signals for power-driven vessels only, in sight of each other. Crossing: also within half a mile.",
        "ru_explain": "Манёвренные сигналы — только для моторных судов в пределах видимости. Пересечение курсов — дополнительно в пределах полумили.",
        "audio_q": "CQACAgIAAxkBAAIB3WnZ05-uamcPsn9lmuOpyTeeTLq9AAIhoQACZJzJSuTRdvHRFbTQOwQ",
        "audio_a": "CQACAgIAAxkBAAIB32nZ063DVxMJV3X6GeSc1ZKzoED_AAIioQACZJzJSqIMQmX9L7BAOwQ",
    },
    {
        "en_q": "INLAND ONLY. A light used to signal passing intentions must be:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Огонь для сигнализации намерений при расхождении должен быть:",
        "en_options": ["A) All-round white OR yellow", "B) All-round yellow only", "C) All-round white only", "D) 225° white only"],
        "ru_options": ["A) Круговой белый ИЛИ жёлтый", "B) Только круговой жёлтый", "C) Только круговой белый", "D) Только белый 225°"],
        "correct": 0,
        "en_explain": "Inland Rule 34(b): all-round white OR yellow light permitted for signaling passing intentions.",
        "ru_explain": "Правило 34(b): разрешён круговой белый ИЛИ жёлтый огонь для сигнализации намерений.",
        "audio_q": "CQACAgIAAxkBAAIB4WnZ07moRzVNadTPXws-PTcdXxXuAAIjoQACZJzJSqXxjVISCq_nOwQ",
        "audio_a": "CQACAgIAAxkBAAIB42nZ08yB-Ea7O4YCcSCP6nQ9ZG54AAIkoQACZJzJStmnVAc942RlOwQ",
    },
    {
        "en_q": "INLAND ONLY. What MAY indicate a partly submerged object being towed?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Что МОЖЕТ обозначать частично погружённый буксируемый объект?",
        "en_options": ["A) Black cone, apex up", "B) Two all-round yellow lights at each end", "C) Searchlight from towing vessel aimed at the tow", "D) All of the above"],
        "ru_options": ["A) Чёрный конус вершиной вверх", "B) Два круговых жёлтых огня на каждом конце", "C) Прожектор с буксировщика на объект", "D) Всё вышеперечисленное"],
        "correct": 2,
        "en_explain": "Inland Rules: searchlight from towing vessel aimed at the tow is permitted when lights cannot be mounted on the object.",
        "ru_explain": "Прожектор с буксировщика допускается когда огни невозможно установить на объекте.",
        "audio_q": "CQACAgIAAxkBAAIB5WnZ0-Ls2yQ3HyZ47vk6RE1JdgZmAAImoQACZJzJSmrdy53-RzX5OwQ",
        "audio_a": "CQACAgIAAxkBAAIB52nZ0_ONn6EnneiqDKiLkygycIidAAInoQACZJzJSr7AWv4ojcTXOwQ",
    },
    {
        "en_q": "BOTH INT & INLAND. Underway in fog, you hear ONE prolonged blast. This indicates:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. В тумане слышите ОДИН продолжительный сигнал. Это:",
        "en_options": ["A) Sailboat underway", "B) Vessel towing", "C) Power vessel making way", "D) Vessel being towed"],
        "ru_options": ["A) Парусное судно на ходу", "B) Судно с буксиром", "C) Моторное судно, идущее вперёд", "D) Буксируемое судно"],
        "correct": 2,
        "en_explain": "Rule 35: ONE prolonged blast every 2 min = power-driven vessel making way. Towing: one prolonged + two short.",
        "ru_explain": "Правило 35: ОДИН продолжительный каждые 2 мин = моторное судно идёт вперёд. Буксировщик: один продолжительный + два коротких.",
        "audio_q": "CQACAgIAAxkBAAIB6WnZ1EMFFFVEvAmXRmMXYUs20ha6AAIvoQACZJzJSiWgLr47NAHROwQ",
        "audio_a": "CQACAgIAAxkBAAIB62nZ1FedxxFoCcnz5hENyme-0iBlAAIzoQACZJzJSkXaFE6fm4yaOwQ",
    },
    {
        "en_q": "A vessel is 'in sight' of another vessel when:",
        "ru_q": "Судно находится 'в пределах видимости' другого судна когда:",
        "en_options": ["A) She is visible on radar", "B) She can be observed visually from the other vessel", "C) She is within VHF radio range", "D) She is within one mile"],
        "ru_options": ["A) Она видна на радаре", "B) Её можно наблюдать визуально с другого судна", "C) Она в зоне VHF радио", "D) Она в пределах одной мили"],
        "correct": 1,
        "en_explain": "Rule 3(k): 'in sight' means observed visually. Radar contact alone does not count.",
        "ru_explain": "Правило 3(k): 'в пределах видимости' означает визуальное наблюдение. Только радар не считается.",
        "audio_q": "CQACAgIAAxkBAAIB7WnZ1G1i2hj120s5wCZuEkbia5MZAAI1oQACZJzJSvgkqv6OvIOSOwQ",
        "audio_a": "CQACAgIAAxkBAAIB72nZ1IQm2ayNiq9oizhUFt91Tp2SAAI2oQACZJzJSoJn6SnHcj5eOwQ",
    },
    {
        "en_q": "You see a vessel displaying the code flag 'LIMA' below which is an 'O' flag. This vessel is:",
        "ru_q": "Вы видите судно с флагом 'LIMA' под которым флаг 'O'. Это судно:",
        "en_options": ["A) requesting a pilot", "B) in distress", "C) carrying dangerous cargo", "D) restricted in ability to maneuver"],
        "ru_options": ["A) запрашивает лоцмана", "B) терпит бедствие", "C) перевозит опасный груз", "D) ограничено в манёвре"],
        "correct": 1,
        "en_explain": "Flag 'O' (Oscar) means 'man overboard' — vessel in distress.",
        "ru_explain": "Флаг 'O' (Оскар) означает 'человек за бортом' — судно терпит бедствие.",
        "audio_q": "CQACAgIAAxkBAAIB8WnZ1J4b1CMOe3d6S81v_kDVtGpPAAI4oQACZJzJStuhTSixWpdNOwQ",
        "audio_a": "CQACAgIAAxkBAAIB82nZ1LYAAeT-StKi1t3w9jFdXpbnbQACO6EAAmScyUpT9w8TPXfsyjsE",
    },
    {
        "en_q": "If it becomes necessary for a stand-on vessel to take action to avoid collision, she shall NOT:",
        "ru_q": "Если привилегированному судну необходимо предпринять действия для предотвращения столкновения, оно НЕ должно:",
        "en_options": ["A) alter course to starboard", "B) turn to port for a vessel on her own port side", "C) slow down", "D) sound the danger signal"],
        "ru_options": ["A) изменить курс вправо", "B) повернуть влево навстречу судну со своего левого борта", "C) сбросить скорость", "D) подать сигнал опасности"],
        "correct": 1,
        "en_explain": "Rule 17(c): stand-on vessel shall NOT turn to port for a vessel on her own port side.",
        "ru_explain": "Правило 17(c): привилегированное судно НЕ должно поворачивать влево навстречу судну со своего левого борта.",
        "audio_q": "CQACAgIAAxkBAAIB9WnZ1M3CN3mEu1-cfW37jJH1ymqFAAI-oQACZJzJSsPFMoXWQxraOwQ",
        "audio_a": "CQACAgIAAxkBAAIB92nZ1OOlsQdBUf3eD9wxi25-sm1HAAJBoQACZJzJSpEay5GioNpGOwQ",
    },
    {
        "en_q": "A pilot vessel on pilotage duty at night will show sidelights and a sternlight:",
        "ru_q": "Лоцманское судно при исполнении обязанностей ночью показывает бортовые огни и кормовой огонь:",
        "en_options": ["A) only when anchored", "B) only when making way", "C) at any time when underway", "D) only in restricted visibility"],
        "ru_options": ["A) только на якоре", "B) только на ходу с движением", "C) в любое время когда на ходу", "D) только при ограниченной видимости"],
        "correct": 2,
        "en_explain": "Rule 29: pilot vessel on duty shows white over red all-round lights, plus sidelights and sternlight at any time when underway.",
        "ru_explain": "Правило 29: лоцманское судно при исполнении обязанностей показывает белый над красным, плюс бортовые и кормовой в любое время на ходу.",
        "audio_q": "CQACAgIAAxkBAAIB-WnZ1PFgKH1vr0VOvE4sVH7-IJN9AAJDoQACZJzJSoG-Ve-bIJ46OwQ",
        "audio_a": "CQACAgIAAxkBAAIB-2nZ1QcLv9s-kBuEy59Bc78NZJ-SAAJFoQACZJzJSkppBA0bfP46OwQ",
    },
    {
        "en_q": "When taking action to avoid collision, you should:",
        "ru_q": "При выполнении манёвра для предотвращения столкновения вы должны:",
        "en_options": ["A) always turn to starboard", "B) always slow down", "C) make sure the action is taken in enough time", "D) sound one short blast"],
        "ru_options": ["A) всегда поворачивать вправо", "B) всегда сбрасывать скорость", "C) убедиться что манёвр выполнен заблаговременно", "D) подать один короткий сигнал"],
        "correct": 2,
        "en_explain": "Rule 8: any action to avoid collision shall be taken in ample time, shall be large enough to be readily apparent.",
        "ru_explain": "Правило 8: любой манёвр для предотвращения столкновения должен быть предпринят заблаговременно и быть достаточно значительным.",
        "audio_q": "CQACAgIAAxkBAAIB_WnZ1RtfHqoQGSA0FOjCbZUhszo6AAJGoQACZJzJSv8LjDsFgZmyOwQ",
        "audio_a": "CQACAgIAAxkBAAIB_2nZ1SqAnheLLkc1-fa2hKMqTFKZAAJHoQACZJzJShrCjTEceBFnOwQ",
    },
    {
        "en_q": "Which vessel may combine her sidelights and sternlight in one lantern on the centerline?",
        "ru_q": "Какое судно может объединить бортовые огни и кормовой огонь в один фонарь по centerline?",
        "en_options": ["A) Any vessel under 20 meters", "B) A 16-meter sailing vessel", "C) A 12-meter power vessel", "D) Any vessel under 12 meters"],
        "ru_options": ["A) Любое судно до 20 метров", "B) Парусное судно 16 метров", "C) Моторное судно 12 метров", "D) Любое судно до 12 метров"],
        "correct": 1,
        "en_explain": "Rule 25(b): a sailing vessel under 20 meters may combine sidelights and sternlight in one lantern at or near the top of the mast.",
        "ru_explain": "Правило 25(b): парусное судно менее 20 метров может объединить бортовые и кормовой огни в один фонарь на верхушке мачты.",
        "audio_q": "CQACAgIAAxkBAAICAWnZ1UgaOhZ15_5We4jKPIqaO18cAAJKoQACZJzJStrnlb6vfOPcOwQ",
        "audio_a": "CQACAgIAAxkBAAICA2nZ1VYLf4U2VKrrR9TpfF-5WyAkAAJLoQACZJzJSuR0vdY85fOJOwQ",
    },
    {
        "en_q": "A vessel engaged in fishing, and at anchor, shall show:",
        "ru_q": "Судно, занятое рыболовством и стоящее на якоре, должно показывать:",
        "en_options": ["A) fishing lights only", "B) anchor light and fishing lights", "C) an anchor light", "D) no lights required"],
        "ru_options": ["A) только огни рыболовства", "B) якорный огонь и огни рыболовства", "C) якорный огонь", "D) огни не требуются"],
        "correct": 2,
        "en_explain": "Rule 26: a vessel fishing at anchor shows anchor light only — fishing lights are not required at anchor.",
        "ru_explain": "Правило 26: судно на якоре занятое рыболовством показывает только якорный огонь — огни рыболовства на якоре не требуются.",
        "audio_q": "CQACAgIAAxkBAAICBWnZ1Wm0-hpRuP_0u9ovCxyaAaEVAAJMoQACZJzJSttiwgxal7KcOwQ",
        "audio_a": "CQACAgIAAxkBAAICB2nZ1XenCEp4ExzB3U5qLOHnVwl6AAJNoQACZJzJSkK58fGTqFoUOwQ",
    },
    {
        "en_q": "Which statement concerning maneuvering in restricted visibility is TRUE?",
        "ru_q": "Какое утверждение о манёврировании в условиях ограниченной видимости ВЕРНО?",
        "en_options": ["A) You may only use engine to maneuver", "B) A vessel which hears a fog signal forward of her beam shall stop her engines", "C) You must anchor immediately", "D) Speed must be reduced to bare steerageway"],
        "ru_options": ["A) Можно использовать только двигатель", "B) Судно слышащее туманный сигнал впереди траверза должно застопорить машины", "C) Нужно немедленно встать на якорь", "D) Скорость должна быть снижена до минимальной управляемой"],
        "correct": 1,
        "en_explain": "Rule 19(e): vessel hearing fog signal forward of beam shall reduce speed to minimum, stop engines if necessary, navigate with extreme caution.",
        "ru_explain": "Правило 19(e): судно слышащее туманный сигнал впереди траверза должно снизить скорость до минимума, застопорить машины при необходимости.",
        "audio_q": "CQACAgIAAxkBAAICCWnZ1dCHqfaNtMPzxoEkJ6ANTZ3oAAJOoQACZJzJSpFBKr0EkGtqOwQ",
        "audio_a": "CQACAgIAAxkBAAICC2nZ1d-ku0SZS7_xHDs2_12TOh2KAAJQoQACZJzJSpjoeSl-90JqOwQ",
    },
    {
        "en_q": "A sailing vessel of over 20 meters in length underway must show:",
        "ru_q": "Парусное судно длиной более 20 метров на ходу должно показывать:",
        "en_options": ["A) masthead light and sidelights only", "B) sidelights and sternlight only", "C) a sternlight", "D) all-round white light"],
        "ru_options": ["A) топовый огонь и бортовые огни", "B) только бортовые огни и кормовой", "C) кормовой огонь", "D) круговой белый огонь"],
        "correct": 2,
        "en_explain": "Rule 25(a): sailing vessel underway shall exhibit sidelights and a sternlight. No masthead light.",
        "ru_explain": "Правило 25(a): парусное судно на ходу показывает бортовые огни и кормовой огонь. Топовый огонь не требуется.",
        "audio_q": "CQACAgIAAxkBAAICDWnZ1esZ30n7WmAitxMAAd2CG2tTbQACUqEAAmScyUp4rRITr9GQnTsE",
        "audio_a": "CQACAgIAAxkBAAICD2nZ1flvD4nJFNZ1XdtW-qwDGUYWAAJToQACZJzJSkt3j1nRpTXcOwQ",
    },
    {
        "en_q": "A power-driven vessel, when towing astern, shall show:",
        "ru_q": "Моторное судно при буксировке на кормовом тросе должно показывать:",
        "en_options": ["A) two masthead lights and sidelights only", "B) one all-round yellow light", "C) a towing light in a vertical line above the sternlight", "D) three masthead lights in a vertical line"],
        "ru_options": ["A) два топовых огня и бортовые огни", "B) один круговой жёлтый огонь", "C) буксировочный огонь вертикально над кормовым огнём", "D) три топовых огня в вертикальной линии"],
        "correct": 2,
        "en_explain": "Rule 24(a): towing vessel shows masthead lights, sidelights, sternlight, and a towing light (yellow) in a vertical line above the sternlight.",
        "ru_explain": "Правило 24(a): буксировщик показывает топовые огни, бортовые, кормовой и буксировочный (жёлтый) вертикально над кормовым.",
        "audio_q": "CQACAgIAAxkBAAICEWnZ1gc4LYIg7xEp2JrMLZwnp__PAAJUoQACZJzJSqfS_AqhBWLZOwQ",
        "audio_a": "CQACAgIAAxkBAAICE2nZ1haJ1rdXxqbgSPLjCcacPx5RAAJWoQACZJzJSnrHgL4vPH3fOwQ",
    },
]

user_state = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📝 Тест / Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("📖 Глоссарий / Glossary", callback_data="menu_glossary")],
        [InlineKeyboardButton("🚗 За рулём / Drive Mode", callback_data="menu_drive")],
    ]
    update.message.reply_text(
        "⚓ Добро пожаловать в Captain6PackBot!\n\nВыберите режим / Choose mode:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_glossary(chat_id, context, index, message_to_delete=None):
    term = GLOSSARY[index]
    caption = f"📖 {index + 1} из {len(GLOSSARY)}\n\n🇺🇸 {term['term']}\n🇷🇺 {term['ru']}"
    prev_index = (index - 1) % len(GLOSSARY)
    keyboard = [
        [InlineKeyboardButton("⬅️", callback_data=f"glo{prev_index}")],
        [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu")],
    ]
    if message_to_delete:
        try:
            message_to_delete.delete()
        except:
            pass
    context.bot.send_audio(
        chat_id=chat_id,
        audio=term["file_id"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_question(query, state):
    q = QUESTIONS[state["q_index"]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    lang_btn = "🇺🇸 English" if lang == "ru" else "🇷🇺 Русский"
    options_text = "\n".join(options)
    full_text = f"❓ Вопрос {state['q_index'] + 1} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
    buttons = [
        [
            InlineKeyboardButton("A", callback_data="answer_0"),
            InlineKeyboardButton("B", callback_data="answer_1"),
            InlineKeyboardButton("C", callback_data="answer_2"),
            InlineKeyboardButton("D", callback_data="answer_3"),
        ],
        [InlineKeyboardButton(lang_btn, callback_data="toggle_lang")],
    ]
    if q.get("audio_q"):
        buttons.append([InlineKeyboardButton("🔊 Слушать вопрос", callback_data="play_q")])
    query.edit_message_text(full_text, reply_markup=InlineKeyboardMarkup(buttons))

def get_file_id(update: Update, context: CallbackContext):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        update.message.reply_text(f"📷 Фото file_id:\n{file_id}")
    elif update.message.audio:
        file_id = update.message.audio.file_id
        name = update.message.audio.file_name
        update.message.reply_text(f"{name}:\n{file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        name = update.message.document.file_name
        update.message.reply_text(f"{name}:\n{file_id}")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if user_id not in user_state:
        user_state[user_id] = {"lang": "ru", "q_index": 0, "g_index": 0}

    state = user_state[user_id]

    if query.data == "menu_quiz":
        state["q_index"] = 0
        send_question(query, state)

    elif query.data == "menu_glossary":
        state["g_index"] = 0
        send_glossary(query.message.chat_id, context, 0, query.message)

    elif query.data.startswith("glo"):
        index = int(query.data[3:])
        state["g_index"] = index
        send_glossary(query.message.chat_id, context, index, query.message)

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📝 Тест / Quiz", callback_data="menu_quiz")],
            [InlineKeyboardButton("📖 Глоссарий / Glossary", callback_data="menu_glossary")],
            [InlineKeyboardButton("🚗 За рулём / Drive Mode", callback_data="menu_drive")],
        ]
        try:
            query.message.delete()
        except:
            pass
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="⚓ Добро пожаловать в Captain6PackBot!\n\nВыберите режим / Choose mode:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "toggle_lang":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        send_question(query, state)

    elif query.data == "play_q":
        q = QUESTIONS[state["q_index"]]
        if q.get("audio_q"):
            context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_q"])

    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["q_index"]]
        lang = state["lang"]
        explain = q["ru_explain"] if lang == "ru" else q["en_explain"]
        correct_letter = ["A", "B", "C", "D"][q["correct"]]
        if chosen == q["correct"]:
            result = f"✅ Правильно! / Correct!\n\n{explain}"
        else:
            chosen_letter = ["A", "B", "C", "D"][chosen]
            result = f"❌ Неверно! Вы выбрали {chosen_letter}, правильный ответ: {correct_letter}\n\n{explain}"
        lang_btn = "🇺🇸 English" if lang == "ru" else "🇷🇺 Русский"
        buttons = [
            [InlineKeyboardButton("➡️ Следующий / Next", callback_data="next_question")],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
        ]
        if q.get("audio_a"):
            buttons.append([InlineKeyboardButton("🔊 Слушать ответ", callback_data="play_a")])
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "toggle_lang_answer":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        q = QUESTIONS[state["q_index"]]
        lang = state["lang"]
        explain = q["ru_explain"] if lang == "ru" else q["en_explain"]
        correct_letter = ["A", "B", "C", "D"][q["correct"]]
        result = f"💡 Правильный ответ: {correct_letter}\n\n{explain}"
        lang_btn = "🇺🇸 English" if lang == "ru" else "🇷🇺 Русский"
        buttons = [
            [InlineKeyboardButton("➡️ Следующий / Next", callback_data="next_question")],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
        ]
        if q.get("audio_a"):
            buttons.append([InlineKeyboardButton("🔊 Слушать ответ", callback_data="play_a")])
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "play_a":
        q = QUESTIONS[state["q_index"]]
        if q.get("audio_a"):
            context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_a"])

    elif query.data == "next_question":
        state["q_index"] = (state["q_index"] + 1) % len(QUESTIONS)
        send_question(query, state)

    elif query.data == "menu_drive":
        query.edit_message_text("🚗 Режим за рулём в разработке / Drive mode coming soon!")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.photo | Filters.audio | Filters.document, get_file_id))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
