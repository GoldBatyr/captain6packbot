import os, json, base64, time, urllib.request

PHOTOS_DIR = '/Users/Batyr/Documents/exam_screens/photos'
IMAGES_MAP = '/Users/Batyr/Documents/exam_screens/images_map.json'
QUESTIONS_FILE = '/Users/Batyr/Documents/exam_screens/questions.json'
OUTPUT_FILE = '/Users/Batyr/Documents/exam_screens/questions_with_images.json'
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

DIAGRAM_QUESTIONS = [
    {'num': 223, 'diagram': 'DIAGRAM 8',  'hint': 'vessel A and vessel B pushing ahead meeting head on'},
    {'num': 391, 'diagram': 'DIAGRAM 75', 'hint': 'lights of a vessel'},
    {'num': 401, 'diagram': 'DIAGRAM 81', 'hint': 'yellow lights flashing lock lights'},
    {'num': 430, 'diagram': 'DIAGRAM 29', 'hint': 'vessels A and B passing narrow channel'},
    {'num': 444, 'diagram': 'DIAGRAM 46', 'hint': 'vessel displaying lights at night'},
    {'num': 449, 'diagram': 'DIAGRAM 6',  'hint': 'day signal vessel'},
    {'num': 456, 'diagram': 'DIAGRAM 17', 'hint': 'vessel A overtaking vessel B open waters'},
    {'num': 457, 'diagram': 'DIAGRAM 37', 'hint': 'two steam vessels meeting one short blast'},
    {'num': 469, 'diagram': 'DIAGRAM 12', 'hint': 'vessel A towing vessel B meeting'},
]

def encode_image(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def ask_claude(photo_path, diagram_num, hint):
    img = encode_image(photo_path)
    prompt = f'Does this image show {diagram_num}? The question is about: {hint}. Reply YES or NO only.'
    payload = json.dumps({
        'model': 'claude-haiku-4-5-20251001',
        'max_tokens': 5,
        'messages': [{'role': 'user', 'content': [
            {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': img}},
            {'type': 'text', 'text': prompt}
        ]}]
    }).encode()
    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={'Content-Type': 'application/json', 'x-api-key': API_KEY, 'anthropic-version': '2023-06-01'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())
            return 'YES' in res['content'][0]['text'].upper()
    except Exception as e:
        print(f'  ERR: {e}')
        return False

# Load diagram photos
with open(IMAGES_MAP) as f:
    imap = json.load(f)
diagram_photos = [d['photo'] for d in imap['diagram_list']]
print(f'Diagram photos to check: {diagram_photos}')

# Load questions
with open(QUESTIONS_FILE) as f:
    questions = json.load(f)

# Match each diagram question to a photo
matches = {}
for dq in DIAGRAM_QUESTIONS:
    print(f"\nLooking for {dq['diagram']} (Q{dq['num']})...")
    for photo in diagram_photos:
        path = os.path.join(PHOTOS_DIR, photo)
        if not os.path.exists(path):
            continue
        print(f'  Checking {photo}...', end=' ')
        match = ask_claude(path, dq['diagram'], dq['hint'])
        if match:
            matches[dq['num']] = photo
            print(f'MATCH!')
            break
        else:
            print('no')
        time.sleep(0.3)
    if dq['num'] not in matches:
        print(f'  No match found for Q{dq["num"]}')

# Update questions.json
print(f'\nMatches found: {len(matches)}')
for qnum, photo in matches.items():
    print(f'  Q{qnum} -> {photo}')
    for q in questions:
        if q['num'] == qnum:
            q['image'] = f'photos/{photo}'
            break

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f'\nSaved to: {OUTPUT_FILE}')
