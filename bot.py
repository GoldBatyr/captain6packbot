import logging
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

import os
TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

GLOSSARY = [
    {"term": "Port", "ru": "Левый борт", "file_id": "CQACAgIAAxkBAAIDpmnd33oq7vcbl3C-HGPr_Y6J2b1lAAIclAACwGnxSlm-Tt506gAB5jsE"},
    {"term": "Starboard", "ru": "Правый борт", "file_id": "CQACAgIAAxkBAAIDomnd33qbRs51tSAVvE0nryvGzWbiAAIYlAACwGnxSl0Q_m9ht5HwOwQ"},
    {"term": "Underway", "ru": "На ходу", "file_id": "CQACAgIAAxkBAAIDp2nd33p35ayaxoqPNzwJYN641FA0AAIdlAACwGnxSh9PEQJydsOFOwQ"},
    {"term": "Overtaking", "ru": "Обгон", "file_id": "CQACAgIAAxkBAAIDqGnd33oW1nO6ZBHubCbuKyxT_UH0AAIelAACwGnxSsBO4PBX4-ieOwQ"},
    {"term": "Stand-on vessel", "ru": "Привилегированное судно", "file_id": "CQACAgIAAxkBAAIDo2nd33pzNbV5R2gB0i-p2r-Y7YobAAIZlAACwGnxSnvglY2QQHKVOwQ"},
    {"term": "Give-way vessel", "ru": "Уступающее судно", "file_id": "CQACAgIAAxkBAAIDpGnd33pmRKGYLIMxhkpqbMaEEHFuAAIalAACwGnxSjVVyCDZokm5OwQ"},
    {"term": "Rules of the Road", "ru": "Правила плавания", "file_id": "CQACAgIAAxkBAAIDpWnd33on0t1CyfrTMrJpL0DfoRa0AAIblAACwGnxSj3l3wm9tbZoOwQ"},
]

