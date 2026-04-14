import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

TOKEN = "8222684433:AAGl7T3wcl3ix-K-yaLcHLtkWOeWZd4EaUA"

logging.basicConfig(level=logging.INFO)

GLOSSARY = [
    {"term": "Port", "ru": "Левый борт", "file_id": "CQACAgIAAxkBAAMdadW4TGAhwHmzRyXnJbqSv6ewVBIAAnqeAAIXELFKZX9-mXLEUkU7BA"},
    {"term": "Starboard", "ru": "Правый борт", "file_id": "CQACAgIAAxkBAAMbadW4TDgWnvdPf7qq_scWI_yFRCYAanieAAIXELFK3uGIBiPuSII7BA"},
    {"term": "Underway", "ru": "На ходу", "file_id": "CQACAgIAAxkBAAMeadW4TCirSAABQzFKQNCrorYwPCkXAAJ7ngACFxCxSpL8H-CBi_BbOwQ"},
    {"term": "Overtaking", "ru": "Обгон", "file_id": "CQACAgIAAxkBAAMZadW4TIR3oU6eb7cE-mpWYAI66DkAAnaeAAIXELFKX4lLnsLEOug7BA"},
    {"term": "Stand-on vessel", "ru": "Привилегированное судно", "file_id": "CQACAgIAAxkBAAMcadW4TNDISQVB_rkXQg18rBXIs10AAnmeAAIXELFKWToEjKf_myY7BA"},
    {"term": "Give-way vessel", "ru": "Уступающее судно", "file_id": "CQACAgIAAxkBAAMfadW4TD_GyIjTekzxb5SXQYE-ZRwAAnyeAAIXELFKIMD_bOWOVTE7BA"},
    {"term": "Rules of the Road", "ru": "Правила плавания", "file_id": "CQACAgIAAxkBAAMaadW4TGT9JISiKDuFDptjii8tCGsAAneeAAIXELFKiytUC_no1GE7BA"},
]

