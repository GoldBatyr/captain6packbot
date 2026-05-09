import json
data = json.load(open('/Users/Batyr/Documents/exam_screens/questions.json', encoding='utf-8'))
def get_topic(q):
    text = (q['en_q'] + ' ' + ' '.join(q['en_options'])).lower()
    if any(w in text for w in ['narrow channel','narrow waterway','bend in a channel','vessel in a narrow','crossing a narrow','overtaking in a narrow','pass in a narrow','navigating a narrow']):
        return 'narrow_channels'
    if any(w in text for w in ['restricted visibility','in fog','in reduced visibility']):
        return 'visibility'
    if any(w in text for w in ['distress','mayday','emergency signal','rescue','flare','epirb','liferaft','pan-pan','sos']):
        return 'distress'
    if any(w in text for w in ['whistle','blast','fog signal','horn','bell','sound signal','siren']):
        return 'sound_signals'
    if any(w in text for w in ['light','shape','cone','ball','diamond','cylinder','masthead','sidelight','sternlight','all-round','lantern','anchor light','strobe','flashing']):
        return 'lights_shapes'
    if any(w in text for w in ['chart','publication','notice to mariners','coast pilot','tide table','depth sounding','projection','mercator','buoy position','chart no','nautical chart','iala','buoy color','buoy system','lateral mark','special mark']):
        return 'charts'
    if any(w in text for w in ['weather','wind','storm','hurricane','front','barometer','cloud','temperature','squall','isobar','beaufort','gale']):
        return 'weather'
    if any(w in text for w in ['true','variance','deviation','compass','magnetic','bearing','course to steer','knot','travel','arrive','distance','nm at','great circle','rhumb','meridian','parallel','longitude','latitude','dead reckoning','fix','plotting']):
        return 'navigation'
    if any(w in text for w in ['block','tackle','rigging','chafing','heaving','hawser','mooring','dock line','docking','anchor','anchoring','ground tackle','windlass','capstan','cleat','bollard','fender','spring line']):
        return 'seamanship'
    if any(w in text for w in ['tidal','tidal current','tide','slack water','moon','ebb','flood tide','neap','spring tide','tidal day','current flow']):
        return 'tides_currents'
    if any(w in text for w in ['stand-on','give-way','head-on','crossing situation','overtaking vessel','meeting vessel','collision','right of way','safe speed','lookout','risk of collision']):
        return 'steering_rules'
    return 'steering_rules'
for q in data:
    q['topic'] = get_topic(q)
topics = {}
for q in data:
    topics[q['topic']] = topics.get(q['topic'], 0) + 1
for t,c in sorted(topics.items()):
    print(t + ': ' + str(c))
json.dump(data, open('/Users/Batyr/Documents/exam_screens/questions.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('Saved!')