QUESTIONS = [
    {
        "num": 1,
        "topic": "sound_signals",
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
        "topic": "sound_signals",
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
        "topic": "sound_signals",
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
        "topic": "sound_signals",
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
        "topic": "sound_signals",
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
        "topic": "sound_signals",
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
        "topic": "sound_signals",
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
        "topic": "lights_shapes",
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
        "topic": "lights_shapes",
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
        "topic": "sound_signals",
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
        "topic": "definitions",
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel is in sight of another vessel when:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно находится в зоне видимости другого судна, когда:",
        "en_options": ["A) She can be observed by radar", "B) She can be observed visually from the other vessel", "C) She can be plotted on radar well enough to determine her heading", "D) Her fog signal can be heard"],
        "ru_options": ["A) Оно наблюдается по радару", "B) Оно наблюдается визуально с другого судна", "C) Его курс определяется по радару", "D) Слышен его туманный сигнал"],
        "correct": 1,
        "en_explain": "Rule 3(k): a vessel is 'in sight' only when she can be observed visually. Radar contact alone does not count.",
        "ru_explain": "Правило 3(k): судно находится в зоне видимости только при визуальном наблюдении. Радар не считается.",
        "audio_q": "CQACAgIAAxkBAAIB7WnZ1G1i2hj120s5wCZuEkbia5MZAAI1oQACZJzJSvgkqv6OvIOSOwQ",
        "audio_a": "CQACAgIAAxkBAAIB72nZ1IQm2ayNiq9oizhUFt91Tp2SAAI2oQACZJzJSoJn6SnHcj5eOwQ",
    },
    {
        "num": 12,
        "topic": "distress",
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
        "topic": "steering_rules",
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
        "topic": "lights_shapes",
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
        "topic": "steering_rules",
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
        "topic": "lights_shapes",
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
        "topic": "lights_shapes",
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
        "topic": "visibility",
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
        "topic": "lights_shapes",
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
        "topic": "lights_shapes",
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
    # ── НОВЫЕ ВОПРОСЫ 21-40 ──
    {
        "num": 21,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. A 200-meter vessel restricted in her ability to maneuver, at anchor, will sound a fog signal of:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно длиной 200 метров, ограниченное в возможности маневрировать, на якоре, подаёт туманный сигнал:",
        "en_options": ["A) A 5 second ringing of a bell forward and a 5 second sounding of a gong aft at intervals of 1 minute", "B) One prolonged followed by two short blasts every 2 minutes", "C) One prolonged followed by three short blasts every minute", "D) One prolonged followed by three short blasts every 2 minutes"],
        "ru_options": ["A) Звонок 5 секунд носовой и гонг 5 секунд кормовой с интервалом 1 минута", "B) Один продолжительный и два коротких каждые 2 минуты", "C) Один продолжительный и три коротких каждую минуту", "D) Один продолжительный и три коротких каждые 2 минуты"],
        "correct": 1,
        "en_explain": "Rule 35: a vessel restricted in ability to maneuver at anchor sounds one prolonged + two short blasts every 2 minutes — same as when underway.",
        "ru_explain": "Правило 35: судно, ограниченное в манёвре и стоящее на якоре, подаёт один продолжительный + два коротких каждые 2 минуты — как и на ходу.",
        "audio_q": "CQACAgIAAxkBAAID6mnfHX4Nypy8Fkvm6oeGjpYdE5FdAAIekAACWUf5SkCxHj5hH6GAOwQ",
        "audio_a": "CQACAgIAAxkBAAID7GnfHZidKnAMk-OStXJofyK8tiGbAAIfkAACWUf5SuxLrscxRBmNOwQ",
    },
    {
        "num": 22,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. If your vessel is underway in fog and you hear one prolonged and three short blasts, this indicates a:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Ваше судно на ходу в тумане, вы слышите один продолжительный и три коротких сигнала. Это:",
        "en_options": ["A) Vessel not under command", "B) Sailing vessel", "C) Vessel in distress", "D) Vessel being towed"],
        "ru_options": ["A) Судно, лишённое управления", "B) Парусное судно", "C) Судно, терпящее бедствие", "D) Буксируемое судно"],
        "correct": 3,
        "en_explain": "Rule 35: one prolonged + three short blasts = vessel being towed (or last vessel in a tow).",
        "ru_explain": "Правило 35: один продолжительный + три коротких = буксируемое судно (или последнее судно в составе буксира).",
        "audio_q": "CQACAgIAAxkBAAID7mnfHbdNeTpGF4ytg8PqD2KOsF3SAAIhkAACWUf5SkRWlAxbrEAcOwQ",
        "audio_a": "CQACAgIAAxkBAAID8GnfHdQOd0FOIhEfiAyplwRFCRCPAAIikAACWUf5SurBQxEPwJDWOwQ",
    },
    {
        "num": 23,
        "topic": "distress",
        "en_q": "BOTH INTERNATIONAL & INLAND. An orange flag showing a black circle and square is a:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Оранжевый флаг с чёрным кругом и квадратом — это:",
        "en_options": ["A) Signal indicating a course change", "B) Distress signal", "C) Signal of asking to communicate with another vessel", "D) Signal indicating danger"],
        "ru_options": ["A) Сигнал изменения курса", "B) Сигнал бедствия", "C) Сигнал запроса связи с другим судном", "D) Сигнал опасности"],
        "correct": 1,
        "en_explain": "Rule 37 / Annex IV: an orange flag with a black circle and square is an official distress signal.",
        "ru_explain": "Правило 37 / Приложение IV: оранжевый флаг с чёрным кругом и квадратом — официальный сигнал бедствия.",
        "audio_q": "CQACAgIAAxkBAAID9mnfHlvH2QW2ZMdDG7jyosCIETt5AAInkAACWUf5SueUe66DxOftOwQ",
        "audio_a": "CQACAgIAAxkBAAID-GnfHmyX0NcybiXsDJQHWAyJgo_IAAIokAACWUf5Sj5ridY5cm6QOwQ",
    },
    {
        "num": 24,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. A partially submerged object towed by a vessel must show during the day:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Частично погружённый буксируемый объект днём должен показывать:",
        "en_options": ["A) One diamond shape when the length of the tow is 200 meters or less", "B) One diamond shape ONLY when the length of the tow exceeds 200 meters in length", "C) One black ball", "D) One black ball only when the length of the tow exceeds 200 meters in length"],
        "ru_options": ["A) Один ромб когда длина буксира 200 метров или менее", "B) Один ромб только когда длина буксира превышает 200 метров", "C) Один чёрный шар", "D) Один чёрный шар только когда длина буксира превышает 200 метров"],
        "correct": 0,
        "en_explain": "Rule 24: one diamond is required for a tow of 200m or less; additional diamonds are added above 200m. Black balls are for anchored vessels.",
        "ru_explain": "Правило 24: один ромб обязателен при длине буксира до 200 м, дополнительные добавляются при превышении 200 м. Чёрные шары — для якорных судов.",
        "audio_q": "CQACAgIAAxkBAAID-mnfHoLM-5py4M2rSieBG_Iq3h34AAIpkAACWUf5SgtSJpf_PaZyOwQ",
        "audio_a": "CQACAgIAAxkBAAID_GnfHpV4vak6iGaA0B10fzqKAwFLAAIqkAACWUf5SmbQGNT6rAjDOwQ",
    },
    {
        "num": 25,
        "topic": "narrow_channels",
        "en_q": "BOTH INTERNATIONAL & INLAND. You are crossing a narrow channel in a small motorboat. You sight a tankship off your port bow coming up the channel. Which statement is TRUE?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Вы пересекаете узкий канал на небольшом моторном катере. Слева по носу — танкер, идущий по каналу. Какое утверждение верно?",
        "en_options": ["A) You are the stand-on vessel because the tankship is to port.", "B) You cannot impede the safe passage of the tankship.", "C) The tankship has the right of way because it is to port of your vessel.", "D) The tankship has the right of way because it is the larger of the two vessels."],
        "ru_options": ["A) Вы привилегированное судно, так как танкер слева.", "B) Вы не должны создавать помех безопасному проходу танкера.", "C) Танкер имеет преимущество, так как он слева от вас.", "D) Танкер имеет преимущество, так как он крупнее."],
        "correct": 1,
        "en_explain": "Rule 9: a vessel crossing a narrow channel shall not impede vessels which can only navigate safely within the channel.",
        "ru_explain": "Правило 9: судно, пересекающее узкий канал, не должно создавать помех судам, которые могут безопасно следовать только в пределах этого канала.",
        "audio_q": "CQACAgIAAxkBAAID_mnfHrT3ISWEcQ4Hnf4ohM9NmRLRAAIrkAACWUf5ShWnw8aud2vqOwQ",
        "audio_a": "CQACAgIAAxkBAAIEAAFp3x7QXQMnroPOewiPI84AAWhRQVQAAiyQAAJZR_lKBVyvtl4sfmY7BA",
    },
    {
        "num": 26,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. In DIAGRAM 8, vessel A and vessel B (which is pushing ahead) are meeting head and head as shown. How must the vessels pass?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. На ДИАГРАММЕ 8 судно A и судно B (толкач) встречаются нос к носу. Как должны разойтись суда?",
        "en_options": ["A) Vessel A must alter course while vessel B continues on its present course.", "B) The vessels should determine which will alter course by exchanging whistle signals.", "C) Both vessels should alter course to port and pass starboard to starboard.", "D) Both vessels should alter course to starboard and pass port to port."],
        "ru_options": ["A) Судно A должно изменить курс, судно B продолжает прежний курс.", "B) Суда должны обменяться звуковыми сигналами для определения манёвра.", "C) Оба судна должны изменить курс влево и разойтись правыми бортами.", "D) Оба судна должны изменить курс вправо и разойтись левыми бортами."],
        "correct": 3,
        "en_explain": "Rule 14: when vessels meet head-on, both vessels shall alter course to starboard and pass port to port.",
        "ru_explain": "Правило 14: при встрече нос к носу оба судна берут вправо и расходятся левыми бортами.",
        "audio_q": "CQACAgIAAxkBAAIEAmnfHulW_fMZlOiITPRIz24AAQamHQACLZAAAllH-UooZyvv_TnlFDsE",
        "audio_a": "CQACAgIAAxkBAAIEBGnfHvbDWrcAASYdGGP-M4oHjPdVSAACLpAAAllH-UqYovmH3d3QpDsE",
        "image": "BQACAgIAAxkBAAIFhmnz-WMmYOabtYCaufwnCqGvagr3AALjowACQAagS6HxNs8OOnsuOwQ",
    },
    {
        "num": 27,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. Each prolonged blast on whistle signals used by a power-driven vessel in fog, whether making way or underway but not making way, is:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Каждый продолжительный сигнал свистка моторного судна в тумане, независимо от того идёт ли оно вперёд или стоит на месте, длится:",
        "en_options": ["A) About one second", "B) Two to four seconds", "C) Four to six seconds", "D) Eight to ten seconds"],
        "ru_options": ["A) Около одной секунды", "B) Два-четыре секунды", "C) Четыре-шесть секунд", "D) Восемь-десять секунд"],
        "correct": 2,
        "en_explain": "Rule 32: a prolonged blast is a blast of from 4 to 6 seconds duration.",
        "ru_explain": "Правило 32: продолжительный сигнал — это сигнал длительностью от 4 до 6 секунд.",
        "audio_q": "CQACAgIAAxkBAAIEBmnfHzU1r2fShM2xuNUWiTDc3ZHfAAIwkAACWUf5SumApywhicH3OwQ",
        "audio_a": "CQACAgIAAxkBAAIECGnfH0KfndzkfHSZNwXlREflvZ2WAAIxkAACWUf5SlkkQkv62XoIOwQ",
    },
    {
        "num": 28,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. The rules state that vessels may depart from the requirements of the Rules when:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Правила допускают отступление от своих требований когда:",
        "en_options": ["A) There are no other vessels around", "B) Operating in a narrow channel", "C) The Master enters it in the ship's log", "D) Necessary to avoid immediate danger"],
        "ru_options": ["A) Вокруг нет других судов", "B) Судно следует в узком канале", "C) Капитан делает запись в судовом журнале", "D) Это необходимо для предотвращения непосредственной опасности"],
        "correct": 3,
        "en_explain": "Rule 2(b): nothing in the Rules shall exonerate a vessel from the consequences of neglect, except to avoid immediate danger.",
        "ru_explain": "Правило 2(b): ничто в Правилах не освобождает судно от ответственности за отступление от Правил, если это не вызвано необходимостью избежать непосредственной опасности.",
        "audio_q": "CQACAgIAAxkBAAIECmnfH2RZYrY_aiZlCEvE1r7tWW-PAAI0kAACWUf5Smwi48zIryMPOwQ",
        "audio_a": "CQACAgIAAxkBAAIEDGnfH387vDRFY-qL7Jf_RKPY2Py3AAI2kAACWUf5SmIiFX0HDrHUOwQ",
    },
    {
        "num": 29,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel 50 meters in length at anchor must sound which fog signal?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно длиной 50 метров на якоре должно подавать какой туманный сигнал?",
        "en_options": ["A) 5-second ringing of a bell every minute", "B) 5-second ringing of a bell every two minutes", "C) 5-second sounding of a gong every minute", "D) 5-second sounding of both a bell and gong every two minutes"],
        "ru_options": ["A) Звонок в колокол 5 секунд каждую минуту", "B) Звонок в колокол 5 секунд каждые две минуты", "C) Удар в гонг 5 секунд каждую минуту", "D) Звонок в колокол и гонг 5 секунд каждые две минуты"],
        "correct": 0,
        "en_explain": "Rule 35(g): a vessel at anchor under 100 meters rings the bell rapidly for 5 seconds at intervals of not more than one minute.",
        "ru_explain": "Правило 35(g): судно на якоре длиной менее 100 метров звонит в колокол 5 секунд каждую минуту.",
        "audio_q": "CQACAgIAAxkBAAIEDmnfH5BhFSPBVamW_sN2sbPEd6mLAAI3kAACWUf5Sk_piyxuJll4OwQ",
        "audio_a": "CQACAgIAAxkBAAIEEGnfH5-bOGZ_LxljomHMKbtX_cmIAAI4kAACWUf5SsD1CW8BeLawOwQ",
    },
    {
        "num": 30,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. What is the minimum sound signaling equipment required aboard a vessel 10 meters in length?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Какое минимальное звуковое сигнальное оборудование требуется на судне длиной 10 метров?",
        "en_options": ["A) Any means of making an efficient sound signal", "B) A bell only", "C) A whistle only", "D) A bell and a whistle"],
        "ru_options": ["A) Любое средство подачи эффективного звукового сигнала", "B) Только колокол", "C) Только свисток", "D) Колокол и свисток"],
        "correct": 0,
        "en_explain": "Rule 33: vessels less than 12 meters are not required to carry a whistle or bell, but must have some means of making an efficient sound signal.",
        "ru_explain": "Правило 33: суда длиной менее 12 метров не обязаны иметь свисток или колокол, но должны иметь какое-либо средство подачи эффективного звукового сигнала.",
        "audio_q": "CQACAgIAAxkBAAIEEmnfH8AMxVERxOF9v4HW7ULFrfZ7AAI5kAACWUf5Sp9EjujV1Hx3OwQ",
        "audio_a": "CQACAgIAAxkBAAIEFGnfH_FeAAGxzvoB8KB7-7Zn3oH1qQACPpAAAllH-Uob1516ViIMxjsE",
    },
    {
        "num": 31,
        "topic": "definitions",
        "en_q": "INTERNATIONAL ONLY. The International Rules of the Road apply:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Международные правила предупреждения столкновений судов применяются:",
        "en_options": ["A) To all waters which are not inland waters", "B) Only to waters outside the territorial waters of the United States", "C) Only to waters where foreign vessels travel", "D) Upon the high seas and connecting waters navigable by seagoing vessels"],
        "ru_options": ["A) На всех водах, которые не являются внутренними", "B) Только за пределами территориальных вод США", "C) Только на водах где ходят иностранные суда", "D) В открытом море и соединённых с ним водах, доступных для морских судов"],
        "correct": 3,
        "en_explain": "COLREGS Rule 1: these Rules shall apply to all vessels upon the high seas and in all waters connected therewith navigable by seagoing vessels.",
        "ru_explain": "МППСС-72 Правило 1: Правила применяются в открытом море и соединённых с ним водах, по которым могут плавать морские суда.",
        "audio_q": "CQACAgIAAxkBAAIEFmnfIJfqT1g2cGom6LUjgp6TUEJCAAJDkAACWUf5Sh1hCoWYXbvMOwQ",
        "audio_a": "CQACAgIAAxkBAAIEGGnfILcDkzEzyLmvoXmDxlarP8DbAAJEkAACWUf5SgFHZgJf2NvxOwQ",
    },
    {
        "num": 32,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel engaged in fishing while at anchor shall sound a fog signal of:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно, занятое рыболовством и стоящее на якоре, подаёт туманный сигнал:",
        "en_options": ["A) One prolonged and three short blasts at one minute intervals", "B) A rapid ringing of the bell for five seconds at one minute intervals", "C) One prolonged and two short blasts at two minute intervals", "D) A sounding of the bell and gong at one minute intervals"],
        "ru_options": ["A) Один продолжительный и три коротких с интервалом одна минута", "B) Быстрый звон колокола 5 секунд с интервалом одна минута", "C) Один продолжительный и два коротких с интервалом две минуты", "D) Звонок колокола и гонга с интервалом одна минута"],
        "correct": 2,
        "en_explain": "Rule 35: a fishing vessel at anchor sounds the same signal as when underway fishing — one prolonged + two short every 2 minutes.",
        "ru_explain": "Правило 35: рыболовное судно на якоре подаёт тот же сигнал что и на ходу: один продолжительный + два коротких каждые 2 минуты.",
        "audio_q": "CQACAgIAAxkBAAIEGmnfINFjrXk2Pr3oW_G0G4uQ2ZhOAAJFkAACWUf5SpGV1l1ABL8vOwQ",
        "audio_a": "CQACAgIAAxkBAAIEHGnfIOeiCjgVhmVcz7nF9NzkXG2uAAJHkAACWUf5SooXSERdWzfnOwQ",
    },
    {
        "num": 33,
        "topic": "definitions",
        "en_q": "BOTH INTERNATIONAL & INLAND. What determines if a vessel is \"restricted in her ability to maneuver\"?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Что определяет статус судна «ограниченного в возможности маневрировать»?",
        "en_options": ["A) Whether or not all of the vessel's control equipment is in working order", "B) The vessel's draft in relation to the available depth of water", "C) Whether the vessel is operating in a narrow channel", "D) The nature of the vessel's work, limiting maneuverability required by the Rules"],
        "ru_options": ["A) Исправность всего навигационного оборудования судна", "B) Осадка судна относительно доступной глубины воды", "C) Следует ли судно в узком канале", "D) Характер выполняемых работ, ограничивающий манёвренность судна согласно Правилам"],
        "correct": 3,
        "en_explain": "Rule 3(g): a vessel restricted in ability to maneuver is one whose nature of work limits her ability to maneuver as required by the Rules.",
        "ru_explain": "Правило 3(g): судно, ограниченное в возможности маневрировать — это судно, которое по характеру своей работы не может маневрировать так, как требуют Правила.",
        "audio_q": "CQACAgIAAxkBAAIEHmnfIQjfSVi5D97XBxCx5VjHSChJAAJIkAACWUf5SklGkFuI5XP2OwQ",
        "audio_a": "CQACAgIAAxkBAAIEIGnfISAEwuM_oPiuZJ47WcSDt8bwAAJJkAACWUf5Sk-rRW02wYDnOwQ",
    },
    {
        "num": 34,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. The stern light shall be positioned such that it will show from dead astern to how many degrees on each side of the stern of the vessel?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Кормовой огонь должен быть расположен так, чтобы освещать дугу от прямо за кормой до скольких градусов с каждого борта?",
        "en_options": ["A) 135.0°", "B) 112.5°", "C) 67.5°", "D) 22.5°"],
        "ru_options": ["A) 135,0°", "B) 112,5°", "C) 67,5°", "D) 22,5°"],
        "correct": 2,
        "en_explain": "Rule 21: the sternlight is a white light showing over an arc of 135°, positioned to show 67.5° on each side from dead astern.",
        "ru_explain": "Правило 21: кормовой огонь — белый огонь, освещающий дугу 135° (по 67,5° с каждого борта от прямо за кормой).",
        "audio_q": "CQACAgIAAxkBAAIEImnfIT5PZ6fGZnbQfJNU6ud_vJHUAAJKkAACWUf5SlsfxkldwBjmOwQ",
        "audio_a": "CQACAgIAAxkBAAIEJGnfIUpzQo0jzRxWIrAMrEI_RGCfAAJLkAACWUf5SnPpu7ve5V78OwQ",
    },
    {
        "num": 35,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. If two sailing vessels are running free with the wind on the same side, which one must keep clear of the other?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Если два парусных судна идут при попутном ветре с ветром на одном борту, какое из них должно уступить дорогу?",
        "en_options": ["A) The one with the wind closest abeam", "B) The one to windward", "C) The one to leeward", "D) The one that sounds the first whistle signal"],
        "ru_options": ["A) То, у которого ветер ближе к траверзу", "B) То, которое находится на ветре", "C) То, которое находится под ветром", "D) То, которое первым подаёт звуковой сигнал"],
        "correct": 1,
        "en_explain": "Rule 12: when two sailing vessels have the wind on the same side, the vessel to windward shall keep out of the way of the vessel to leeward.",
        "ru_explain": "Правило 12: если два парусных судна имеют ветер на одном борту — судно на ветре уступает дорогу судну под ветром.",
        "audio_q": "CQACAgIAAxkBAAIEJmnfIV1euC19JAKFtabUdDXsYWiSAAJMkAACWUf5SkRZp58fSbHNOwQ",
        "audio_a": "CQACAgIAAxkBAAIEKGnfIXNEkcB19PwYLOAG2GXacW2tAAJNkAACWUf5SqiSTscWrcr2OwQ",
    },
    {
        "num": 36,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. Which statement is TRUE, according to the Rules?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Какое утверждение верно согласно Правилам?",
        "en_options": ["A) A vessel not under command shall keep out of the way of a vessel restricted in her ability to maneuver.", "B) A vessel not under command shall keep out of the way of a vessel engaged in fishing.", "C) A vessel engaged in fishing while underway shall, so far as possible, keep out of the way of a vessel restricted in her ability to maneuver.", "D) A vessel engaged in fishing shall keep out of the way of a sailing vessel."],
        "ru_options": ["A) Судно лишённое управления уступает дорогу судну ограниченному в манёвре.", "B) Судно лишённое управления уступает дорогу судну занятому рыболовством.", "C) Судно занятое рыболовством на ходу по возможности уступает дорогу судну ограниченному в манёвре.", "D) Судно занятое рыболовством уступает дорогу парусному судну."],
        "correct": 2,
        "en_explain": "Rule 18: hierarchy of vessels — a vessel restricted in ability to maneuver has priority over a fishing vessel. Fishing vessel gives way.",
        "ru_explain": "Правило 18: иерархия судов — судно ограниченное в манёвре имеет приоритет над судном занятым рыболовством. Рыболовное судно уступает дорогу.",
        "audio_q": "CQACAgIAAxkBAAIEKmnfIY-P4c_ulMldoG_9WLx8ZXEhAAJPkAACWUf5SpZqCya7jAs5OwQ",
        "audio_a": "CQACAgIAAxkBAAIELGnfIZ4I3hbIQbinOcgbDubHH5jRAAJQkAACWUf5SjTbZQ1O_1OwOwQ",
    },
    {
        "num": 37,
        "topic": "narrow_channels",
        "en_q": "INTERNATIONAL ONLY. Your vessel is crossing a narrow channel. A vessel to port is within the channel and crossing your course. She is showing a black cylinder. What is your responsibility?",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Ваше судно пересекает узкий канал. Судно слева находится в канале и пересекает ваш курс. Оно показывает чёрный цилиндр. Каковы ваши обязанности?",
        "en_options": ["A) Hold your course and speed.", "B) Sound the danger signal.", "C) Begin an exchange of passing signals.", "D) Do not cross the channel if you might impede the other vessel."],
        "ru_options": ["A) Держать курс и скорость.", "B) Подать сигнал опасности.", "C) Начать обмен сигналами расхождения.", "D) Не пересекать канал если вы можете создать помеху этому судну."],
        "correct": 3,
        "en_explain": "Rule 9: a vessel crossing a narrow channel shall not impede vessels navigating within the channel. Black cylinder = vessel constrained by draft.",
        "ru_explain": "Правило 9: судно пересекающее узкий канал не должно создавать помех судам следующим по каналу. Чёрный цилиндр = судно ограничено своей осадкой.",
        "audio_q": "CQACAgIAAxkBAAIELmnfIb5hVhfjAAHBDtNC7lKfcfvkbQACUZAAAllH-UrxtxZwOijGBTsE",
        "audio_a": "CQACAgIAAxkBAAIEMGnfIdnteTX5JonJxsN-4Yhy5QZTAAJSkAACWUf5ShStL8mYlwuhOwQ",
    },
    {
        "num": 38,
        "topic": "lights_shapes",
        "en_q": "INTERNATIONAL ONLY. Lighting requirements in inland waters are different from those for international waters for:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Требования к огням на внутренних водах отличаются от международных для:",
        "en_options": ["A) Barges being towed by pushing ahead", "B) Vessels restricted in their ability to maneuver", "C) Vessels towing astern", "D) Barges being towed astern"],
        "ru_options": ["A) Барж, толкаемых впереди", "B) Судов, ограниченных в возможности маневрировать", "C) Судов, буксирующих за кормой", "D) Барж, буксируемых за кормой"],
        "correct": 0,
        "en_explain": "US Inland Rules: barges being pushed ahead have special lighting requirements that differ from COLREGS.",
        "ru_explain": "Внутренние правила США: баржи толкаемые впереди имеют особые требования к огням, отличающиеся от МППСС-72.",
        "audio_q": "CQACAgIAAxkBAAIEMmnfIgGLn_FDQZv6CUTqE3x11vudAAJTkAACWUf5Sqv81RpIF2rZOwQ",
        "audio_a": "CQACAgIAAxkBAAIENGnfIhCJ-q1wxjo4zFR-pXoez-S3AAJUkAACWUf5SuCA3hRV6nW_OwQ",
    },
    {
        "num": 39,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. You have made your vessel up to a tow and are moving from a pier out into the main channel. If your engines are turning ahead, what whistle signal should you sound?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы сформировали буксир и отходите от причала в основной канал. Если машины работают вперёд, какой звуковой сигнал следует подать?",
        "en_options": ["A) One prolonged and two short blasts", "B) Three long blasts", "C) One prolonged blast", "D) Five or more short rapid blasts"],
        "ru_options": ["A) Один продолжительный и два коротких", "B) Три длинных", "C) Один продолжительный", "D) Пять и более коротких частых"],
        "correct": 2,
        "en_explain": "Inland Rules: a vessel departing a dock with engines going ahead sounds ONE prolonged blast (4-6 sec) to warn surrounding vessels.",
        "ru_explain": "Внутренние правила: судно отходящее от причала с машиной вперёд подаёт один продолжительный сигнал (4-6 сек) для предупреждения окружающих судов.",
        "audio_q": "CQACAgIAAxkBAAIENmnfIivkJ2LG59jUDhAHxVcvvm4AA1WQAAJZR_lKWRyIF8J0OO87BA",
        "audio_a": "CQACAgIAAxkBAAIEOGnfIjze6CUCt-x99WSue6OLdHDiAAJWkAACWUf5Sr1mZDT9QK5POwQ",
    },
    {
        "num": 40,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. You are approaching another vessel and will pass safely starboard to starboard without changing course. You should:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Вы сближаетесь с другим судном и безопасно разойдётесь правыми бортами без изменения курса. Вы должны:",
        "en_options": ["A) Hold course and sound no whistle signal", "B) Hold course and sound a two blast whistle signal", "C) Change course to starboard and sound one blast", "D) Hold course and sound one blast"],
        "ru_options": ["A) Держать курс и не подавать звуковых сигналов", "B) Держать курс и подать два коротких сигнала", "C) Изменить курс вправо и подать один короткий", "D) Держать курс и подать один короткий"],
        "correct": 0,
        "en_explain": "COLREGS Rule 34: maneuvering signals are only sounded when altering course. If no course change is needed and passing is safe, no signal is required.",
        "ru_explain": "МППСС-72 Правило 34: звуковые манёвренные сигналы подаются при изменении курса. Если курс не меняется и расхождение безопасное — сигналы не требуются.",
        "audio_q": "CQACAgIAAxkBAAIEOmnfIlHZ-1O7s0hjJy6LFiUdhWF0AAJXkAACWUf5SqEsjvB0ghI7OwQ",
        "audio_a": "CQACAgIAAxkBAAIEPGnfImCLHruBnqmflTAq6C-rd2YTAAJYkAACWUf5SnOCQlvK75V_OwQ",
    },
    # ── НОВЫЕ ВОПРОСЫ 41-60 ──
    {
        "num": 41,
        "topic": "narrow_channels",
        "en_q": "INLAND ONLY. Which is true of a downbound vessel, when meeting an upbound vessel on the Western Rivers?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Что верно в отношении судна идущего вниз по течению при встрече с судном идущим вверх на Западных реках?",
        "en_options": ["A) She has the right of way only if she is a power-driven vessel.", "B) She has the right of way only if she has a tow.", "C) She does not have the right of way, since the other vessel is not crossing the river.", "D) She must wait for a whistle signal from the upbound vessel."],
        "ru_options": ["A) Оно имеет преимущество только если является моторным судном.", "B) Оно имеет преимущество только если имеет буксир.", "C) Оно не имеет преимущества, так как другое судно не пересекает реку.", "D) Оно должно ждать звукового сигнала от судна идущего вверх."],
        "correct": 0,
        "en_explain": "On Western Rivers: a downbound vessel always has the right of way over an upbound vessel due to reduced maneuverability with the current.",
        "ru_explain": "На Западных реках: судно идущее вниз по течению всегда имеет преимущество перед судном идущим вверх, так как у него меньше манёвренности при управлении течением.",
        "audio_q": "CQACAgIAAxkBAAIEW2noLHVRmPjw6MWFPUU2tRFZFmgKAAL8mwACt59BS3iyfDmN-WyTOwQ",
        "audio_a": "CQACAgIAAxkBAAIEXWnoLKehMT8tjYCTFW7Cc5fUgpliAAL9mwACt59BS5JEOfjsXygcOwQ",
    },
    {
        "num": 42,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. The lights illustrated in DIAGRAM 75 are those of a:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Огни изображённые на ДИАГРАММЕ 75 принадлежат:",
        "en_options": ["A) Pipeline", "B) Vessel towing by pushing ahead", "C) Vessel being towed astern", "D) Vessel underway and dredging"],
        "ru_options": ["A) Трубопроводу", "B) Судну буксирующему толканием впереди", "C) Судну буксируемому за кормой", "D) Судну на ходу занятому дноуглубительными работами"],
        "correct": 1,
        "en_explain": "US Inland Rules: a vessel towing by pushing ahead shows a special combination of lights that differs from COLREGS.",
        "ru_explain": "Внутренние правила США: судно толкающее баржу впереди показывает специальную комбинацию огней отличную от МППСС-72.",
        "audio_q": "CQACAgIAAxkBAAIEX2noLNX6sMxkhGTSytyjRX-b_vZrAAL-mwACt59BS9hRwn66_D5MOwQ",
        "audio_a": "CQACAgIAAxkBAAIEYWnoLV3gAZm2afRCOKubI4DHXVA6AAL_mwACt59BS3cmr6i3B1L3OwQ",
        "image": "BQACAgIAAxkBAAIFfGnz9_8s2CNc8nYvF35yBf7E4CfbAALdowACQAagS8yYZPkfjmHzOwQ",
    },
    {
        "num": 43,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. While underway, you sight the lights illustrated with the yellow lights flashing. You should (see DIAGRAM 81):",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. На ходу вы видите огни изображённые на диаграмме с мигающими жёлтыми огнями. Вы должны (см. ДИАГРАММУ 81):",
        "en_options": ["A) Wait until the vessel ahead crosses your bow", "B) Stop until the red lights turn green", "C) Proceed leaving all the lights on your starboard side", "D) Pass between the two sets of vertical red lights"],
        "ru_options": ["A) Ждать пока судно впереди пересечёт ваш курс", "B) Остановиться пока красные огни не станут зелёными", "C) Следовать оставляя все огни по правому борту", "D) Пройти между двумя группами вертикальных красных огней"],
        "correct": 3,
        "en_explain": "Flashing yellow lights on a dredge indicate the safe passage channel — you must pass between the two groups of red lights.",
        "ru_explain": "Мигающие жёлтые огни на дноуглубительном снаряде указывают безопасный проход — нужно пройти между двумя группами красных огней.",
        "audio_q": "CQACAgIAAxkBAAIEY2noLZ03er-55J7qQJbUielWx0c9AAOcAAK3n0FLKj-HQTLhNnY7BA",
        "audio_a": "CQACAgIAAxkBAAIEZWnoLbhcaX0vjTTbdvCEdx0UB330AAIBnAACt59BS0YXB2fMjSG1OwQ",
        "image": "BQACAgIAAxkBAAIFfmnz-BT1_2ulNuptUbFglfi-BUDGAALeowACQAagS0v9M0ST1UyCOwQ",
    },
    {
        "num": 44,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. A law enforcement boat may display a:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Катер правоохранительных органов может показывать:",
        "en_options": ["A) Blue flag", "B) Flashing blue light", "C) Flashing red light", "D) Flashing amber light"],
        "ru_options": ["A) Синий флаг", "B) Мигающий синий огонь", "C) Мигающий красный огонь", "D) Мигающий янтарный огонь"],
        "correct": 1,
        "en_explain": "US Inland Rules: law enforcement vessels use a flashing blue light as an identifying signal.",
        "ru_explain": "Внутренние правила США: суда правоохранительных органов используют мигающий синий огонь как опознавательный сигнал.",
        "audio_q": "CQACAgIAAxkBAAIEZ2noLcwwx4R1CWLaNGiyviNIY6iLAAICnAACt59BSzhla1q5C_ShOwQ",
        "audio_a": "CQACAgIAAxkBAAIEaWnoLd4o4EImNMpj-o5LphwDcXtWAAIDnAACt59BS4NsikB5N4LxOwQ",
    },
    {
        "num": 45,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. Which of the following is used to indicate the presence of a partly submerged object being towed?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Что из перечисленного используется для обозначения частично погружённого буксируемого объекта?",
        "en_options": ["A) A diamond shape on the towed object", "B) An all-round light at each end of the towed object", "C) A searchlight from the towing vessel in the direction of the tow", "D) All of the above"],
        "ru_options": ["A) Ромб на буксируемом объекте", "B) Круговой огонь на каждом конце буксируемого объекта", "C) Прожектор с буксирующего судна в направлении буксира", "D) Всё вышеперечисленное"],
        "correct": 3,
        "en_explain": "Inland Rules: any of the listed methods or their combination is permitted to indicate a partly submerged towed object.",
        "ru_explain": "Внутренние правила: для обозначения частично погружённого объекта допускается любой из перечисленных способов или их комбинация.",
        "audio_q": "CQACAgIAAxkBAAIEa2noLhpmCII-eZEaqvVFAkaEqSXEAAIEnAACt59BS7uG97-fTFHfOwQ",
        "audio_a": "CQACAgIAAxkBAAIEbWnoLinA34gVU3wBTGQVhnkiiRmRAAIFnAACt59BS7tzB8A7uHW7OwQ",
    },
    {
        "num": 46,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. What is the required whistle signal for a vessel leaving a dock or berth?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Какой звуковой сигнал обязано подать судно при отходе от причала или берта?",
        "en_options": ["A) One short blast", "B) One prolonged blast", "C) Two short blasts", "D) One long blast"],
        "ru_options": ["A) Один короткий сигнал", "B) Один продолжительный сигнал", "C) Два коротких сигнала", "D) Один длинный сигнал"],
        "correct": 1,
        "en_explain": "Inland Rules: a vessel leaving a dock sounds ONE prolonged blast (4-6 sec) to warn surrounding vessels.",
        "ru_explain": "Внутренние правила: судно отходящее от причала подаёт один продолжительный сигнал (4-6 сек) для предупреждения окружающих судов.",
        "audio_q": "CQACAgIAAxkBAAIEb2noLmesJ2y4A-Idq29lfOPkB04PAAIGnAACt59BS9cUHfy8nSxPOwQ",
        "audio_a": "CQACAgIAAxkBAAIEcWnoLouFmVjNKSHGJbC282ybROtZAAIHnAACt59BS_-wRh2sSAiXOwQ",
    },
    {
        "num": 47,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. Vessels 'A' and 'B' are passing in a narrow channel as shown in DIAGRAM 29. Which of the following is true concerning whistle signals between vessels?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Суда A и B расходятся в узком канале как показано на ДИАГРАММЕ 29. Что верно в отношении звуковых сигналов?",
        "en_options": ["A) Both vessels should sound two short blasts.", "B) Both vessels should sound one short blast.", "C) Vessel 'A' should sound one short blast and vessel 'B' should sound two short blasts.", "D) Neither vessel should sound any signal as no course change is necessary."],
        "ru_options": ["A) Оба судна должны подать два коротких сигнала.", "B) Оба судна должны подать один короткий сигнал.", "C) Судно A подаёт один короткий, судно B подаёт два коротких.", "D) Ни одно судно не подаёт сигналов так как изменение курса не требуется."],
        "correct": 0,
        "en_explain": "Inland Rules: vessels passing port to port exchange TWO short blasts.",
        "ru_explain": "Внутренние правила: суда расходящиеся левыми бортами обмениваются двумя короткими сигналами.",
        "audio_q": "CQACAgIAAxkBAAIEc2noLrOC_DAibR01T4wtNB6yIetqAAIInAACt59BS2T8kMG_i23aOwQ",
        "audio_a": "CQACAgIAAxkBAAIEdWnoLsQqr_o2ZTyrReKDYFB3mThXAAIJnAACt59BS6VyIP9qEzY-OwQ",
        "image": "BQACAgIAAxkBAAIFgGnz-C1ID_ifm_Bq_4j51YP1TtLWAALfowACQAagS3OwRCzrU61dOwQ",
    },
    {
        "num": 48,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. Your vessel is meeting another vessel head to head. To comply with the rules, you should:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Ваше судно встречается с другим судном нос к носу. Согласно правилам вы должны:",
        "en_options": ["A) Exchange one short blast, alter course to the left and pass starboard to starboard", "B) Exchange one short blast, alter course to the right and pass port to port", "C) Exchange two short blasts, alter course to the left and pass starboard to starboard", "D) Exchange two short blasts, alter course to the right and pass port to port"],
        "ru_options": ["A) Обменяться одним коротким, изменить курс влево и разойтись правыми бортами", "B) Обменяться одним коротким, изменить курс вправо и разойтись левыми бортами", "C) Обменяться двумя короткими, изменить курс влево и разойтись правыми бортами", "D) Обменяться двумя короткими, изменить курс вправо и разойтись левыми бортами"],
        "correct": 1,
        "en_explain": "Rule 34: when meeting head-on — one short blast, alter course to starboard, pass port to port.",
        "ru_explain": "Правило 34: при встрече нос к носу — один короткий сигнал, курс вправо, расходятся левыми бортами.",
        "audio_q": "CQACAgIAAxkBAAIEd2noLtql7DhqKf_kprdC7IrVY7bJAAIKnAACt59BS_sbO7rjKxa8OwQ",
        "audio_a": "CQACAgIAAxkBAAIEeWnoLumddwIOnIWjAAEy88X0qOq0BgACC5wAArefQUvIBpOl7XA2gDsE",
    },
    {
        "num": 49,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. A vessel intends to overtake another vessel on the overtaken vessel's port side. What whistle signal should be sounded in order to state this intention?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Судно намерено обогнать другое судно с левого борта обгоняемого. Какой сигнал следует подать?",
        "en_options": ["A) 1 short blast", "B) 2 short blasts", "C) 2 prolonged and 1 short blast", "D) 2 prolonged and 2 short blasts"],
        "ru_options": ["A) 1 короткий сигнал", "B) 2 коротких сигнала", "C) 2 продолжительных и 1 короткий", "D) 2 продолжительных и 2 коротких"],
        "correct": 1,
        "en_explain": "Rule 34: overtaking on PORT side = TWO short blasts. Overtaken vessel responds with same signal to confirm.",
        "ru_explain": "Правило 34: обгон с левого (PORT) борта = два коротких сигнала. Обгоняемое судно отвечает тем же сигналом для подтверждения.",
        "audio_q": "CQACAgIAAxkBAAIEe2noLxb01g2po3mB_Bqe6bwrwAZ5AAIMnAACt59BS73e-oNWle-lOwQ",
        "audio_a": "CQACAgIAAxkBAAIEfWnoLyH3VhA_O2Zsn3jA6aikKE9dAAINnAACt59BSwABYuDe8UScBzsE",
    },
    {
        "num": 50,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. At night a barge moored in a slip used primarily for mooring purposes shall:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Ночью баржа ошвартованная в слипе используемом преимущественно для швартовки:",
        "en_options": ["A) Not be required to be lighted", "B) Show a white light at each corner", "C) Show a red light at the bow and stern", "D) Show a flashing yellow light at each corner"],
        "ru_options": ["A) Не обязана иметь огни", "B) Показывает белый огонь на каждом углу", "C) Показывает красный огонь на носу и корме", "D) Показывает мигающий жёлтый огонь на каждом углу"],
        "correct": 0,
        "en_explain": "US Inland Rules: a barge moored in a designated mooring area is exempt from lighting requirements.",
        "ru_explain": "Внутренние правила США: баржа ошвартованная в специально отведённом месте для швартовки освобождается от требования выставлять огни.",
        "audio_q": "CQACAgIAAxkBAAIEf2noLzjnsJEr1rRk8oxee8INQCVmAAIOnAACt59BS0W6KDOO4r-QOwQ",
        "audio_a": "CQACAgIAAxkBAAIEgWnoL1avWD0yFPyaYykdiAeuiXAxAAIQnAACt59BS6f8kGrPKP72OwQ",
    },
    {
        "num": 51,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. Which statement is true concerning the light used for maneuvering signals?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Какое утверждение верно в отношении огня используемого для манёвренных сигналов?",
        "en_options": ["A) It must be synchronized with the whistle.", "B) It may be white or yellow.", "C) It must be an all-round light.", "D) All of the above."],
        "ru_options": ["A) Он должен быть синхронизирован со свистком.", "B) Он может быть белым или жёлтым.", "C) Он должен быть круговым огнём.", "D) Всё вышеперечисленное."],
        "correct": 3,
        "en_explain": "Rule 34(b): the light for maneuvering signals must be an all-round white or yellow light, synchronized with the whistle.",
        "ru_explain": "Правило 34(b): огонь для манёвренных сигналов должен быть круговым белым или жёлтым и синхронизирован со свистком.",
        "audio_q": "CQACAgIAAxkBAAIEg2noL2rXc5OFA29mSaZB2IxtSxVeAAISnAACt59BS2ZQKJjxjpnGOwQ",
        "audio_a": "CQACAgIAAxkBAAIEhWnoL3VHqRw6fs8fiI9bZBSpJjA_AAITnAACt59BS23uS8m4m_HwOwQ",
    },
    {
        "num": 52,
        "topic": "narrow_channels",
        "en_q": "INLAND ONLY. On the Western Rivers, a vessel crossing a river must:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. На Западных реках судно пересекающее реку должно:",
        "en_options": ["A) Only keep out of the way of a power-driven vessel descending the river", "B) Keep out of the way of any vessel descending the river", "C) Keep out of the way of a power-driven vessel ascending or descending the river", "D) Keep out of the way of any vessel ascending or descending the river"],
        "ru_options": ["A) Уступать дорогу только моторному судну идущему вниз по течению", "B) Уступать дорогу любому судну идущему вниз по течению", "C) Уступать дорогу моторному судну идущему вверх или вниз по течению", "D) Уступать дорогу любому судну идущему вверх или вниз по течению"],
        "correct": 2,
        "en_explain": "Inland Rules — Western Rivers: a vessel crossing the river shall keep out of the way of power-driven vessels ascending or descending the river.",
        "ru_explain": "Внутренние правила — Западные реки: судно пересекающее реку уступает дорогу моторным судам следующим вверх или вниз по течению.",
        "audio_q": "CQACAgIAAxkBAAIEh2noL66GaXlXwlstYm0CyivQHzVaAAIUnAACt59BS9Xi1cVEUprSOwQ",
        "audio_a": "CQACAgIAAxkBAAIEiWnoL8Sp3KBTh4kp35MxkTXP88u0AAIVnAACt59BSzgHNs-M-iVwOwQ",
    },
    {
        "num": 53,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. You are overtaking another vessel in a narrow channel. You wish to overtake her on her starboard side. You should sound a whistle signal of:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете другое судно в узком канале и хотите обойти его с правого борта. Вы должны подать сигнал:",
        "en_options": ["A) One short blast", "B) Two prolonged blasts followed by one short blast", "C) One prolonged and one short blast", "D) At least five short blasts"],
        "ru_options": ["A) Один короткий сигнал", "B) Два продолжительных и один короткий", "C) Один продолжительный и один короткий", "D) Не менее пяти коротких сигналов"],
        "correct": 0,
        "en_explain": "Rule 34: overtaking on STARBOARD side = ONE short blast. Overtaken vessel responds with same signal to confirm.",
        "ru_explain": "Правило 34: обгон с правого (STARBOARD) борта = один короткий сигнал. Обгоняемое судно отвечает тем же сигналом для подтверждения.",
        "audio_q": "CQACAgIAAxkBAAIEi2noMAVEBxg2ydsikUXm2hKoU_zAAAIWnAACt59BS2JfOaH60oZkOwQ",
        "audio_a": "CQACAgIAAxkBAAIEjWnoMBuU1EgM01UDAqEoa0hf9zwTAAIXnAACt59BS-IhbgNDgz9VOwQ",
    },
    {
        "num": 54,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. You are meeting another vessel in inland waters, and she sounds one short blast on the whistle. This means that:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы встречаете другое судно на внутренних водах и оно подаёт один короткий сигнал. Это означает что:",
        "en_options": ["A) She is changing course to starboard", "B) She is changing course to port", "C) She intends to leave you on her port side", "D) She desires to depart from the Rules"],
        "ru_options": ["A) Оно изменяет курс вправо", "B) Оно изменяет курс влево", "C) Оно намерено оставить вас по своему левому борту", "D) Оно желает отступить от Правил"],
        "correct": 2,
        "en_explain": "Inland Rules: one short blast = intention to pass port to port, leaving the other vessel on the port side.",
        "ru_explain": "Внутренние правила: один короткий сигнал = намерение разойтись левыми бортами, оставив встречное судно по левому борту.",
        "audio_q": "CQACAgIAAxkBAAIEj2noMDU8vgPtdTxrvCXM1xl1AAGMgwACGJwAArefQUtNr4qW4HfROjsE",
        "audio_a": "CQACAgIAAxkBAAIEkWnoMFLU30pQ3wMjrSQv0OHZIgZvAAIZnAACt59BSyGpeCbXN-2uOwQ",
    },
    {
        "num": 55,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. A barge more than 50-meters long would be required to show how many white anchor lights when anchored in a Secretary of Transportation approved 'special anchorage area'?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Сколько белых якорных огней обязана показывать баржа длиной более 50 метров на якоре в специальной якорной зоне одобренной Министерством транспорта?",
        "en_options": ["A) 1", "B) 2", "C) 3", "D) 4"],
        "ru_options": ["A) 1", "B) 2", "C) 3", "D) 4"],
        "correct": 1,
        "en_explain": "US Inland Rules: a barge over 50 meters at anchor in a special anchorage area must show two white anchor lights.",
        "ru_explain": "Внутренние правила США: баржа длиной более 50 метров на якоре в специальной якорной зоне показывает два белых якорных огня.",
        "audio_q": "CQACAgIAAxkBAAIEk2noMG0wUcFCjD8ozLuDC6333cNhAAIbnAACt59BS7s4OgZKzl0QOwQ",
        "audio_a": "CQACAgIAAxkBAAIElWnoMJIWQfj8VJpW18qz6ohFoBVRAAIdnAACt59BS924L4xCKSqmOwQ",
    },
    {
        "num": 56,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel must proceed at a safe speed:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно обязано следовать с безопасной скоростью:",
        "en_options": ["A) In restricted visibility", "B) In congested waters", "C) During darkness", "D) At all times"],
        "ru_options": ["A) В условиях ограниченной видимости", "B) В оживлённых водах", "C) В тёмное время суток", "D) В любое время"],
        "correct": 3,
        "en_explain": "Rule 6: every vessel shall at all times proceed at a safe speed so that she can take proper and effective action to avoid collision.",
        "ru_explain": "Правило 6: каждое судно должно следовать с безопасной скоростью постоянно, чтобы иметь возможность предпринять надлежащие действия для предупреждения столкновения.",
        "audio_q": "CQACAgIAAxkBAAIEl2noMKShJ0prjGe5JDAI9dogPdR9AAIenAACt59BS-nEAxoZeF8cOwQ",
        "audio_a": "CQACAgIAAxkBAAIEmWnoMLAxmSv5WZiDQ2JFFQABsM-_5gACH5wAArefQUtWAAGpr7CrB6Y7BA",
    },
    {
        "num": 57,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. Which of the following is used to show the presence of a partly submerged object being towed?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Что из перечисленного используется для обозначения частично погружённого буксируемого объекта?",
        "en_options": ["A) A diamond shape on the towed object", "B) An all-round light at each end of the towed object", "C) A searchlight from the towing vessel in the direction of the tow", "D) All of the above"],
        "ru_options": ["A) Ромб на буксируемом объекте", "B) Круговой огонь на каждом конце объекта", "C) Прожектор с буксирующего судна в направлении буксира", "D) Всё вышеперечисленное"],
        "correct": 3,
        "en_explain": "Rule 24: any of the listed methods or their combination is permitted to indicate a partly submerged towed object.",
        "ru_explain": "Правило 24: для обозначения частично погружённого буксируемого объекта разрешается использовать любой из перечисленных способов или их комбинацию.",
        "audio_q": "CQACAgIAAxkBAAIEm2noMMDlG0w3LfLBZC62u0v6NPT1AAIgnAACt59BS8n2winUYsgkOwQ",
        "audio_a": "CQACAgIAAxkBAAIEnWnoMMpNtzSjF9-Z5o_nCPkxF-TRAAIinAACt59BS0aw8foNnCWiOwQ",
    },
    {
        "num": 58,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. You are underway on vessel 'A' and sight vessel 'B' which is a vessel underway and fishing. Which statement is true?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Вы на ходу на судне A и видите судно B которое занято рыболовством на ходу. Какое утверждение верно?",
        "en_options": ["A) Vessel 'A' must keep out of the way of vessel 'B' because 'B' is to port.", "B) Vessel 'A' must keep out of the way of vessel 'B' because 'B' is fishing.", "C) Vessel 'B' must keep out of the way of vessel 'A' because 'A' is to starboard.", "D) In this case, both vessels are required by the Rules to keep clear of each other."],
        "ru_options": ["A) Судно A должно уступить дорогу судну B так как B находится слева.", "B) Судно A должно уступить дорогу судну B так как B занято рыболовством.", "C) Судно B должно уступить дорогу судну A так как A находится справа.", "D) Оба судна обязаны уступать дорогу друг другу."],
        "correct": 1,
        "en_explain": "Rule 18: a vessel engaged in fishing has priority over a vessel underway not engaged in special operations. Fishing takes precedence over direction.",
        "ru_explain": "Правило 18: судно занятое рыболовством имеет приоритет над судном на ходу не занятым специальными работами. Рыболовство важнее направления.",
        "audio_q": "CQACAgIAAxkBAAIEn2noMNwn5fN76aNovtbCGwOfL5ycAAIjnAACt59BS0B-Glxt7v1pOwQ",
        "audio_a": "CQACAgIAAxkBAAIEoWnoMO-Bq-HXC3nTeuJlXjduBwAB6AACJJwAArefQUv1V_Vt48a8HDsE",
        "image": "BQACAgIAAxkBAAIFgmnz-Esi1PZXjdGxDTPww2yOAisVAALgowACQAagS1_uv1Tb8B8qOwQ",
    },
    {
        "num": 59,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. If it becomes necessary for a stand-on vessel to take action to avoid collision, she shall, if possible:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Если привилегированному судну необходимо маневрировать для предотвращения столкновения, оно должно по возможности:",
        "en_options": ["A) Not decrease speed", "B) Not increase speed", "C) Not turn to port for a vessel on her own port side", "D) Not turn to starboard for a vessel on her own port side"],
        "ru_options": ["A) Не уменьшать скорость", "B) Не увеличивать скорость", "C) Не поворачивать влево если уступающее судно находится слева", "D) Не поворачивать вправо если уступающее судно находится слева"],
        "correct": 2,
        "en_explain": "Rule 17(c): stand-on vessel shall NOT turn to port when a give-way vessel is on her port side — this closes the gap and increases collision risk.",
        "ru_explain": "Правило 17(c): привилегированное судно не должно поворачивать влево если уступающее судно находится слева — это сокращает дистанцию и увеличивает риск столкновения.",
        "audio_q": "CQACAgIAAxkBAAIEo2noMP9PLFsT6heNXMQ_GGH5yqeHAAIlnAACt59BSy39MCEAAcrZUjsE",
        "audio_a": "CQACAgIAAxkBAAIEpWnoMQ_l4Oo218p4bCgjBvw5IQHxAAImnAACt59BS7w8CV3j5jjcOwQ",
    },
    {
        "num": 60,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. What type of vessel or operation is indicated by a vessel displaying two cones with the apexes together?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Какой тип судна или операции обозначают два конуса вершинами вместе?",
        "en_options": ["A) Sailing", "B) Trawling", "C) Minesweeping", "D) Dredging"],
        "ru_options": ["A) Парусное судно", "B) Траление", "C) Траление мин", "D) Дноуглубительные работы"],
        "correct": 1,
        "en_explain": "Rule 26: two cones with apexes together is the day signal for a vessel engaged in trawling.",
        "ru_explain": "Правило 26: два конуса вершинами вместе — дневной знак судна занятого тралением (trawling).",
        "audio_q": "CQACAgIAAxkBAAIEp2noMR91J7d0WE3aqtNpnKa053M9AAInnAACt59BS6keO5btab7xOwQ",
        "audio_a": "CQACAgIAAxkBAAIEqWnoMTF6SSe6pQ9kVt7njpZBplkZAAIonAACt59BS0P9N6ce9mkvOwQ",
    },
    # ── НОВЫЕ ВОПРОСЫ 61-130 ──
    {
        "num": 61,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. When should the fog signal of a vessel being towed be sounded?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Когда буксируемое судно должно подавать туманный сигнал?",
        "en_options": ["A) After the towing vessel's fog signal", "B) Before the towing vessel's fog signal", "C) Approximately one minute after the towing vessel's fog signal", "D) If the towing vessel is sounding a fog signal, the vessel towed is not required to sound any fog signal."],
        "ru_options": ["A) После туманного сигнала буксирующего судна", "B) До туманного сигнала буксирующего судна", "C) Примерно через минуту после сигнала буксирующего судна", "D) Если буксирующее судно подаёт туманный сигнал, буксируемое судно не обязано подавать сигнал"],
        "correct": 0,
        "en_explain": "Rule 35: a vessel being towed sounds her fog signal (one prolonged + three short blasts) immediately after the towing vessel's signal.",
        "ru_explain": "Буксируемое судно подаёт туманный сигнал сразу после буксирующего судна. Согласно Правилу 35 МППСС-72, сигнал буксируемого судна — один продолжительный и три коротких звука.",
    },
    {
        "num": 62,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. At night, a vessel displaying the lights illustrated in DIAGRAM 46 is:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Ночью судно показывает огни как на ДИАГРАММЕ 46. Это судно:",
        "en_options": ["A) Sailing", "B) Fishing and making way", "C) A pilot boat making way", "D) Fishing and anchored"],
        "ru_options": ["A) Парусное на ходу", "B) Занятое рыболовством на ходу", "C) Лоцманское судно на ходу", "D) Занятое рыболовством на якоре"],
        "correct": 3,
        "en_explain": "Rule 26: a vessel engaged in fishing at anchor shows fishing lights (green over white) without steaming lights.",
        "ru_explain": "Судно занятое рыболовством на якоре показывает огни рыболовства (зелёный над белым) без ходовых огней. Согласно Правилу 26 МППСС-72, якорные огни для рыболовных судов не требуются.",
        "image": "BQACAgIAAxkBAAIF32n7-UvHfuHmLDKlTVPcSEfzuD6IAAJtmgACohPgSwouFCUHgIsGOwQ",
    },
    {
        "num": 63,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. The maximum length of a power-driven vessel which may show an all-round white light and sidelights instead of a masthead light and sidelights is:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Максимальная длина моторного судна которое может показывать круговой белый огонь и бортовые огни вместо топового огня и бортовых огней:",
        "en_options": ["A) 7 meters", "B) 10 meters", "C) 11 meters", "D) 20 meters"],
        "ru_options": ["A) 7 метров", "B) 10 метров", "C) 11 метров", "D) 20 метров"],
        "correct": 2,
        "en_explain": "Rule 23(c): power-driven vessels less than 12 meters may show an all-round white light and sidelights instead of masthead light. Maximum length is under 12 meters, i.e. 11 meters.",
        "ru_explain": "Моторные суда длиной менее 12 метров могут показывать круговой белый огонь и бортовые огни вместо топового огня. Максимальная длина такого судна — менее 12 метров, то есть 11 метров. Правило 23(c) МППСС-72.",
    },
    {
        "num": 64,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. When shall the stand-on vessel change course and speed?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Когда привилегированное судно должно изменить курс и скорость?",
        "en_options": ["A) The stand-on vessel may change course and speed at any time as it has the right-of-way", "B) After the give-way vessel sounds one blast in a crossing situation", "C) When action by the give-way vessel alone cannot prevent collision", "D) When the two vessels become less than one-half mile apart"],
        "ru_options": ["A) Привилегированное судно может изменить курс и скорость в любое время так как имеет преимущество", "B) После того как уступающее судно подаст один сигнал при пересечении курсов", "C) Когда действий уступающего судна одного недостаточно для предотвращения столкновения", "D) Когда два судна сближаются на расстояние менее полумили"],
        "correct": 2,
        "en_explain": "Rule 17(b): the stand-on vessel is obliged to take action only when it becomes apparent that the give-way vessel alone cannot prevent collision.",
        "ru_explain": "Привилегированное судно обязано изменить курс или скорость только когда действий уступающего судна одного недостаточно для предотвращения столкновения. Правило 17(b) МППСС-72.",
    },
    {
        "num": 65,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. When moving from a berth alongside a quay (wharf), a vessel must sound:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. При отходе от причала (набережной) судно должно подать:",
        "en_options": ["A) A prolonged blast", "B) Three short blasts", "C) A long blast", "D) None of the above"],
        "ru_options": ["A) Один продолжительный сигнал", "B) Три коротких сигнала", "C) Один длинный сигнал", "D) Никакого сигнала"],
        "correct": 3,
        "en_explain": "COLREGS Rule 34: no whistle signal is required when departing a berth under international rules. This requirement exists only in US Inland Rules.",
        "ru_explain": "Международные правила (МППСС-72) не требуют подачи звукового сигнала при отходе от причала. Это требование существует только во Внутренних правилах США. Согласно МППСС-72 Правило 34, сигналы подаются при манёврировании в виду другого судна.",
    },
    {
        "num": 66,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. You see a vessel displaying the day signal shown in DIAGRAM 6. The vessel is:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Вы видите судно показывающее дневной знак как на ДИАГРАММЕ 6 (шар — ромб — шар). Это судно:",
        "en_options": ["A) Not under command", "B) Fishing with trawls", "C) Laying cable", "D) Aground"],
        "ru_options": ["A) Лишённое управления", "B) Занятое тралением", "C) Прокладывающее кабель", "D) На мели"],
        "correct": 2,
        "en_explain": "Rule 27(b): ball-diamond-ball vertical day signal = vessel restricted in ability to maneuver. Cable laying falls under this category.",
        "ru_explain": "Три фигуры вертикально — шар, ромб, шар — дневной знак судна ограниченного в возможности маневрировать. Прокладка кабеля относится к этой категории. Правило 27(b) МППСС-72.",
        "image": "BQACAgIAAxkBAAIF4Wn7-bw9KVWV9jrIsqybdNNPyqLzAAJumgACohPgS0_em2phZzT5OwQ",
    },
    {
        "num": 67,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. You are underway in fog and hear a fog signal of two prolonged blasts on your starboard quarter. You should:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Вы на ходу в тумане и слышите сигнал два продолжительных по правой раковине. Вы должны:",
        "en_options": ["A) Stop your vessel", "B) Change your course to the left", "C) Change course to the right", "D) Hold your course and speed"],
        "ru_options": ["A) Остановить судно", "B) Изменить курс влево", "C) Изменить курс вправо", "D) Держать курс и скорость"],
        "correct": 3,
        "en_explain": "Rule 19: two prolonged blasts = vessel underway but not making way. Signal on the starboard quarter means vessel is astern — no immediate threat. No course change required if collision risk is absent.",
        "ru_explain": "Два продолжительных сигнала — сигнал судна на ходу но не движущегося вперёд. Сигнал по раковине означает что судно позади и не создаёт непосредственной угрозы. Согласно Правилу 19 МППСС-72 изменение курса не требуется если угроза столкновения отсутствует.",
    },
    {
        "num": 68,
        "topic": "narrow_channels",
        "en_q": "INLAND ONLY. You are overtaking a vessel in a narrow channel and wish to leave her on your starboard side. You may:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы обгоняете судно в узком канале и хотите оставить его по правому борту. Вы можете:",
        "en_options": ["A) Attempt to contact her on the radiotelephone to arrange for the passage", "B) Overtake her without sounding whistle signals", "C) Sound four short blasts", "D) Sound one short blast"],
        "ru_options": ["A) Попытаться связаться по радиотелефону для согласования прохода", "B) Обогнать без звуковых сигналов", "C) Подать четыре коротких сигнала", "D) Подать один короткий сигнал"],
        "correct": 0,
        "en_explain": "Inland Rule 34: overtaking on the starboard side is non-standard and only permitted after radio agreement with the vessel being overtaken.",
        "ru_explain": "Обгон с правого борта — нестандартный манёвр на внутренних водах. Согласно Правилу 34 Inland Rules, такой обгон разрешён только после согласования по радиотелефону с обгоняемым судном.",
    },
    {
        "num": 69,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. A signal of intent, which must be answered by another vessel, is sounded in international waters by:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Сигнал намерения на который другое судно обязано ответить в международных водах подаётся:",
        "en_options": ["A) A vessel meeting another head and head", "B) A vessel crossing the course of another", "C) A vessel overtaking another", "D) Any of the above"],
        "ru_options": ["A) Судном встречающим другое нос к носу", "B) Судном пересекающим курс другого", "C) Судном обгоняющим другое", "D) Любым из вышеперечисленных"],
        "correct": 2,
        "en_explain": "COLREGS Rule 34(c): only the overtaking vessel in a narrow channel sounds a signal of intent (two prolonged + one or two short) which must be answered by the vessel being overtaken.",
        "ru_explain": "Согласно МППСС-72 Правилу 34(c), только обгоняющее судно в узком канале подаёт сигнал намерения (два продолжительных + один или два коротких), на который обгоняемое судно обязано ответить.",
    },
    {
        "num": 70,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. Which signal is only sounded by a power-driven vessel?",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Какой сигнал подаётся только моторным судном?",
        "en_options": ["A) A signal meaning \"I am altering my course to starboard.\"", "B) A signal meaning \"I intend to overtake you on your starboard side.\"", "C) A signal meaning that the vessel sounding it is in doubt as to the other vessel's actions.", "D) A signal sounded when approaching a bend."],
        "ru_options": ["A) Сигнал означающий «Я изменяю курс вправо»", "B) Сигнал означающий «Я намерен обогнать вас с правого борта»", "C) Сигнал означающий сомнение в намерениях другого судна", "D) Сигнал при приближении к повороту"],
        "correct": 0,
        "en_explain": "COLREGS Rule 34(a): maneuvering signals (one, two or three short blasts) are sounded only by power-driven vessels in sight of each other.",
        "ru_explain": "Согласно МППСС-72 Правилу 34(a), манёвренные сигналы (один, два или три коротких) подаются только моторными судами в виду друг друга.",
    },
    {
        "num": 71,
        "topic": "narrow_channels",
        "en_q": "INTERNATIONAL ONLY. In which case would an overtaking vessel sound a whistle signal of two prolonged followed by one short blast?",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. В каком случае обгоняющее судно подаёт сигнал два продолжительных и один короткий?",
        "en_options": ["A) When overtaking in restricted visibility", "B) When overtaking in a narrow channel", "C) When overtaking on open waters", "D) When no other vessels are in the immediate area"],
        "ru_options": ["A) При обгоне в условиях ограниченной видимости", "B) При обгоне в узком канале", "C) При обгоне на открытой воде", "D) Когда поблизости нет других судов"],
        "correct": 1,
        "en_explain": "COLREGS Rule 34(c): two prolonged + one short = intent to overtake on starboard side in a narrow channel or fairway only.",
        "ru_explain": "Согласно МППСС-72 Правилу 34(c), сигнал два продолжительных + один короткий означает намерение обогнать с правого борта и подаётся только в узком канале или на фарватере.",
    },
    {
        "num": 72,
        "topic": "definitions",
        "en_q": "INTERNATIONAL ONLY. The International Rules of the Road apply:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Международные правила предупреждения столкновений применяются:",
        "en_options": ["A) To all waters which are not inland waters", "B) Only to waters outside the territorial waters of the United States", "C) Only to waters where foreign vessels travel", "D) Upon the high seas and connecting waters navigable by seagoing vessels"],
        "ru_options": ["A) На всех водах которые не являются внутренними", "B) Только за пределами территориальных вод США", "C) Только на водах где ходят иностранные суда", "D) В открытом море и соединённых с ним водах доступных для морских судов"],
        "correct": 3,
        "en_explain": "COLREGS Rule 1(a): these Rules shall apply to all vessels upon the high seas and in all waters connected therewith navigable by seagoing vessels.",
        "ru_explain": "МППСС-72 Правило 1(a): Правила применяются ко всем судам в открытом море и соединённых с ним водах по которым могут плавать морские суда.",
    },
    {
        "num": 73,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. Vessel \"A\" is overtaking vessel \"B\" on open waters as shown in DIAGRAM 17, and will pass without changing course. Vessel \"A\":",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Судно A обгоняет судно B на открытой воде как показано на ДИАГРАММЕ 17 и разойдётся без изменения курса. Судно A:",
        "en_options": ["A) Should sound two short blasts", "B) Should sound the danger signal", "C) Should sound one long blast", "D) Need not sound any whistle signals"],
        "ru_options": ["A) Должно подать два коротких сигнала", "B) Должно подать сигнал опасности", "C) Должно подать один длинный сигнал", "D) Не обязано подавать никаких звуковых сигналов"],
        "correct": 3,
        "en_explain": "COLREGS Rule 34: maneuvering signals are only sounded when altering course. On open waters, if overtaking is safe without course change — no whistle signal required.",
        "ru_explain": "Согласно МППСС-72 Правилу 34, манёвренные сигналы подаются только при изменении курса. Если обгон происходит на открытой воде без изменения курса и расхождение безопасное — звуковые сигналы не требуются.",
        "image": "BQACAgIAAxkBAAIF42n7-dnuaRinowbatiFJD5vC0F26AAJvmgACohPgS3J0Z_UdNRlMOwQ",
    },
    {
        "num": 74,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. Two steam vessels are meeting in the situation shown in DIAGRAM 37. One short blast by vessel \"A\" means:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Два моторных судна встречаются как показано на ДИАГРАММЕ 37. Один короткий сигнал судна A означает:",
        "en_options": ["A) \"I am altering my course to starboard\"", "B) \"I intend to pass on your port side\"", "C) \"My intention is to hold course and speed\"", "D) \"I intend to pass on your starboard side\""],
        "ru_options": ["A) «Я изменяю курс вправо»", "B) «Я намерен пройти по вашему левому борту»", "C) «Моё намерение — держать курс и скорость»", "D) «Я намерен пройти по вашему правому борту»"],
        "correct": 1,
        "en_explain": "Inland Rule 34: one short blast = intent to pass port to port, i.e. pass on the other vessel's port side.",
        "ru_explain": "На внутренних водах США один короткий сигнал означает намерение разойтись левыми бортами — пройти по левому борту встречного судна. Правило 34 Inland Rules.",
        "image": "BQACAgIAAxkBAAIF5Wn7-hAC3J4jLBzRJPXKwYr-DE4jAAJwmgACohPgS4ir4L68TlRqOwQ",
    },
    {
        "num": 75,
        "topic": "narrow_channels",
        "en_q": "INLAND ONLY. You are approaching a sharp bend in a river. You have sounded a prolonged blast and it has been answered by a vessel on the other side of the bend. Which statement is true?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы приближаетесь к крутому повороту реки. Вы подали продолжительный сигнал и получили ответ от судна с другой стороны поворота. Какое утверждение верно?",
        "en_options": ["A) Both vessels must exchange passing signals when they sight each other visually.", "B) No further whistle signals are necessary.", "C) The vessel downriver must stop engines and navigate with caution."],
        "ru_options": ["A) Оба судна должны обменяться сигналами расхождения когда увидят друг друга визуально.", "B) Дальнейших звуковых сигналов не требуется.", "C) Судно идущее вниз по реке должно застопорить машины и следовать с осторожностью."],
        "correct": 0,
        "en_explain": "Inland Rule 34(e): the prolonged blast at a bend is a warning signal only. When vessels sight each other visually they must exchange proper maneuvering signals.",
        "ru_explain": "Согласно Inland Rules Правилу 34(e), продолжительный сигнал при приближении к повороту — предупредительный. Когда суда войдут в зону визуальной видимости они обязаны обменяться манёвренными сигналами расхождения.",
    },
    {
        "num": 76,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. At night, a barge being towed astern must display:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Ночью баржа буксируемая за кормой должна показывать:",
        "en_options": ["A) Red and green sidelights only", "B) A white sternlight only", "C) Sidelights and a sternlight", "D) One all-round white light"],
        "ru_options": ["A) Только красный и зелёный бортовые огни", "B) Только белый кормовой огонь", "C) Бортовые огни и кормовой огонь", "D) Один круговой белый огонь"],
        "correct": 2,
        "en_explain": "Rule 24(e): a vessel being towed shall exhibit sidelights and a sternlight.",
        "ru_explain": "Согласно Правилу 24(e) МППСС-72, буксируемое судно должно показывать бортовые огни и кормовой огонь.",
    },
    {
        "num": 77,
        "topic": "narrow_channels",
        "en_q": "INLAND ONLY. You are in charge of a power-driven vessel crossing a river on the Western Rivers. You must keep out of the way of:",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы на моторном судне пересекаете реку на Западных реках. Вы должны уступить дорогу:",
        "en_options": ["A) A sail vessel descending the river", "B) A power-driven vessel ascending the river", "C) A vessel restricted in its ability to maneuver crossing the river", "D) Any of the above"],
        "ru_options": ["A) Парусному судну идущему вниз по течению", "B) Моторному судну идущему вверх по течению", "C) Судну ограниченному в манёвре пересекающему реку", "D) Всем вышеперечисленным"],
        "correct": 3,
        "en_explain": "Inland Rules — Western Rivers Rule 9: a vessel crossing the river shall keep out of the way of vessels ascending or descending, and vessels restricted in ability to maneuver.",
        "ru_explain": "Inland Rules — Западные реки: судно пересекающее реку уступает дорогу судам следующим вверх или вниз по течению, а также судам ограниченным в манёвре. Правило 9 Inland Rules.",
    },
    {
        "num": 78,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. A 45-meter vessel is pulling a 210-meter tow. She may exhibit:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно длиной 45 метров буксирует состав длиной 210 метров. Оно может показывать:",
        "en_options": ["A) A masthead light forward, and two masthead lights in a vertical line aft", "B) Three masthead lights forward and one aft", "C) Two masthead lights forward and no after-masthead light", "D) None of the above"],
        "ru_options": ["A) Один топовый огонь носовой и два топовых огня кормовых вертикально", "B) Три топовых огня носовых и один кормовой", "C) Два топовых огня носовых и ни одного кормового", "D) Ничего из вышеперечисленного"],
        "correct": 1,
        "en_explain": "Rule 24(a): when the length of the tow exceeds 200 meters, the towing vessel shows three masthead lights vertically instead of two.",
        "ru_explain": "Согласно Правилу 24(a) МППСС-72, когда длина буксира превышает 200 метров, буксирующее судно показывает три топовых огня вертикально вместо двух.",
    },
    {
        "num": 79,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel engaged in fishing must display a light in the direction of any gear that extends outward more than 150 meters. The color of this light is:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно занятое рыболовством должно показывать огонь в направлении снастей выходящих более чем на 150 метров. Цвет этого огня:",
        "en_options": ["A) White", "B) Green", "C) Red", "D) Yellow"],
        "ru_options": ["A) Белый", "B) Зелёный", "C) Красный", "D) Жёлтый"],
        "correct": 0,
        "en_explain": "Rule 26(c): a vessel engaged in fishing shall show a white light in the direction of the gear when it extends more than 150 meters from the vessel.",
        "ru_explain": "Согласно Правилу 26(c) МППСС-72, судно занятое рыболовством показывает белый огонь в направлении снастей если они выходят более чем на 150 метров от судна.",
    },
    {
        "num": 80,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. A vessel engaged in fishing during the day would show:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно занятое рыболовством днём показывает:",
        "en_options": ["A) One black ball", "B) Two cones with bases together", "C) A cone, point downward", "D) Two cones, points together"],
        "ru_options": ["A) Один чёрный шар", "B) Два конуса основаниями вместе", "C) Конус вершиной вниз", "D) Два конуса вершинами вместе"],
        "correct": 3,
        "en_explain": "Rule 26(b): a vessel engaged in trawling shows two cones with apexes together as a day signal.",
        "ru_explain": "Согласно Правилу 26(b) МППСС-72, судно занятое тралением днём показывает два конуса вершинами вместе.",
    },
    {
        "num": 81,
        "topic": "sound_signals",
        "en_q": "BOTH INTERNATIONAL & INLAND. You are underway, in fog, when you hear a whistle signal of one prolonged blast followed by two short blasts. This signal could indicate a vessel:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Вы на ходу в тумане и слышите один продолжительный и два коротких сигнала. Это может быть судно:",
        "en_options": ["A) Not under command", "B) Being towed", "C) Aground", "D) All of the above"],
        "ru_options": ["A) Лишённое управления", "B) Буксируемое", "C) На мели", "D) Любое из вышеперечисленных"],
        "correct": 0,
        "en_explain": "Rule 35: one prolonged + two short is sounded by vessels not under command, restricted in ability to maneuver, constrained by draft, sailing, fishing, or towing. A vessel being towed sounds one prolonged + three short. A vessel aground rings a bell. Therefore only A is correct.",
        "ru_explain": "Правило 35 МППСС-72: один продолжительный + два коротких подают суда лишённые управления, ограниченные в манёвре, стеснённые осадкой, парусные, рыболовные и буксирующие. Буксируемое судно — один продолжительный + три коротких. Судно на мели — звонок в колокол. Из вариантов подходит только A.",
    },
    {
        "num": 82,
        "topic": "definitions",
        "en_q": "BOTH INTERNATIONAL & INLAND. The word \"vessel\", in the Rules, includes:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Слово «судно» в Правилах включает:",
        "en_options": ["A) Sailing ships", "B) Nondisplacement craft", "C) Seaplanes", "D) All of the above"],
        "ru_options": ["A) Парусные суда", "B) Суда без водоизмещения", "C) Гидросамолёты", "D) Всё вышеперечисленное"],
        "correct": 3,
        "en_explain": "Rule 3(a): the word 'vessel' includes every description of water craft, including nondisplacement craft and seaplanes, used or capable of being used as a means of transportation on water.",
        "ru_explain": "Правило 3(a) МППСС-72: слово «судно» означает все виды плавучих средств включая неводоизмещающие суда и гидросамолёты используемые или могущие быть использованными в качестве средства передвижения по воде.",
    },
    {
        "num": 83,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. A sailing vessel which is also propelled by machinery shall show during daylight hours:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Парусное судно использующее также механический двигатель днём должно показывать:",
        "en_options": ["A) A black diamond", "B) A black cone", "C) A black ball", "D) A basket"],
        "ru_options": ["A) Чёрный ромб", "B) Чёрный конус", "C) Чёрный шар", "D) Корзину"],
        "correct": 1,
        "en_explain": "Rule 25(e): a sailing vessel proceeding under sail when also being propelled by machinery shall exhibit a conical shape, apex downwards, in the forward part of the vessel.",
        "ru_explain": "Согласно Правилу 25(e) МППСС-72, парусное судно идущее под двигателем днём показывает чёрный конус вершиной вниз на носу судна там где он лучше всего виден.",
    },
    {
        "num": 84,
        "topic": "lights_shapes",
        "en_q": "BOTH INTERNATIONAL & INLAND. A partially submerged object towed by a vessel must show during the day:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Частично погружённый буксируемый объект днём должен показывать:",
        "en_options": ["A) A diamond shape when the length of the tow is 200 meters or less", "B) A diamond shape only when the length of the tow exceeds 200 meters in length", "C) One black ball", "D) One black ball only when the length of the tow exceeds 200 meters in length"],
        "ru_options": ["A) Ромб когда длина буксира 200 метров или менее", "B) Ромб только когда длина буксира превышает 200 метров", "C) Один чёрный шар", "D) Один чёрный шар только когда длина буксира превышает 200 метров"],
        "correct": 0,
        "en_explain": "Rule 24(g): a partially submerged object being towed shows a diamond shape when the length of tow is 200 meters or less; additional diamonds are added above 200 meters.",
        "ru_explain": "Правило 24(g) МППСС-72: частично погружённый объект при длине буксира до 200 метров показывает один ромб, при длине более 200 метров — дополнительные ромбы.",
    },
    {
        "num": 85,
        "topic": "lights_shapes",
        "en_q": "INTERNATIONAL ONLY. The light which may be used with vessel's whistle is to be:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Огонь который может использоваться вместе со свистком судна должен быть:",
        "en_options": ["A) Used when the whistle is broken", "B) Used prior to sounding the whistle", "C) Used only at night", "D) A white light"],
        "ru_options": ["A) Использован когда свисток сломан", "B) Использован до подачи свистка", "C) Использован только ночью", "D) Белым огнём"],
        "correct": 3,
        "en_explain": "COLREGS Rule 34(b): a vessel may supplement any whistle signal with a light signal. The light shall be a white all-round light visible at a distance of at least 5 miles.",
        "ru_explain": "Согласно МППСС-72 Правилу 34(b), судно может дополнять звуковые сигналы световыми. Световой сигнал должен быть белым круговым огнём видимым со всех сторон на расстоянии не менее 5 миль.",
    },
    {
        "num": 86,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. Vessel \"A\" (towing) and vessel \"B\" are meeting as shown in DIAGRAM 12. Which statement is TRUE?",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Судно A (буксировщик) и судно B встречаются как показано на ДИАГРАММЕ 12. Какое утверждение верно?",
        "en_options": ["A) Both vessels should alter course to starboard and pass port to port.", "B) Both vessels should alter course to port and pass starboard to starboard.", "C) Vessel A must hold course as the towing vessel has right of way.", "D) No action is required as the vessels will pass safely."],
        "ru_options": ["A) Оба судна должны изменить курс вправо и разойтись левыми бортами.", "B) Оба судна должны изменить курс влево и разойтись правыми бортами.", "C) Судно A должно держать курс так как буксировщик имеет преимущество.", "D) Никаких действий не требуется так как суда разойдутся безопасно."],
        "correct": 0,
        "en_explain": "Rule 14: when vessels meet head-on, both shall alter course to starboard and pass port to port. The presence of a tow does not change this rule.",
        "ru_explain": "Правило 14 МППСС-72: при встрече нос к носу оба судна берут вправо и расходятся левыми бортами. Наличие буксира не меняет это правило.",
        "image": "BQACAgIAAxkBAAIF52n7-jQYcdP90PcFdK9LH7pskiJLAAJxmgACohPgS8hNBIjZlHGpOwQ",
    },
    {
        "num": 87,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. When two vessels are in sight of one another, all of the following signals may be given EXCEPT:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Когда два судна находятся в зоне взаимной видимости все следующие сигналы могут быть поданы КРОМЕ:",
        "en_options": ["A) A light signal of at least five short and rapid flashes", "B) Four short whistle blasts", "C) One prolonged, one short, one prolonged and one short whistle blasts", "D) Two short whistle blasts"],
        "ru_options": ["A) Световой сигнал не менее пяти коротких частых вспышек", "B) Четыре коротких свистка", "C) Один продолжительный, один короткий, один продолжительный и один короткий", "D) Два коротких свистка"],
        "correct": 1,
        "en_explain": "COLREGS Rule 34: maneuvering signals are one, two or three short blasts; danger signal is five or more short blasts; overtaking in narrow channel is two prolonged + one or two short. Four short blasts are not prescribed by the Rules.",
        "ru_explain": "МППСС-72 Правило 34: манёвренные сигналы — один, два или три коротких; сигнал опасности — пять и более коротких; сигнал обгона в узком канале — два продолжительных + один или два коротких. Четыре коротких сигнала не предусмотрены Правилами.",
    },
    {
        "num": 88,
        "topic": "lights_shapes",
        "en_q": "INLAND ONLY. What is true of a \"special flashing light\"?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Что верно в отношении «специального мигающего огня»?",
        "en_options": ["A) It is optional below the Baton Rouge Highway Bridge.", "B) It may show through an arc of not less than 180°.", "C) It flashes at the rate of 120 flashes per minute.", "D) All of the above"],
        "ru_options": ["A) Он необязателен ниже моста Батон-Руж.", "B) Он может освещать дугу не менее 180°.", "C) Он мигает со скоростью 120 вспышек в минуту.", "D) Всё вышеперечисленное."],
        "correct": 1,
        "en_explain": "Inland Rules Annex II: the special flashing yellow light for pushed ahead vessels must show through an arc of not less than 180°. Flash rate is 50-70 per minute, not 120.",
        "ru_explain": "Согласно Inland Rules Приложению II, специальный мигающий жёлтый огонь для толкаемых составов должен освещать дугу не менее 180°. Частота мигания — 50-70 вспышек в минуту, не 120.",
    },
    {
        "num": 89,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. You are underway in fog and hear a fog signal consisting of one prolonged and two short blasts. It could be any of the following EXCEPT a vessel:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Вы на ходу в тумане и слышите один продолжительный и два коротких сигнала. Это может быть любое из следующих судов КРОМЕ:",
        "en_options": ["A) Engaged in minesweeping", "B) Engaged in fishing", "C) Constrained by her draft", "D) Being towed"],
        "ru_options": ["A) Занятого тралением мин", "B) Занятого рыболовством", "C) Ограниченного своей осадкой", "D) Буксируемого"],
        "correct": 3,
        "en_explain": "Rule 35: one prolonged + two short is sounded by vessels not under command, restricted in ability to maneuver, constrained by draft, sailing, fishing, or towing. A vessel being towed sounds one prolonged + three short blasts.",
        "ru_explain": "Правило 35 МППСС-72: один продолжительный + два коротких подают суда лишённые управления, ограниченные в манёвре, стеснённые осадкой, парусные, рыболовные и буксирующие. Буксируемое судно подаёт один продолжительный + три коротких.",
    },
    {
        "num": 90,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. The rule regarding look-outs applies:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Правило о вахтенном наблюдении применяется:",
        "en_options": ["A) In restricted visibility", "B) In heavy traffic", "C) Between dusk and dawn", "D) All of the above"],
        "ru_options": ["A) В условиях ограниченной видимости", "B) В оживлённом судоходстве", "C) В тёмное время суток", "D) Во всех вышеперечисленных случаях"],
        "correct": 3,
        "en_explain": "Rule 5: every vessel shall at all times maintain a proper look-out by sight and hearing as well as by all available means appropriate to the prevailing circumstances.",
        "ru_explain": "Правило 5 МППСС-72: каждое судно должно постоянно вести надлежащее визуальное и слуховое наблюдение используя все имеющиеся средства. Требование действует постоянно и при любых условиях.",
    },
    {
        "num": 91,
        "topic": "sound_signals",
        "en_q": "INTERNATIONAL ONLY. When vessels are in sight of one another, two short blasts from one of the vessels means:",
        "ru_q": "ТОЛЬКО МЕЖДУНАРОДНЫЕ ВОДЫ. Когда суда находятся в зоне взаимной видимости два коротких сигнала от одного из судов означают:",
        "en_options": ["A) \"I am altering my course to starboard\"", "B) \"I am altering my course to port\"", "C) \"I intend to change course to starboard\"", "D) \"I intend to change course to port\""],
        "ru_options": ["A) «Я изменяю курс вправо»", "B) «Я изменяю курс влево»", "C) «Я намерен изменить курс вправо»", "D) «Я намерен изменить курс влево»"],
        "correct": 1,
        "en_explain": "COLREGS Rule 34(a): two short blasts mean 'I am altering my course to port'. Unlike Inland Rules where signals express intent, under COLREGS they indicate a maneuver already being executed.",
        "ru_explain": "МППСС-72 Правило 34(a): два коротких сигнала означают «Я изменяю свой курс влево». В отличие от Inland Rules где сигналы выражают намерение, в международных водах они указывают на манёвр уже выполняемый.",
    },
    {
        "num": 92,
        "topic": "steering_rules",
        "en_q": "BOTH INTERNATIONAL & INLAND. The Rules state that certain factors are to be taken into account when determining safe speed. Those factors include:",
        "ru_q": "МЕЖДУНАРОДНЫЕ И ВНУТРЕННИЕ ВОДЫ. Правила указывают что при определении безопасной скорости необходимо учитывать определённые факторы. К ним относятся:",
        "en_options": ["A) State of wind, sea, and current, and the proximity of navigational hazards", "B) Maximum attainable speed of your vessel", "C) Temperature", "D) Aids to navigation that are available"],
        "ru_options": ["A) Состояние ветра, моря и течения, близость навигационных опасностей", "B) Максимально достижимая скорость судна", "C) Температура воздуха", "D) Имеющиеся навигационные средства"],
        "correct": 0,
        "en_explain": "Rule 6: factors for safe speed include visibility, traffic density, vessel maneuverability, navigational hazards, state of wind, sea and current, and draft in relation to water depth.",
        "ru_explain": "Правило 6 МППСС-72: при выборе безопасной скорости учитываются состояние видимости, плотность судоходства, манёвренность судна, навигационные опасности, состояние ветра моря и течения, осадка судна относительно глубины воды.",
    },
    {
        "num": 93,
        "topic": "sound_signals",
        "en_q": "INLAND ONLY. You have made your vessel up to a tow and are moving from a pier out into the main channel. If your engines are turning ahead, what whistle signal should you sound?",
        "ru_q": "ТОЛЬКО ВНУТРЕННИЕ ВОДЫ. Вы сформировали буксирный состав и отходите от причала в основной канал. Если машины работают вперёд, какой звуковой сигнал следует подать?",
        "en_options": ["A) One prolonged and two short blasts", "B) Three long blasts", "C) One prolonged blast", "D) Five or more short rapid blasts"],
        "ru_options": ["A) Один продолжительный и два коротких", "B) Три длинных", "C) Один продолжительный", "D) Пять и более коротких частых"],
        "correct": 2,
        "en_explain": "Inland Rules: a vessel departing a dock with engines going ahead sounds ONE prolonged blast (4-6 sec) to warn surrounding vessels.",
        "ru_explain": "Inland Rules: судно отходящее от причала с машиной вперёд подаёт один продолжительный сигнал (4-6 сек) для предупреждения окружающих судов.",
    },
    {
        "num": 94,
        "topic": "charts",
        "en_q": "Which government agency publishes the U.S. Coast Pilot?",
        "ru_q": "Какое государственное ведомство публикует U.S. Coast Pilot?",
        "en_options": ["A) U.S. Coast Guard", "B) National Ocean Service", "C) National Geospatial-Intelligence Agency", "D) Army Corps of Engineers"],
        "ru_options": ["A) Береговая охрана США", "B) Национальная океанографическая служба (NOS)", "C) Национальное агентство геопространственной разведки (NGA)", "D) Инженерный корпус армии США"],
        "correct": 1,
        "en_explain": "The U.S. Coast Pilot is published by the National Ocean Service (NOS), a division of NOAA.",
        "ru_explain": "U.S. Coast Pilot публикуется Национальной океанографической службой (NOS) — подразделением NOAA. Издание содержит навигационную информацию о прибрежных водах, портах, гаванях и внутренних водных путях США.",
    },
    {
        "num": 95,
        "topic": "charts",
        "en_q": "Notice to Mariners are published:",
        "ru_q": "Notice to Mariners (Извещения мореплавателям) публикуются:",
        "en_options": ["A) Daily", "B) Weekly", "C) Monthly", "D) Yearly"],
        "ru_options": ["A) Ежедневно", "B) Еженедельно", "C) Ежемесячно", "D) Ежегодно"],
        "correct": 1,
        "en_explain": "Notice to Mariners are published weekly by the National Geospatial-Intelligence Agency (NGA).",
        "ru_explain": "Notice to Mariners публикуются еженедельно Национальным агентством геопространственной разведки (NGA) и содержат обновления навигационных карт, изменения огней, знаков и опасностей.",
    },
    {
        "num": 96,
        "topic": "charts",
        "en_q": "A method of representing a spherical, three dimensional surface on a plane onto a two dimensional sheet of paper is called a:",
        "ru_q": "Метод изображения сферической трёхмерной поверхности на плоском двумерном листе бумаги называется:",
        "en_options": ["A) Map", "B) Chart", "C) Projection", "D) Mirror Image"],
        "ru_options": ["A) Карта", "B) Чарт", "C) Проекция", "D) Зеркальное изображение"],
        "correct": 2,
        "en_explain": "A cartographic projection is a mathematical method of transferring the spherical surface of the Earth onto a flat plane.",
        "ru_explain": "Картографическая проекция — математический метод перенесения сферической поверхности Земли на плоскость. Наиболее распространённая морская проекция — проекция Меркатора.",
    },
    {
        "num": 97,
        "topic": "charts",
        "en_q": "A set of great circles which pass through the north and south geographic poles are called:",
        "ru_q": "Совокупность больших кругов проходящих через северный и южный географические полюса называется:",
        "en_options": ["A) Meridians of longitude", "B) Parallels of latitude", "C) Rhumb lines", "D) Equators"],
        "ru_options": ["A) Меридианы долготы", "B) Параллели широты", "C) Локсодромы", "D) Экваторы"],
        "correct": 0,
        "en_explain": "Meridians are great circles passing through both geographic poles used to measure longitude.",
        "ru_explain": "Меридианы — большие круги проходящие через оба географических полюса. Они используются для измерения долготы — угла от нулевого меридиана (Гринвич) на восток или запад.",
    },
    {
        "num": 98,
        "topic": "charts",
        "en_q": "The compass rose on a nautical chart indicates both variation and:",
        "ru_q": "Картушка компаса на морской карте показывает магнитное склонение (variation) и:",
        "en_options": ["A) Deviation", "B) Annual rate of variation change", "C) Compass error", "D) Precession"],
        "ru_options": ["A) Девиацию", "B) Годовое изменение склонения", "C) Погрешность компаса", "D) Прецессию"],
        "correct": 1,
        "en_explain": "The compass rose shows true north, magnetic north, the amount of magnetic variation, and its annual rate of change.",
        "ru_explain": "Картушка компаса показывает истинный север, магнитный север, величину магнитного склонения и его годовое изменение. Девиация зависит от конкретного судна и на карте не указывается.",
    },
    {
        "num": 99,
        "topic": "charts",
        "en_q": "The depth of water on a chart is indicated as 23 meters. This is equal to:",
        "ru_q": "Глубина воды на карте указана как 23 метра. Это равно:",
        "en_options": ["A) 11.5 fathoms", "B) 12.6 fathoms", "C) 69.0 feet", "D) 78.6 feet"],
        "ru_options": ["A) 11,5 фатомов", "B) 12,6 фатомов", "C) 69,0 футов", "D) 78,6 футов"],
        "correct": 1,
        "en_explain": "1 fathom = 1.8288 m. 23 m / 1.8288 = 12.6 fathoms. (Fathom is an old British nautical unit = 6 feet = 1.83 m.)",
        "ru_explain": "1 фатом (fathom) = 1,8288 м. 23 м ÷ 1,8288 = 12,6 фатомов. (Fathom — старинная британская морская мера глубины = 6 футов = 1,83 м. «Fathom» похожа на «Морская сажень» — русский аналог, использовалась во времена Петра I)",
    },
    {
        "num": 100,
        "topic": "charts",
        "en_q": "NOS Charts of 1:40,000 or larger scale carry a:",
        "ru_q": "Карты NOS масштаба 1:40 000 и крупнее содержат:",
        "en_options": ["A) Logarithmic Speed Scale", "B) Nautical mile Scale", "C) Yard Scale", "D) Statute Mile Scale"],
        "ru_options": ["A) Логарифмическую шкалу скоростей", "B) Шкалу морских миль", "C) Шкалу ярдов", "D) Шкалу статутных миль"],
        "correct": 0,
        "en_explain": "NOS charts of large scale (1:40,000 and larger) carry a logarithmic speed scale for determining vessel speed.",
        "ru_explain": "Карты NOS крупного масштаба (1:40 000 и крупнее) содержат логарифмическую шкалу скоростей которая позволяет определять скорость судна по времени прохождения известного расстояния.",
    },
    {
        "num": 101,
        "topic": "charts",
        "en_q": "An angle between a line connecting one point with another and a base is called a:",
        "ru_q": "Угол между линией соединяющей одну точку с другой и базовой линией называется:",
        "en_options": ["A) Tangent Plane", "B) Direction", "C) Parallel", "D) Meridian"],
        "ru_options": ["A) Касательная плоскость", "B) Направление", "C) Параллель", "D) Меридиан"],
        "correct": 1,
        "en_explain": "In navigation, direction is an angle measured from a base line (usually true north) to a line connecting two points, measured clockwise from 000 to 360 degrees.",
        "ru_explain": "В навигации направление — угол измеряемый от базовой линии (обычно истинный север) до линии соединяющей две точки, по часовой стрелке от 000° до 360°.",
    },
    {
        "num": 102,
        "topic": "charts",
        "en_q": "On salt water, distances are measured in:",
        "ru_q": "На солёной воде расстояния измеряются в:",
        "en_options": ["A) Statute Miles", "B) Kilometers", "C) Fathoms", "D) Nautical Miles"],
        "ru_options": ["A) Статутных милях", "B) Километрах", "C) Фатомах", "D) Морских милях"],
        "correct": 3,
        "en_explain": "At sea, distances are measured in nautical miles. One nautical mile = 1852 meters.",
        "ru_explain": "На море расстояния измеряются в морских милях. Одна морская миля равна одной угловой минуте широты = 1852 метра.",
    },
    {
        "num": 103,
        "topic": "charts",
        "en_q": "The compass rose on a chart shows true and magnetic north directions.",
        "ru_q": "Картушка компаса на карте показывает направления истинного и магнитного севера.",
        "en_options": ["A) True", "B) False"],
        "ru_options": ["A) Верно", "B) Неверно"],
        "correct": 0,
        "en_explain": "The compass rose contains two rings: the outer shows True North, the inner shows Magnetic North.",
        "ru_explain": "Картушка компаса на морской карте содержит два кольца: внешнее показывает истинный север (True North), внутреннее — магнитный север (Magnetic North) с учётом местного магнитного склонения.",
    },
    {
        "num": 104,
        "topic": "charts",
        "en_q": "Some basic information which is included on a chart may include:",
        "ru_q": "Основная информация на морской карте включает:",
        "en_options": ["A) Type of projection", "B) Scale", "C) Unit of depth measurement", "D) All of the above"],
        "ru_options": ["A) Тип проекции", "B) Масштаб", "C) Единицу измерения глубин", "D) Всё вышеперечисленное"],
        "correct": 3,
        "en_explain": "A standard NOS nautical chart contains the type of projection, scale, units of depth measurement, date of publication and other navigational information.",
        "ru_explain": "Стандартная морская карта NOS содержит тип картографической проекции, масштаб, единицы измерения глубин, дату издания и другую навигационную информацию.",
    },
    {
        "num": 105,
        "topic": "charts",
        "en_q": "You should use only the latest edition of a chart to insure safe navigation.",
        "ru_q": "Для безопасной навигации следует использовать только последнее издание карты.",
        "en_options": ["A) True", "B) False"],
        "ru_options": ["A) Верно", "B) Неверно"],
        "correct": 0,
        "en_explain": "Using outdated charts is dangerous. Chart currency is maintained through Notice to Mariners.",
        "ru_explain": "Использование устаревших карт опасно так как навигационная обстановка постоянно меняется. Актуальность карт обеспечивается через Notice to Mariners.",
    },
    {
        "num": 106,
        "topic": "charts",
        "en_q": "The color on a chart which is ideal for reading during night time navigation is:",
        "ru_q": "Цвет на карте идеально подходящий для чтения при ночной навигации:",
        "en_options": ["A) Red", "B) Blue", "C) Magenta", "D) Green"],
        "ru_options": ["A) Красный", "B) Синий", "C) Пурпурный (Magenta)", "D) Зелёный"],
        "correct": 2,
        "en_explain": "Magenta is used on nautical charts for navigational information. Under red bridge lighting, magenta markings remain readable without disrupting night vision.",
        "ru_explain": "Пурпурный (magenta) цвет используется на морских картах для навигационной информации. При красном освещении ходового мостика пурпурные обозначения хорошо читаются не нарушая ночную адаптацию зрения.",
    },
    {
        "num": 107,
        "topic": "charts",
        "en_q": "One nautical mile equals:",
        "ru_q": "Одна морская миля равна:",
        "en_options": ["A) 10 seconds of longitude.", "B) 5 minutes of longitude.", "C) 10 minutes of latitude.", "D) 1 minute of latitude."],
        "ru_options": ["A) 10 угловым секундам долготы", "B) 5 угловым минутам долготы", "C) 10 угловым минутам широты", "D) 1 угловой минуте широты"],
        "correct": 3,
        "en_explain": "A nautical mile = one arc minute of a meridian (latitude) = 1852 meters.",
        "ru_explain": "Морская миля определяется как длина одной угловой минуты меридиана (широты) и равна 1852 метра. На меркаторских картах широтная шкала используется для измерения расстояний.",
    },
    {
        "num": 108,
        "topic": "charts",
        "en_q": "Who publishes charts of the high seas and foreign waters based on its own and other nations surveys?",
        "ru_q": "Кто публикует карты открытого моря и иностранных вод на основе собственных и зарубежных съёмок?",
        "en_options": ["A) NOAA", "B) NOS", "C) NGA", "D) NIMA"],
        "ru_options": ["A) NOAA", "B) NOS", "C) NGA", "D) NIMA"],
        "correct": 2,
        "en_explain": "NGA (National Geospatial-Intelligence Agency) publishes charts of the high seas and foreign waters. NIMA is the former name of NGA.",
        "ru_explain": "NGA (National Geospatial-Intelligence Agency) публикует карты открытого моря и иностранных вод. NIMA — прежнее название этого агентства. NOS публикует карты прибрежных вод США.",
    },
    {
        "num": 109,
        "topic": "charts",
        "en_q": "The edition number and date, month and year of each NOS chart are printed:",
        "ru_q": "Номер издания и дата (месяц и год) каждой карты NOS напечатаны:",
        "en_options": ["A) Upper right corner", "B) Lower right corner", "C) Upper left corner", "D) Lower left corner"],
        "ru_options": ["A) В правом верхнем углу", "B) В правом нижнем углу", "C) В левом верхнем углу", "D) В левом нижнем углу"],
        "correct": 3,
        "en_explain": "On NOS charts, the edition number and publication date are located in the lower left corner.",
        "ru_explain": "На картах NOS номер издания, дата выпуска и информация о корректуре располагаются в левом нижнем углу карты.",
    },
    {
        "num": 110,
        "topic": "charts",
        "en_q": "Depth soundings on a chart are taken at:",
        "ru_q": "Глубины на карте измерены от уровня:",
        "en_options": ["A) Mean higher high water", "B) Mean low water", "C) Mean lower low water", "D) Mean high water"],
        "ru_options": ["A) Среднего высшего полного прилива", "B) Среднего малой воды", "C) Среднего низшего малого прилива", "D) Среднего полного прилива"],
        "correct": 2,
        "en_explain": "On US charts, depths are referenced to Mean Lower Low Water (MLLW) — the lowest calculated water level.",
        "ru_explain": "На картах США глубины указываются от уровня среднего низшего малого прилива (MLLW). Это наиболее низкий расчётный уровень воды что обеспечивает максимальную безопасность.",
    },
    {
        "num": 111,
        "topic": "charts",
        "en_q": "The publication which can be used for reference in regards to specific abbreviations on a chart is:",
        "ru_q": "Издание используемое для расшифровки условных обозначений и сокращений на морских картах:",
        "en_options": ["A) USCG Light List", "B) Coast Pilot", "C) Chart No. 1", "D) Tide and Current Tables"],
        "ru_options": ["A) Light List (Береговой охраны США)", "B) Coast Pilot", "C) Chart No. 1", "D) Таблицы приливов и течений"],
        "correct": 2,
        "en_explain": "Chart No. 1 is a joint NOAA/NGA publication containing symbols, abbreviations and conventions used on US nautical charts.",
        "ru_explain": "Chart No. 1 — совместное издание NOAA и NGA содержащее полный перечень символов, сокращений и условных обозначений используемых на морских картах США.",
    },
    {
        "num": 112,
        "topic": "charts",
        "en_q": "Vertical clearance datum for objects on a chart such as a bridge is taken at:",
        "ru_q": "Вертикальный габарит объектов на карте (например мостов) отсчитывается от уровня:",
        "en_options": ["A) Mean lower low water", "B) Neap tide high water", "C) Mean high water", "D) Low water"],
        "ru_options": ["A) Среднего низшего малого прилива", "B) Высокой воды при квадратурных приливах", "C) Среднего полного прилива", "D) Малой воды"],
        "correct": 2,
        "en_explain": "Vertical clearances on US charts are referenced to Mean High Water (MHW) — the highest calculated water level.",
        "ru_explain": "Вертикальные габариты мостов на картах США отсчитываются от уровня среднего полного прилива (MHW). Это наиболее высокий расчётный уровень воды обеспечивающий минимальный гарантированный клиренс.",
    },
    {
        "num": 113,
        "topic": "charts",
        "en_q": "The most common projection used for ocean and coastal areas is called a:",
        "ru_q": "Наиболее распространённая проекция для океанских и прибрежных районов называется:",
        "en_options": ["A) Polyconic Projection", "B) Tangent Plane Projection", "C) Mercator Projection", "D) Pilot Projection"],
        "ru_options": ["A) Поликоническая проекция", "B) Проекция касательной плоскости", "C) Проекция Меркатора", "D) Пилотная проекция"],
        "correct": 2,
        "en_explain": "The Mercator Projection is a cylindrical map projection where a rhumb line (constant course) is a straight line — ideal for marine navigation.",
        "ru_explain": "Проекция Меркатора — цилиндрическая картографическая проекция при которой локсодромия (линия постоянного курса) изображается прямой линией. Идеальна для морской навигации.",
    },
    {
        "num": 114,
        "topic": "charts",
        "en_q": "The nature of the shore is sometimes indicated by various symbols which may include:",
        "ru_q": "Характер берега иногда обозначается различными символами которые могут включать:",
        "en_options": ["A) Fine dots", "B) Double magenta lines", "C) Large double black and yellow lines", "D) None of the above"],
        "ru_options": ["A) Мелкие точки", "B) Двойные пурпурные линии", "C) Крупные двойные чёрно-жёлтые линии", "D) Ничего из вышеперечисленного"],
        "correct": 0,
        "en_explain": "Fine dots on a chart indicate a sandy shore. Symbols are described in Chart No. 1.",
        "ru_explain": "На морских картах мелкие точки обозначают песчаный берег. Описание всех символов дано в Chart No. 1.",
    },
    {
        "num": 115,
        "topic": "charts",
        "en_q": "A buoy position on a chart is indicated by:",
        "ru_q": "Положение буя на карте обозначается:",
        "en_options": ["A) Tear drop shape", "B) Black diamond", "C) Large black dot", "D) Small open circle"],
        "ru_options": ["A) Каплевидной формой", "B) Чёрным ромбом", "C) Большой чёрной точкой", "D) Маленьким незакрашенным кружком"],
        "correct": 3,
        "en_explain": "According to Chart No. 1, the exact position of a buoy is indicated by a small open circle beneath the buoy symbol.",
        "ru_explain": "Согласно Chart No. 1, точное положение буя на карте обозначается маленьким незакрашенным кружком под символом буя.",
    },
    {
        "num": 116,
        "topic": "charts",
        "en_q": "This chart is the largest scale and most detailed of the series:",
        "ru_q": "Этот тип карт является наиболее крупномасштабным и детальным в серии:",
        "en_options": ["A) Harbor Charts", "B) Small Craft Charts", "C) Coast Charts", "D) Special Coast Charts"],
        "ru_options": ["A) Портовые карты (Harbor Charts)", "B) Карты для малых судов (Small Craft Charts)", "C) Береговые карты (Coast Charts)", "D) Специальные береговые карты"],
        "correct": 0,
        "en_explain": "Harbor Charts (scale 1:50,000 and larger) are the most detailed, used for entering ports and harbors.",
        "ru_explain": "Портовые карты (Harbor Charts) имеют масштаб 1:50 000 и крупнее и являются наиболее детальными. Они используются для захода в порты, гавани и внутренние водные пути.",
    },
    {
        "num": 117,
        "topic": "charts",
        "en_q": "This type of chart combines historical data such as weather, wave heights, prevailing winds but is not intended to be used alone for navigation:",
        "ru_q": "Этот тип карт объединяет исторические данные о погоде, высоте волн и преобладающих ветрах но не предназначен для самостоятельного использования при навигации:",
        "en_options": ["A) Harbor Chart", "B) Polyconic Chart", "C) General Chart", "D) Pilot Chart"],
        "ru_options": ["A) Портовая карта", "B) Поликоническая карта", "C) Генеральная карта", "D) Пилотная карта"],
        "correct": 3,
        "en_explain": "Pilot Charts (NGA) contain statistical data on weather, currents, winds and wave heights by month — used for planning ocean passages only.",
        "ru_explain": "Pilot Charts издаются NGA и содержат статистические данные о погоде, течениях, ветрах и высоте волн по месяцам. Используются для планирования океанских переходов но не заменяют навигационные карты.",
    },
    {
        "num": 118,
        "topic": "charts",
        "en_q": "A \"map\" and a \"chart\" are essentially used for the same navigational purposes.",
        "ru_q": "«Карта» (map) и «чарт» (chart) используются по существу для одних и тех же навигационных целей.",
        "en_options": ["A) False", "B) True"],
        "ru_options": ["A) Неверно", "B) Верно"],
        "correct": 0,
        "en_explain": "A nautical chart is for water navigation (depths, hazards, lights). A map is for land navigation. These are fundamentally different documents.",
        "ru_explain": "Морской чарт предназначен для навигации по воде и содержит глубины, опасности, огни. Карта (map) предназначена для сухопутной навигации. Это принципиально разные документы.",
    },
    {
        "num": 119,
        "topic": "charts",
        "en_q": "If using an electronic chart for navigation, it is not necessary to use printed charts.",
        "ru_q": "При использовании электронной карты для навигации нет необходимости использовать печатные карты.",
        "en_options": ["A) True", "B) False"],
        "ru_options": ["A) Верно", "B) Неверно"],
        "correct": 1,
        "en_explain": "USCG requires up-to-date paper charts on board. Electronic charts are an additional tool but do not replace official printed charts.",
        "ru_explain": "USCG требует наличия актуальных бумажных карт на борту. Электронные карты являются дополнительным инструментом но не заменяют официальные печатные карты.",
    },
    {
        "num": 120,
        "topic": "charts",
        "en_q": "A ____________ provides the shortest distance between any two points.",
        "ru_q": "____________ обеспечивает кратчайшее расстояние между любыми двумя точками.",
        "en_options": ["A) Large square", "B) Parallel", "C) Great circle", "D) Rhumb line"],
        "ru_options": ["A) Большой квадрат", "B) Параллель", "C) Большой круг", "D) Локсодромия"],
        "correct": 2,
        "en_explain": "A great circle arc is the shortest distance between two points on Earth's surface.",
        "ru_explain": "Большой круг (great circle) — дуга большого круга является кратчайшим расстоянием между двумя точками на поверхности Земли.",
    },
    {
        "num": 121,
        "topic": "charts",
        "en_q": "\"Precautionary Area\" SEE NOTE G is a reference to:",
        "ru_q": "«Precautionary Area — СМ. ПРИМЕЧАНИЕ G» означает:",
        "en_options": ["A) A note on the chart pertaining to specific navigation information for that area.", "B) A note in the coast pilot pertaining to specific navigation information for that area.", "C) A note in the light list pertaining to specific navigation information for that area.", "D) A note in Chart 1 pertaining to specific navigation information for that area."],
        "ru_options": ["A) Примечание на карте относящееся к конкретной навигационной информации для этого района.", "B) Примечание в Coast Pilot относящееся к конкретной навигационной информации для этого района.", "C) Примечание в Light List относящееся к конкретной навигационной информации для этого района.", "D) Примечание в Chart No. 1 относящееся к конкретной навигационной информации для этого района."],
        "correct": 0,
        "en_explain": "Inscriptions like 'SEE NOTE G' refer to notes placed directly on the same chart containing specific navigational information for that area.",
        "ru_explain": "Надписи типа «SEE NOTE G» на морских картах отсылают к примечаниям размещённым непосредственно на той же карте с конкретной навигационной информацией для данного района.",
    },
    {
        "num": 122,
        "topic": "charts",
        "en_q": "Types of fog signals are not indicated on a chart.",
        "ru_q": "Типы туманных сигналов не указываются на морской карте.",
        "en_options": ["A) True", "B) False"],
        "ru_options": ["A) Верно", "B) Неверно"],
        "correct": 1,
        "en_explain": "Nautical charts contain information about fog signals — type (horn, bell, whistle), characteristic and period. Also published in the Light List.",
        "ru_explain": "Морские карты содержат информацию о туманных сигналах навигационных знаков — тип сигнала, характеристику и период. Эти данные также публикуются в Light List.",
    },
    {
        "num": 123,
        "topic": "charts",
        "en_q": "The abbreviation on a chart of \"Obstn\" indicates:",
        "ru_q": "Аббревиатура «Obstn» на морской карте обозначает:",
        "en_options": ["A) Obstacle", "B) Illusion", "C) Obstruction", "D) Object"],
        "ru_options": ["A) Препятствие (Obstacle)", "B) Иллюзия (Illusion)", "C) Навигационная опасность (Obstruction)", "D) Объект (Object)"],
        "correct": 2,
        "en_explain": "According to Chart No. 1, 'Obstn' = Obstruction — a navigational hazard with imprecisely established position or dimensions.",
        "ru_explain": "Согласно Chart No. 1, «Obstn» — сокращение от «Obstruction» (навигационная опасность). Обозначает объект опасный для судоходства с неточно установленным положением.",
    },
    {
        "num": 124,
        "topic": "weather",
        "en_q": "A weather forecast states that the wind will commence backing. In the Northern Hemisphere, this would indicate that it will:",
        "ru_q": "Прогноз погоды сообщает что ветер начнёт «backing» (заходить). В Северном полушарии это означает что он:",
        "en_options": ["A) Decrease in velocity", "B) Continue blowing from the same direction", "C) Shift in a counterclockwise manner", "D) Shift in a clockwise manner"],
        "ru_options": ["A) Уменьшится в скорости", "B) Продолжит дуть с того же направления", "C) Изменит направление против часовой стрелки", "D) Изменит направление по часовой стрелке"],
        "correct": 2,
        "en_explain": "'Backing' = wind shift counterclockwise. 'Veering' = clockwise. In the Northern Hemisphere backing wind is associated with an approaching cyclone.",
        "ru_explain": "«Backing» — смещение ветра против часовой стрелки (например с юга на восток на север). «Veering» — смещение по часовой стрелке. В Северном полушарии заходящий ветер обычно связан с приближением циклона.",
    },
    {
        "num": 125,
        "topic": "weather",
        "en_q": "Barometers are usually calibrated to indicate atmospheric pressure in:",
        "ru_q": "Барометры обычно калибруются для показания атмосферного давления в:",
        "en_options": ["A) Inches of mercury and centimeters", "B) Feet of mercury and millibars", "C) Inches of mercury and millibars", "D) Inches of mercury and millimeters"],
        "ru_options": ["A) Дюймах ртутного столба и сантиметрах", "B) Футах ртутного столба и миллибарах", "C) Дюймах ртутного столба и миллибарах", "D) Дюймах ртутного столба и миллиметрах"],
        "correct": 2,
        "en_explain": "Marine barometers display pressure in inches of mercury (inHg) and millibars (mb). Standard: 29.92 inHg = 1013.25 mb.",
        "ru_explain": "Морские барометры показывают атмосферное давление в дюймах ртутного столба (inHg) и миллибарах (mb). Стандартное давление: 29,92 inHg = 1013,25 мб.",
    },
    {
        "num": 126,
        "topic": "weather",
        "en_q": "The atmosphere in the vicinity of a high pressure area is called a(n):",
        "ru_q": "Атмосфера в районе области высокого давления называется:",
        "en_options": ["A) Anticyclone", "B) Cold front", "C) Occluded front", "D) Cyclone"],
        "ru_options": ["A) Антициклон", "B) Холодный фронт", "C) Окклюдированный фронт", "D) Циклон"],
        "correct": 0,
        "en_explain": "An anticyclone is a high pressure area. In the Northern Hemisphere air moves clockwise and generally brings clear weather.",
        "ru_explain": "Антициклон — область высокого атмосферного давления. В Северном полушарии воздух движется по часовой стрелке. Антициклоны обычно приносят ясную погоду.",
    },
    {
        "num": 127,
        "topic": "weather",
        "en_q": "On the approach of a warm front, barometric pressure usually:",
        "ru_q": "При приближении тёплого фронта барометрическое давление обычно:",
        "en_options": ["A) Falls", "B) Is steady", "C) Is uncertain", "D) Rises"],
        "ru_options": ["A) Падает", "B) Остаётся стабильным", "C) Непредсказуемо", "D) Растёт"],
        "correct": 0,
        "en_explain": "On approach of a warm front, pressure gradually falls, cloud cover increases and visibility deteriorates.",
        "ru_explain": "При приближении тёплого фронта барометрическое давление постепенно падает, облачность увеличивается, видимость ухудшается.",
    },
    {
        "num": 128,
        "topic": "weather",
        "en_q": "If it is impossible to avoid a hurricane in the Northern Hemisphere, the most favorable place to be when the storm passes is in:",
        "ru_q": "Если невозможно избежать урагана в Северном полушарии наиболее благоприятное место при прохождении шторма:",
        "en_options": ["A) The dangerous semicircle", "B) The eye (center) of the storm", "C) That half of the storm lying to the right of the storm's path", "D) That half of the storm lying to the left of the storm's path"],
        "ru_options": ["A) Опасный полукруг", "B) Глаз (центр) шторма", "C) Правая половина относительно пути шторма", "D) Левая половина относительно пути шторма"],
        "correct": 3,
        "en_explain": "In the Northern Hemisphere the right semicircle is dangerous (wind + forward speed). The left (navigable) semicircle is less dangerous.",
        "ru_explain": "В Северном полушарии правый полукруг урагана опасен — скорость ветра складывается со скоростью шторма. Левый полукруг менее опасен.",
    },
    {
        "num": 129,
        "topic": "weather",
        "en_q": "An air mass is termed \"warm\" if:",
        "ru_q": "Воздушная масса называется «тёплой» если:",
        "en_options": ["A) It originated in a low pressure area", "B) It originated in a high pressure area", "C) The ground over which it moves is cooler than the air", "D) It is above 70 degrees F"],
        "ru_options": ["A) Она образовалась в области низкого давления", "B) Она образовалась в области высокого давления", "C) Поверхность над которой она движется холоднее воздуха", "D) Её температура выше 70 градусов по Фаренгейту"],
        "correct": 2,
        "en_explain": "An air mass is warm when it moves over a cooler surface. The name is determined by relative temperature difference, not absolute temperature.",
        "ru_explain": "Воздушная масса называется тёплой когда она движется над более холодной поверхностью. Название определяется относительной разницей температур, а не абсолютной.",
    },
    {
        "num": 130,
        "topic": "weather",
        "en_q": "The fog most commonly encountered at sea is called:",
        "ru_q": "Наиболее распространённый вид тумана в море называется:",
        "en_options": ["A) Conduction fog", "B) Radiation fog", "C) Frontal fog", "D) Advection fog"],
        "ru_options": ["A) Кондукционный туман", "B) Радиационный туман", "C) Фронтальный туман", "D) Адвекционный туман"],
        "correct": 3,
        "en_explain": "Advection fog forms when warm moist air moves over cooler water. Radiation fog is typical of land.",
        "ru_explain": "Адвекционный туман образуется когда тёплый влажный воздух перемещается над более холодной водной поверхностью. Это наиболее распространённый тип морского тумана.",
    },
]


user_state = {}

MAIN_MENU_TEXT = "⚓ Добро пожаловать! / Welcome to Captain6PackBot!\n\nВыберите режим / Choose mode:"

TOPICS = {
    "sound_signals":   {"ru": "🔊 Звуковые сигналы",     "en": "Sound Signals"},
    "lights_shapes":   {"ru": "💡 Огни и знаки",          "en": "Lights & Shapes"},
    "steering_rules":  {"ru": "🚢 Маневрирование",        "en": "Steering Rules"},
    "narrow_channels": {"ru": "🌊 Узкие каналы и реки",   "en": "Narrow Channels"},
    "visibility":      {"ru": "🌫️ Ограниченная видимость", "en": "Visibility"},
    "distress":        {"ru": "🆘 Сигналы бедствия",      "en": "Distress Signals"},
    "definitions":     {"ru": "📋 Определения",           "en": "Definitions"},
    "charts":          {"ru": "🗺️ Карты и публикации",    "en": "Charts & Publications"},
    "weather":         {"ru": "🌦️ Погода",                "en": "Weather"},
}


def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Тест / Quiz — все вопросы", callback_data="menu_quiz")],
        [InlineKeyboardButton("📚 Topics / Темы — по разделам", callback_data="menu_topics")],
        [InlineKeyboardButton("📖 Glossary / Глоссарий", callback_data="menu_glossary")],
        [InlineKeyboardButton("🔊👂 Listening / Аудирование 🚗🏋️", callback_data="menu_drive")],
        [InlineKeyboardButton("📊 My Progress / Мой прогресс", callback_data="menu_progress")],
        [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
    ])