QUESTIONS = [
    {
        "num": 1,
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
        "num": 2,
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
        "num": 3,
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
        "num": 4,
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
        "num": 5,
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
        "num": 6,
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
        "num": 7,
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
        "num": 8,
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
        "num": 9,
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
        "num": 10,
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
        "num": 11,
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel is in sight of another vessel when:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно находится в зоне видимости другого судна, когда:",
        "en_options": ["A) She can be observed by radar", "B) She can be observed visually from the other vessel", "C) She can be plotted on radar well enough to determine her heading", "D) Her fog signal can be heard"],
        "ru_options": ["A) Она наблюдается по радару", "B) Она наблюдается визуально с другого судна", "C) Её курс определяется по радару", "D) Слышен её туманный сигнал"],
        "correct": 1,
        "en_explain": "Rule 3(k): a vessel is 'in sight' only when she can be observed visually. Radar contact alone does not count.",
        "ru_explain": "Правило 3(k): судно находится в зоне видимости только при визуальном наблюдении. Радар не считается.",
        "audio_q": "CQACAgIAAxkBAAIB7WnZ1G1i2hj120s5wCZuEkbia5MZAAI1oQACZJzJSvgkqv6OvIOSOwQ",
        "audio_a": "CQACAgIAAxkBAAIB72nZ1IQm2ayNiq9oizhUFt91Tp2SAAI2oQACZJzJSoJn6SnHcj5eOwQ",
    },
    {
        "num": 12,
        "en_q": "BOTH INTERNATIONAL & INLAND. You see a vessel displaying the code flag 'LIMA' below which is a red ball. The vessel is:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно показывает флаг 'LIMA' и под ним красный шар. Это означает:",
        "en_options": ["A) Trolling", "B) Getting ready to receive aircraft", "C) Aground", "D) In distress"],
        "ru_options": ["A) Занято троллингом", "B) Готовится принять воздушное судно", "C) На мели", "D) Терпит бедствие"],
        "correct": 3,
        "en_explain": "Flag 'L' (LIMA) + red ball = distress signal. This combination indicates a vessel in distress and needing assistance.",
        "ru_explain": "Флаг 'L' (LIMA) + красный шар = сигнал бедствия. Судно терпит бедствие и нуждается в помощи.",
        "audio_q": "CQACAgIAAxkBAAIB8WnZ1J4b1CMOe3d6S81v_kDVtGpPAAI4oQACZJzJStuhTSixWpdNOwQ",
        "audio_a": "CQACAgIAAxkBAAIB82nZ1LYAAeT-StKi1t3w9jFdXpbnbQACO6EAAmScyUpT9w8TPXfsyjsE",
    },
    {
        "num": 13,
        "en_q": "BOTH INTERNATIONAL & INLAND. If it becomes necessary for a stand-on vessel to take action to avoid collision, she shall NOT, if possible:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Если привилегированному судну необходимо маневрировать для предотвращения столкновения, оно НЕ должно, если возможно:",
        "en_options": ["A) Decrease speed", "B) Increase speed", "C) Turn to port for a vessel on her own port side", "D) Turn to starboard for a vessel on her own port side"],
        "ru_options": ["A) Уменьшать скорость", "B) Увеличивать скорость", "C) Поворачивать влево в сторону судна слева", "D) Поворачивать вправо в сторону судна слева"],
        "correct": 2,
        "en_explain": "Rule 17(c): stand-on vessel shall NOT turn to port when a give-way vessel is on her port side — this would close the gap.",
        "ru_explain": "Правило 17(c): привилегированное судно НЕ должно поворачивать влево если уступающее судно находится слева — это сокращает дистанцию.",
        "audio_q": "CQACAgIAAxkBAAIB9WnZ1M3CN3mEu1-cfW37jJH1ymqFAAI-oQACZJzJSsPFMoXWQxraOwQ",
        "audio_a": "CQACAgIAAxkBAAIB92nZ1OOlsQdBUf3eD9wxi25-sm1HAAJBoQACZJzJSpEay5GioNpGOwQ",
    },
    {
        "num": 14,
        "en_q": "BOTH INTERNATIONAL & INLAND. A pilot vessel on pilotage duty at night will show sidelights and a sternlight:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Лоцманское судно на дежурстве ночью показывает бортовые огни и кормовой огонь:",
        "en_options": ["A) When at anchor", "B) Only when making way", "C) At any time when underway", "D) Only when the identifying lights are not being shown"],
        "ru_options": ["A) На якоре", "B) Только при движении вперёд", "C) В любое время на ходу", "D) Только когда не горят опознавательные огни"],
        "correct": 2,
        "en_explain": "Rule 29: a pilot vessel underway shows sidelights and sternlight at any time, regardless of identifying lights.",
        "ru_explain": "Правило 29: лоцманское судно на ходу показывает бортовые и кормовой огни в любое время, независимо от опознавательных огней.",
        "audio_q": "CQACAgIAAxkBAAIB-WnZ1PFgKH1vr0VOvE4sVH7-IJN9AAJDoQACZJzJSoG-Ve-bIJ46OwQ",
        "audio_a": "CQACAgIAAxkBAAIB-2nZ1QcLv9s-kBuEy59Bc78NZJ-SAAJFoQACZJzJSkppBA0bfP46OwQ",
    },
    {
        "num": 15,
        "en_q": "BOTH INTERNATIONAL & INLAND. When taking action to avoid collision, you should:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. При манёвре для предотвращения столкновения вы должны:",
        "en_options": ["A) Make sure the action is taken in enough time", "B) Not make any large course changes", "C) Not make any large speed changes", "D) All of the above"],
        "ru_options": ["A) Убедиться что манёвр выполнен заблаговременно", "B) Не делать резких изменений курса", "C) Не делать резких изменений скорости", "D) Всё вышеперечисленное"],
        "correct": 0,
        "en_explain": "Rule 8: action to avoid collision must be taken in ample time. Large course/speed changes are encouraged if needed to be effective.",
        "ru_explain": "Правило 8: главное требование — манёвр выполнен заблаговременно и достаточно решительно.",
        "audio_q": "CQACAgIAAxkBAAIB_WnZ1RtfHqoQGSA0FOjCbZUhszo6AAJGoQACZJzJSv8LjDsFgZmyOwQ",
        "audio_a": "CQACAgIAAxkBAAIB_2nZ1SqAnheLLkc1-fa2hKMqTFKZAAJHoQACZJzJShrCjTEceBFnOwQ",
    },
    {
        "num": 16,
        "en_q": "BOTH INTERNATIONAL & INLAND. Which vessel may combine her sidelights and sternlight in one lantern on the fore and aft centerline?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Какое судно может объединить бортовые огни и кормовой огонь в один фонарь на осевой линии?",
        "en_options": ["A) A 16-meter sailing vessel", "B) A 25-meter power-driven vessel", "C) A 28-meter sailing vessel", "D) Any non-self-propelled vessel"],
        "ru_options": ["A) Парусное судно длиной 16 м", "B) Моторное судно длиной 25 м", "C) Парусное судно длиной 28 м", "D) Любое несамоходное судно"],
        "correct": 0,
        "en_explain": "Rule 25(c): sailing vessels under 20 meters may combine sidelights and sternlight in one all-round lantern at the masthead.",
        "ru_explain": "Правило 25(c): только парусные суда менее 20 метров могут использовать комбинированный трёхцветный фонарь на мачте.",
        "audio_q": "CQACAgIAAxkBAAICAWnZ1UgaOhZ15_5We4jKPIqaO18cAAJKoQACZJzJStrnlb6vfOPcOwQ",
        "audio_a": "CQACAgIAAxkBAAICA2nZ1VYLf4U2VKrrR9TpfF-5WyAkAAJLoQACZJzJSuR0vdY85fOJOwQ",
    },
    {
        "num": 17,
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel engaged in fishing, and at anchor, shall show:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно, занятое рыболовством и стоящее на якоре, должно показывать:",
        "en_options": ["A) An anchor light", "B) Sidelights and a sternlight", "C) Three lights in a vertical line, the highest and lowest being red, and the middle being white", "D) None of the above"],
        "ru_options": ["A) Якорный огонь", "B) Бортовые и кормовой огни", "C) Три огня вертикально: верхний и нижний красные, средний белый", "D) Ничего из вышеперечисленного"],
        "correct": 3,
        "en_explain": "Rule 26: a fishing vessel at anchor shows fishing lights only (green over white), not anchor lights or sidelights.",
        "ru_explain": "Правило 26: рыболовное судно на якоре показывает только огни рыболовства (зелёный над белым).",
        "audio_q": "CQACAgIAAxkBAAICBWnZ1Wm0-hpRuP_0u9ovCxyaAaEVAAJMoQACZJzJSttiwgxal7KcOwQ",
        "audio_a": "CQACAgIAAxkBAAICB2nZ1XenCEp4ExzB3U5qLOHnVwl6AAJNoQACZJzJSkK58fGTqFoUOwQ",
    },
    {
        "num": 18,
        "en_q": "BOTH INTERNATIONAL & INLAND. Which statement concerning maneuvering in restricted visibility is FALSE?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Какое утверждение о манёврировании в условиях ограниченной видимости НЕВЕРНО?",
        "en_options": ["A) A vessel which cannot avoid a close-quarters situation shall reduce her speed to bare steerageway.", "B) A vessel which hears a fog signal forward of her beam shall stop her engines.", "C) A vessel which hears a fog signal forward of the beam shall navigate with caution.", "D) If a vessel determines by radar that a close-quarters situation is developing, she shall take avoiding action in ample time."],
        "ru_options": ["A) Судно, не способное избежать опасного сближения, должно снизить скорость до минимальной управляемой.", "B) Судно, услышавшее туманный сигнал по носу, должно застопорить машины.", "C) Судно, услышавшее туманный сигнал по носу, должно следовать с осторожностью.", "D) Если радар показывает опасное сближение — манёвр должен быть выполнен заблаговременно."],
        "correct": 1,
        "en_explain": "Rule 19(e): hearing a fog signal forward — reduce to minimum steerageway. Stopping engines is not required.",
        "ru_explain": "Правило 19(e): услышав туманный сигнал по носу — снизить до минимальной управляемой скорости. Останавливать машины не обязательно.",
        "audio_q": "CQACAgIAAxkBAAICCWnZ1dCHqfaNtMPzxoEkJ6ANTZ3oAAJOoQACZJzJSpFBKr0EkGtqOwQ",
        "audio_a": "CQACAgIAAxkBAAICC2nZ1d-ku0SZS7_xHDs2_12TOh2KAAJQoQACZJzJSpjoeSl-90JqOwQ",
    },
    {
        "num": 19,
        "en_q": "BOTH INTERNATIONAL & INLAND. A sailing vessel of over 20 meters in length underway must show:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Парусное судно длиной более 20 метров на ходу обязано показывать:",
        "en_options": ["A) A red light over a green light at the masthead", "B) A white masthead light", "C) A combined lantern", "D) A sternlight"],
        "ru_options": ["A) Красный над зелёным на мачте", "B) Белый топовый огонь", "C) Комбинированный фонарь", "D) Кормовой огонь"],
        "correct": 3,
        "en_explain": "Rule 25: a sailing vessel over 20m must show sidelights and a sternlight. Combined lantern only permitted under 20m.",
        "ru_explain": "Правило 25: парусное судно более 20 м обязано показывать бортовые и кормовой огонь. Комбинированный фонарь — только до 20 м.",
        "audio_q": "CQACAgIAAxkBAAICDWnZ1esZ30n7WmAitxMAAd2CG2tTbQACUqEAAmScyUp4rRITr9GQnTsE",
        "audio_a": "CQACAgIAAxkBAAICD2nZ1flvD4nJFNZ1XdtW-qwDGUYWAAJToQACZJzJSkt3j1nRpTXcOwQ",
    },
    {
        "num": 20,
        "en_q": "BOTH INTERNATIONAL & INLAND. A power-driven vessel, when towing astern, shall show:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Моторное судно при буксировке за кормой должно показывать:",
        "en_options": ["A) Two towing lights in a vertical line", "B) A towing light in a vertical line above the sternlight", "C) Two towing lights in addition to the sternlight", "D) A small white light in lieu of the sternlight"],
        "ru_options": ["A) Два буксировочных огня вертикально", "B) Буксировочный огонь над кормовым огнём вертикально", "C) Два буксировочных огня в дополнение к кормовому", "D) Малый белый огонь вместо кормового"],
        "correct": 1,
        "en_explain": "Rule 24(a): towing vessel shows a yellow towing light in a vertical line directly above the sternlight.",
        "ru_explain": "Правило 24(a): буксировщик показывает жёлтый буксировочный огонь вертикально над кормовым огнём.",
        "audio_q": "CQACAgIAAxkBAAICEWnZ1gc4LYIg7xEp2JrMLZwnp__PAAJUoQACZJzJSqfS_AqhBWLZOwQ",
        "audio_a": "CQACAgIAAxkBAAICE2nZ1haJ1rdXxqbgSPLjCcacPx5RAAJWoQACZJzJSnrHgL4vPH3fOwQ",
    },
]

