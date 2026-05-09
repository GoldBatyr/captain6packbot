import os, sys, json, base64, time, urllib.request
from html.parser import HTMLParser

PHOTOS_DIR = '/Users/Batyr/Documents/exam_screens/photos'
HTML_FILE = '/Users/Batyr/Documents/exam_screens/messages.html'
OUTPUT_FILE = '/Users/Batyr/Documents/exam_screens/images_map.json'
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

if not API_KEY:
    print('ERROR: ANTHROPIC_API_KEY not set')
    sys.exit(1)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.cur = None
        self.cap = False
        self.buf = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get('class','')
        if tag == 'div' and 'default' in cls and 'message' in cls:
            self.cur = {'photos':[], 'text':''}
            self.messages.append(self.cur)
        if tag == 'a' and 'photo_wrap' in cls:
            h = d.get('href','')
            if h.startswith('photos/') and '_thumb' not in h and self.cur is not None:
                self.cur['photos'].append(h.replace('photos/',''))
        if tag == 'div' and 'text' in cls:
            self.cap = True
            self.buf = []
    def handle_endtag(self, tag):
        if tag == 'div' and self.cap:
            self.cap = False
            if self.cur:
                t = ' '.join(self.buf).strip()
                if t:
                    self.cur['text'] += ' ' + t
    def handle_data(self, data):
        if self.cap:
            self.buf.append(data.strip())

def check(path):
    with open(path,'rb') as f:
        data = base64.b64encode(f.read()).decode()
    payload = json.dumps({'model':'claude-haiku-4-5-20251001','max_tokens':10,'messages':[{'role':'user','content':[{'type':'image','source':{'type':'base64','media_type':'image/jpeg','data':data}},{'type':'text','text':'Reply ONE word: DIAGRAM if this image contains a nautical diagram, illustration, drawing or figure. TEXT_ONLY if it contains only text.'}]}]}).encode()
    req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload, headers={'Content-Type':'application/json','x-api-key':API_KEY,'anthropic-version':'2023-06-01'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())
            return 'DIAGRAM' in res['content'][0]['text'].upper()
    except Exception as e:
        print(f'  ERR: {e}')
        return False

print('Parsing messages.html...')
with open(HTML_FILE,'r',encoding='utf-8') as f:
    html = f.read()
p = Parser()
p.feed(html)
msgs = [m for m in p.messages if m['photos']]
print(f'Photos to check: {len(msgs)}')
results, diagrams = [], []
for i,msg in enumerate(msgs):
    for photo in msg['photos']:
        if '_thumb' in photo:
            continue
        path = os.path.join(PHOTOS_DIR, photo)
        if not os.path.exists(path):
            continue
        print(f'[{i+1}/{len(msgs)}] {photo}', end=' ')
        is_d = check(path)
        entry = {'photo':photo,'is_diagram':is_d,'context':msg['text'][:150]}
        results.append(entry)
        if is_d:
            diagrams.append(entry)
            print('-> DIAGRAM!')
        else:
            print('-> text')
        if (i+1) % 20 == 0:
            with open(OUTPUT_FILE,'w') as f:
                json.dump({'checked':i+1,'diagrams':len(diagrams),'diagram_list':diagrams,'all':results},f,ensure_ascii=False,indent=2)
            print(f'[saved: {len(diagrams)} diagrams]')
        time.sleep(0.2)
with open(OUTPUT_FILE,'w') as f:
    json.dump({'checked':len(results),'diagrams':len(diagrams),'diagram_list':diagrams,'all':results},f,ensure_ascii=False,indent=2)
print(f'\nDONE: {len(results)} checked, {len(diagrams)} diagrams found')
for d in diagrams:
    print(f'  {d["photo"]}')
print(f'Saved: {OUTPUT_FILE}')