def get_topics_keyboard():
    buttons = []
    for key, names in TOPICS.items():
        count = sum(1 for q in QUESTIONS if q.get("topic") == key)
        btn_text = f"{names['en']} / {names['ru']} ({count})"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"topic_{key}")])
    buttons.append([InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def get_topic_start_keyboard(topic_key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start / Начать", callback_data=f"start_topic_{topic_key}")],
        [InlineKeyboardButton("📚 Topics / Темы", callback_data="menu_topics")],
        [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
    ])


def start(update: Update, context: CallbackContext):
    update.message.reply_text(MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())


# ── ГЛОССАРИЙ ──

def send_glossary(chat_id, context, index, old_msg_id=None):
    if old_msg_id:
        try:
            context.bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
        except Exception as e:
            logging.error(f"DELETE ERROR: {e}")

    if index >= len(GLOSSARY):
        context.bot.send_message(
            chat_id=chat_id,
            text=MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard()
        )
        return

    term = GLOSSARY[index]
    caption = f"📖 {index + 1} из {len(GLOSSARY)}\n\nEN: {term['term']}\nRU: {term['ru']}"
    logging.info(f"SENDING GLOSSARY index={index} file_id={term['file_id'][:20]}")

    try:
        context.bot.send_audio(
            chat_id=chat_id,
            audio=term["file_id"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Next", callback_data=f"glo_{index + 1}")],
                [InlineKeyboardButton("🏠 Меню / Menu", callback_data="main_menu_from_glo")],
            ])
        )
        logging.info(f"GLOSSARY SENT OK index={index}")
    except Exception as e:
        logging.error(f"SEND_AUDIO ERROR: {e}")


# ── ТЕСТ ──

def strip_letter(opt_text):
    if len(opt_text) >= 3 and opt_text[1] == ")":
        return opt_text[3:].strip()
    return opt_text.strip()


def build_question_keyboard(state):
    lang = state["lang"]
    lang_btn = "🌐 English / На русском" if lang == "ru" else "🌐 Russian / На английском"
    q = QUESTIONS[state["order"][state["pos"]]]
    buttons = [
        [
            InlineKeyboardButton("A", callback_data="answer_0"),
            InlineKeyboardButton("B", callback_data="answer_1"),
            InlineKeyboardButton("C", callback_data="answer_2"),
            InlineKeyboardButton("D", callback_data="answer_3"),
        ],
        [InlineKeyboardButton(lang_btn, callback_data="toggle_lang")],
        [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
    ]
    if q.get("audio_q"):
        buttons.insert(2, [InlineKeyboardButton("▶️ Play / Слушать", callback_data="play_q")])
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

    # Если у вопроса есть картинка — отправляем её отдельным сообщением перед вопросом
    if q.get("image"):
        try:
            img_msg = context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=q["image"]
            )
            state["audio_msg_ids"].append(img_msg.message_id)
        except Exception as e:
            logging.error(f"SEND_PHOTO ERROR: {e}")

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


def send_progress_snapshot(chat_id, context, state):
    total = len(QUESTIONS)
    en_done = len(state["progress_en"])
    ru_done = len(state["progress_ru"])
    audio_done = len(state["progress_audio"])

    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    date_str = now.strftime("%d %b %Y")

    # Бары прогресса (10 символов)
    def bar(count, total):
        filled = round(count / total * 10) if total > 0 else 0
        return "▓" * filled + "░" * (10 - filled)

    # Прогресс по темам (EN)
    topic_lines = []
    for key, names in TOPICS.items():
        topic_nums = set(q["num"] for q in QUESTIONS if q.get("topic") == key)
        topic_total = len(topic_nums)
        topic_done = len(state["progress_en"] & topic_nums)
        if topic_total == 0:
            continue
        if topic_done == topic_total:
            icon = "✅"
        elif topic_done > 0:
            icon = "🔄"
        else:
            icon = "⬜"
        topic_lines.append(f"{icon} {names['en']}: {topic_done}/{topic_total}")

    topics_text = "\n".join(topic_lines)

    # Дельта с прошлого снапшота
    last = state.get("last_snapshot")
    if last is None:
        delta_text = f"📅 {date_str}\nFirst snapshot / Первый снапшот"
    else:
        d_en = en_done - last["en"]
        d_ru = ru_done - last["ru"]
        d_audio = audio_done - last["audio"]
        delta_text = (
            f"📅 {date_str} — since last time / с прошлого раза:\n"
            f"🇺🇸 English: +{d_en}\n"
            f"🇷🇺 Russian: +{d_ru}\n"
            f"🎧 Audio: +{d_audio}"
        )

    text = (
        f"📊 My Progress / Мой прогресс\n\n"
        f"🇺🇸 English answered:  {en_done} / {total}\n"
        f"{bar(en_done, total)}\n\n"
        f"🇷🇺 На русском:  {ru_done} / {total}\n"
        f"{bar(ru_done, total)}\n\n"
        f"🎧 Audio listened:  {audio_done} / {total}\n"
        f"{bar(audio_done, total)}\n\n"
        f"By topic / По темам (🇺🇸 EN):\n"
        f"{topics_text}\n\n"
        f"{'─' * 20}\n"
        f"{delta_text}"
    )

    # Сохраняем текущий снапшот
    state["last_snapshot"] = {"en": en_done, "ru": ru_done, "audio": audio_done}

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if user_id not in user_state:
        order = list(range(len(QUESTIONS)))
        random.shuffle(order)
        user_state[user_id] = {
            "lang": "ru", "pos": 0, "g_index": 0, "order": order, "audio_msg_ids": [],
            "progress_en": set(),
            "progress_ru": set(),
            "progress_audio": set(),
            "last_snapshot": None,
        }

    state = user_state[user_id]
    if "audio_msg_ids" not in state:
        state["audio_msg_ids"] = []
    if "progress_en" not in state:
        state["progress_en"] = set()
    if "progress_ru" not in state:
        state["progress_ru"] = set()
    if "progress_audio" not in state:
        state["progress_audio"] = set()
    if "last_snapshot" not in state:
        state["last_snapshot"] = None

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

    # ── Меню из прогресса — снапшот НЕ удаляется ──
    elif query.data == "main_menu_from_progress":
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

    # ── Темы ──
    elif query.data == "menu_topics":
        try:
            query.message.delete()
        except Exception:
            pass
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📚 Choose topic / Выберите тему:",
            reply_markup=get_topics_keyboard()
        )

    elif query.data.startswith("topic_"):
        topic_key = query.data[6:]
        topic = TOPICS.get(topic_key, {})
        count = sum(1 for q in QUESTIONS if q.get("topic") == topic_key)
        text = (
            f"{topic.get('en', '')} / {topic.get('ru', '')}\n\n"
            f"{count} questions / {count} вопросов\n\n"
            f"Questions on this topic only / Вопросы только по этой теме"
        )
        try:
            query.edit_message_text(text, reply_markup=get_topic_start_keyboard(topic_key))
        except Exception:
            pass

    elif query.data.startswith("start_topic_"):
        topic_key = query.data[12:]
        topic_order = [i for i, q in enumerate(QUESTIONS) if q.get("topic") == topic_key]
        random.shuffle(topic_order)
        state["order"] = topic_order
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
            state["progress_audio"].add(q["num"])

    elif query.data == "play_a":
        q = QUESTIONS[state["order"][state["pos"]]]
        if q.get("audio_a"):
            msg = context.bot.send_audio(chat_id=query.message.chat_id, audio=q["audio_a"])
            state["audio_msg_ids"].append(msg.message_id)
            state["progress_audio"].add(q["num"])

    elif query.data.startswith("answer_"):
        chosen = int(query.data.split("_")[1])
        q = QUESTIONS[state["order"][state["pos"]]]
        lang = state["lang"]

        # Прогресс — фиксируем только первый ответ
        q_num = q["num"]
        if q_num not in state["progress_en"] and q_num not in state["progress_ru"]:
            if lang == "en":
                state["progress_en"].add(q_num)
            else:
                state["progress_ru"].add(q_num)

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

        lang_btn = "🌐 English / На русском" if lang == "ru" else "🌐 Russian / На английском"
        buttons = [
            [
                InlineKeyboardButton("⬅️ Back / Назад", callback_data="back_to_question"),
                InlineKeyboardButton("➡️ Next / Далее", callback_data="next_question"),
            ],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("▶️ Play / Слушать", callback_data="play_a")])
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
        lang_btn = "🌐 English / На русском" if lang == "ru" else "🌐 Russian / На английском"
        result = f"💡 Правильный ответ: {correct_answer_text}\n\n{explain}"
        buttons = [
            [
                InlineKeyboardButton("⬅️ Back / Назад", callback_data="back_to_question"),
                InlineKeyboardButton("➡️ Next / Далее", callback_data="next_question"),
            ],
            [InlineKeyboardButton(lang_btn, callback_data="toggle_lang_answer")],
            [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
        ]
        if q.get("audio_a"):
            buttons.insert(1, [InlineKeyboardButton("▶️ Play / Слушать", callback_data="play_a")])
        query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "next_question":
        next_pos = state["pos"] + 1
        if next_pos >= len(state["order"]):
            # Определяем это тема или общий тест
            current_topic = None
            if len(state["order"]) < len(QUESTIONS):
                # Это тест по теме — ищем какая тема
                first_q = QUESTIONS[state["order"][0]]
                current_topic = first_q.get("topic")

            if current_topic and current_topic in TOPICS:
                topic = TOPICS[current_topic]
                count = len(state["order"])
                text = (
                    f"🎉 Topic complete! / Тема завершена!\n\n"
                    f"{topic['en']} / {topic['ru']}\n\n"
                    f"✅ {count} questions done / {count} вопросов пройдено\n\n"
                    f"What's next? / Что дальше?"
                )
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Repeat / Повторить", callback_data=f"start_topic_{current_topic}")],
                    [InlineKeyboardButton("📚 Topics / Темы", callback_data="menu_topics")],
                    [InlineKeyboardButton("📝 All questions / Все вопросы", callback_data="menu_quiz")],
                    [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
                ])
                query.edit_message_text(text, reply_markup=buttons)
            else:
                # Общий тест — начинаем сначала
                state["pos"] = 0
                send_question(query, state, context)
        else:
            state["pos"] = next_pos
            send_question(query, state, context)

    # ── Глоссарий ──
    elif query.data == "menu_glossary":
        state["g_index"] = 0
        send_glossary(query.message.chat_id, context, 0, old_msg_id=query.message.message_id)

    elif query.data.startswith("glo_"):
        index = int(query.data[4:])
        state["g_index"] = index
        send_glossary(query.message.chat_id, context, index, old_msg_id=query.message.message_id)

    # ── Прогресс ──
    elif query.data == "menu_progress":
        try:
            query.message.delete()
        except Exception:
            pass
        send_progress_snapshot(query.message.chat_id, context, state)

    # ── Аудирование ──
    elif query.data == "menu_drive":
        query.edit_message_text(
            "🔊👂 Режим аудирования в разработке / Listening mode coming soon! 🚗 🏋️",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Menu / Меню", callback_data="main_menu")],
            ])
        )


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