user_state = {}

MAIN_MENU_TEXT = "⚓ Добро пожаловать в Captain6PackBot!\n\nВыберите режим / Choose mode:"


def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Тест / Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("📖 Глоссарий / Glossary", callback_data="menu_glossary")],
        [InlineKeyboardButton("🔊👂 Аудирование / Listening 🚗 🏋️", callback_data="menu_drive")],
    ])


def start(update: Update, context: CallbackContext):
    update.message.reply_text(MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())


# ── ГЛОССАРИЙ ──

def glossary_keyboard(index):
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton("Prev", callback_data=f"glo_{index - 1}"))
    nav_row.append(InlineKeyboardButton("Next", callback_data=f"glo_{index + 1}"))
    return InlineKeyboardMarkup([
        nav_row,
        [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu_from_glo")],
    ])


def send_glossary_first(chat_id, context, old_msg_id=None):
    """Отправляет первую карточку, удаляя предыдущее сообщение (текстовое меню)."""
    if old_msg_id:
        try:
            context.bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
        except Exception:
            pass
    term = GLOSSARY[0]
    caption = f"📖 1 из {len(GLOSSARY)}\n\nEN: {term['term']}\nRU: {term['ru']}"
    context.bot.send_audio(
        chat_id=chat_id,
        audio=term["file_id"],
        caption=caption,
        reply_markup=glossary_keyboard(0)
    )


def update_glossary(query, context, index):
    """Листает глоссарий — меняет аудио через edit_message_media."""
    from telegram import InputMediaAudio

    # После последнего слова — удаляем аудио и показываем меню
    if index >= len(GLOSSARY):
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard()
        )
        return

    term = GLOSSARY[index]
    caption = f"📖 {index + 1} из {len(GLOSSARY)}\n\nEN: {term['term']}\nRU: {term['ru']}"

    try:
        context.bot.edit_message_media(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            media=InputMediaAudio(media=term["file_id"], caption=caption),
            reply_markup=glossary_keyboard(index)
        )
    except Exception:
        # Если edit не сработал — удаляем и отправляем заново
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_audio(
            chat_id=query.message.chat_id,
            audio=term["file_id"],
            caption=caption,
            reply_markup=glossary_keyboard(index)
        )


