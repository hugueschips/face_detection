import cv2
import json
from time import sleep
from bubble import Bubble

debug = True
detect_faces = False

with open('./lab/emotion.json', 'r') as f:
    emo_dic = json.load(f)
f.close()
with open('./lab/emotion_audio.json', 'r') as f:
    aud_dic = json.load(f)
f.close()
with open('./lab/position.json', 'r') as f:
    pos_dic = json.load(f)
f.close()

face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt2.xml')
cap = cv2.VideoCapture('./lab/video.mp4')
#cap = cv2.VideoCapture(0)
fps = cap.get(cv2.CAP_PROP_FPS)

def get_index_list(ts, fps, dic_list, init_range):
    for i in range(init_range, len(dic_list)):
        if abs(ts - dic_list[i]['timestamp']) <= .9/fps:
            return i

def get_text(text, text2):
    out = []
    for item in text:
        if item:
            out.append(item.capitalize())
    if out:
        out.insert(0, 'FACE')
    if text2:
        out.append('VOICE')
        out.append(text2.capitalize())
    return(out)

init_index_face = {key : 0 for key in emo_dic.keys()}
while True:
    ret, frame = cap.read()
    ts = cap.get(cv2.CAP_PROP_POS_MSEC)/1000.

    ## Get indices for each face
    idx_face = {}
    for key, value in emo_dic.items():
        idx_face[key] = get_index_list(ts, fps, value, init_index_face[key])
        if idx_face[key]:
            init_index_face[key] = idx_face[key]

    ## Get face with biggest mouth
    biggest_mouth_key = next(iter(pos_dic))
    mouth_size = 0.
    voice = False
    for key, value in pos_dic.items():
        if idx_face[key]:
            if value[idx_face[key]]['mouth'] > mouth_size:
                mouth_size = value[idx_face[key]]['mouth']
                biggest_mouth_key = key
                voice = True

    ## Get audio index and create an audio dic
    if voice:
        idx_voice = int(round(ts, 0))
        voice_dic = {key : None for key in pos_dic.keys()}
        if idx_voice < len(aud_dic):
            voice_dic[biggest_mouth_key] = aud_dic[idx_voice]['emotion']

    ## Draw bubbles
    bg_color = (0, 255, 0)
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = 2 * frame.shape[1]/1280.
    thickness = 4
    margin = 20
    for key, idx in idx_face.items():
        if idx:
            text = [emo_dic[key][idx]['emotion'], emo_dic[key][idx]['meaningful_expression']]
            x1, y1 = int(pos_dic[key][idx]['x1']), int(pos_dic[key][idx]['y1'])
            x2, y2 = int(pos_dic[key][idx]['x2']), int(pos_dic[key][idx]['y2'])
            text = get_text(text, voice_dic[key])
            if text:
                bubble = Bubble(frame, (x1, y1), (x2, y2), text, bg_color, font_face, scale, thickness, margin)
                bubble.uncrop()
                bubble.draw(frame)

    ## Detect faces
    if detect_faces:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        for x, y, w, h in face:
           cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    ## Debug mode
    if debug:
        sleep(0.001)
        cv2.putText(frame, '{:.5}'.format(ts), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    ## Wait for "q" key
    if cv2.waitKey(1) == ord('q'):
        break

    cv2.imshow('video', frame)
cap.release()
cv2.destroyAllWindows()