# ── ТЕСТ ──

def strip_letter(opt_text):
    if len(opt_text) >= 3 and opt_text[1] == ")":
        return opt_text[3:].strip()
    return opt_text.strip()


def build_question_keyboard(state):
    lang = state["lang"]
    lang_btn = "Изменить вопрос на EN" if lang == "ru" else "Изменить вопрос на RU"
    q = QUESTIONS[state["order"][state["pos"]]]
    buttons = [
        [
            InlineKeyboardButton("A", callback_data="answer_0"),
            InlineKeyboardButton("B", callback_data="answer_1"),
            InlineKeyboardButton("C", callback_data="answer_2"),
            InlineKeyboardButton("D", callback_data="answer_3"),
        ],
        [InlineKeyboardButton(lang_btn, callback_data="toggle_lang")],
        [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu")],
    ]
    if q.get("audio_q"):
        buttons.insert(2, [InlineKeyboardButton("🔊 Слушать вопрос на английском", callback_data="play_q")])
    return InlineKeyboardMarkup(buttons)


def send_question(query, state, context):
    for msg_id in state.get("audio_msg_ids", []):
        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
        except Exception:
            pass
    state["audio_msg_ids"] = []

    q = QUESTIONS[state["order"][state["pos"]]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    options_text = "\n".join(options)
    full_text = f"❓ Вопрос {q['num']} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
    keyboard = build_question_keyboard(state)

    try:
        query.edit_message_text(full_text, reply_markup=keyboard)
    except Exception:
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=full_text,
            reply_markup=keyboard
        )


def send_question_no_delete(query, state, context):
    q = QUESTIONS[state["order"][state["pos"]]]
    lang = state["lang"]
    question = q["ru_q"] if lang == "ru" else q["en_q"]
    options = q["ru_options"] if lang == "ru" else q["en_options"]
    options_text = "\n".join(options)
    full_text = f"❓ Вопрос {q['num']} из {len(QUESTIONS)}\n\n{question}\n\n{options_text}"
    keyboard = build_question_keyboard(state)
    try:
        query.edit_message_text(full_text, reply_markup=keyboard)
    except Exception:
        pass


def get_file_id(update: Update, context: CallbackContext):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        update.message.reply_text(f"🖼 Photo file_id:\n<code>{file_id}</code>", parse_mode="HTML")
    elif update.message.audio:
        update.message.reply_text(f"🔊 {update.message.audio.file_name}:\n<code>{update.message.audio.file_id}</code>", parse_mode="HTML")
    elif update.message.document:
        update.message.reply_text(f"📎 {update.message.document.file_name}:\n<code>{update.message.document.file_id}</code>", parse_mode="HTML")


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if user_id not in user_state:
        order = list(range(len(QUESTIONS)))
        random.shuffle(order)
        user_state[user_id] = {"lang": "ru", "pos": 0, "g_index": 0, "order": order, "audio_msg_ids": []}

    state = user_state[user_id]
    if "audio_msg_ids" not in state:
        state["audio_msg_ids"] = []

    # ── Главное меню ──
    if query.data in ("main_menu", "main_menu_from_glo"):
        for msg_id in state.get("audio_msg_ids", []):
            try:
                context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
            except Exception:
                pass
        state["audio_msg_ids"] = []
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard()
        )

    # ── Тест ──
    elif query.data == "menu_quiz":
        order = list(range(len(QUESTIONS)))
        random.shuffle(order)
        state["order"] = order
        state["pos"] = 0
        send_question(query, state, context)

    elif query.data == "toggle_lang":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        send_question_no_delete(query, state, context)

    elif query.data == "play_q":
        q = QUESTIONS[state["order"][state["pos"]]]
        if q.get("audio_q"):
            msg = context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_q"])
            state["audio_msg_ids"].append(msg.message_id)

    elif query.data == "play_a":
        q = QUESTIONS[state["order"][state["pos"]]]
        if q.get("audio_a"):
            msg = context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_a"])
            state["audio_msg_ids"].append(msg.message_id)

    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["order"][state["pos"]]]
        lang = state["lang"]
        explain = q["ru_explain"] if lang == "ru" else q["en_explain"]
        correct_idx = q["correct"]
        options = q["ru_options"] if lang == "ru" else q["en_options"]
        correct_answer_text = strip_letter(options[correct_idx])

        if chosen == correct_idx:
            result = f"✅ Правильно! / Correct!\n\n📌 {correct_answer_text}\n\n{explain}"
        else:
            chosen_answer_text = strip_letter(options[chosen])
            result = (
                f"❌ Неверно! / Wrong!\n\n"
                f"Ваш ответ: {chosen_answer_text}\n"
                f"Правильный ответ: {correct_answer_text}\n\n"
                f"{explain}"
            )

        lang_btn = "Изменить вопрос на EN" if lang == "ru" else "Изменить вопрос на RU"
        buttons = [
            [
                InlineKeyboardButton("⬅️ Вернуться к вопросу", callback_data="back_to_question"),
                InlineKeyboardButton("➡️ Следующий / Next", callback_data="next_question"),
            ],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("🔊 Слушать ответ на английском", callback_data="play_a")])
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "back_to_question":
        send_question(query, state, context)

    elif query.data == "toggle_lang_answer":
        state["lang"] = "en" if state["lang"] == "ru" else "ru"
        q = QUESTIONS[state["order"][state["pos"]]]
        lang = state["lang"]
        explain = q["ru_explain"] if lang == "ru" else q["en_explain"]
        correct_idx = q["correct"]
        options = q["ru_options"] if lang == "ru" else q["en_options"]
        correct_answer_text = strip_letter(options[correct_idx])
        lang_btn = "Изменить вопрос на EN" if lang == "ru" else "Изменить вопрос на RU"
        result = f"💡 Правильный ответ: {correct_answer_text}\n\n{explain}"
        buttons = [
            [
                InlineKeyboardButton("⬅️ Вернуться к вопросу", callback_data="back_to_question"),
                InlineKeyboardButton("➡️ Следующий / Next", callback_data="next_question"),
            ],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("🔊 Слушать ответ на английском", callback_data="play_a")])
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "next_question":
        state["pos"] = (state["pos"] + 1) % len(QUESTIONS)
        send_question(query, state, context)

    # ── Глоссарий ──
    elif query.data == "menu_glossary":
        state["g_index"] = 0
        send_glossary_first(query.message.chat_id, context, old_msg_id=query.message.message_id)

    elif query.data.startswith("glo_"):
        index = int(query.data[4:])
        state["g_index"] = index
        update_glossary(query, context, index)

    # ── Аудирование ──
    elif query.data == "menu_drive":
        query.edit_message_text("🔊👂 Режим аудирования в разработке / Listening mode coming soon! 🚗 🏋️")


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
