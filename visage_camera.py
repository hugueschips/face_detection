import cv2
import json
import numpy as np
from time import sleep
from geometry import Point, Rectangle
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

## Retrieve all emotions
emo1 = set([item['emotion'].capitalize() for item in aud_dic])
emo2 = []
for key, value in emo_dic.items():
    for item in value:
        if item['emotion']:
            emo2.append(item['emotion'].capitalize())
        if item['meaningful_expression']:
            emo2.append(item['meaningful_expression'].capitalize())
emo2 = set(emo2)
emotion_list = [emo1.union(emo2)]



face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt2.xml')
cap = cv2.VideoCapture('./lab/video.mp4')
#cap = cv2.VideoCapture(0)
fps = cap.get(cv2.CAP_PROP_FPS)

def get_index_list(ts, fps, dic_list, init_range):
    for i in range(init_range, len(dic_list)):
        if abs(ts - dic_list[i]['timestamp']) <= .9/fps:
            return i

def get_text(text, text2, color_dic):
    def new_random_color():
        return (int(np.random.randint(0, 256)), int(np.random.randint(0, 256)), int(np.random.randint(0, 256)) )
    out = []
    for item in text:
        if item:
            out.append(item.capitalize())
            if item.capitalize() not in color_dic.keys():
                color_dic[item.capitalize()] = new_random_color()
    if out:
        out.insert(0, 'FACE')
    if text2:
        out.append('VOICE')
        out.append(text2.capitalize())
        if text2.capitalize() not in color_dic.keys():
            color_dic[text2.capitalize()] = new_random_color()
    return out

init_index_face = {key : 0 for key in emo_dic.keys()}
mouth_movement = {key : [0 for i in range(int(fps))] for key in emo_dic.keys()}
color_dic = {'FACE' : (0,0,0), 'VOICE': (0,0,0)}
while True:
    ret, frame = cap.read()
    if frame is None:
        break
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
            mouth_movement[key].append(value[idx_face[key]]['mouth'])
            val = np.std(mouth_movement[key][-int(fps):])
            if val > mouth_size:
                mouth_size = val
                biggest_mouth_key = key
                voice = True

    ## Get audio index and create an audio dic
    if voice:
        idx_voice = int(round(ts, 0))
        voice_dic = {key : None for key in pos_dic.keys()}
        if idx_voice < len(aud_dic):
            voice_dic[biggest_mouth_key] = aud_dic[idx_voice]['emotion']

    ## Draw bubbles
    bubbles = []
    for key, idx in idx_face.items():
        if idx:
            text = [emo_dic[key][idx]['emotion'], emo_dic[key][idx]['meaningful_expression']]
            text = get_text(text, voice_dic[key], color_dic)
            pt1 = Point(int(pos_dic[key][idx]['x1']), int(pos_dic[key][idx]['y1']))
            pt2 = Point(int(pos_dic[key][idx]['x2']), int(pos_dic[key][idx]['y2']))
            if text:
                bubbles.append(Bubble(frame, pt1, pt2, text))
    for i, bubble in enumerate(bubbles):
        for j, other_bubble in enumerate(bubbles[i+1:]):
            if bubble.rec.do_overlap(other_bubble.rec):
                print(bubble.rec)
                print(other_bubble.rec)
                dxy, dim, sign = bubble.rec.min_overlap(other_bubble.rec)
                print(dxy, dim, sign)
                if dim == 0:
                    bubble.rec.shift_right(dxy * sign)
                    other_bubble.rec.shift_right(-dxy * sign)
                elif dim == 1:
                    bubble.rec.shift_down(dxy * sign)
                    other_bubble.rec.shift_down(-dxy * sign)
                bubble.update_ac()
                other_bubble.update_ac()
        bubble.draw(frame, color_dic)

    ## Detect faces
    if detect_faces:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        for x, y, w, h in face:
           cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    ## Debug mode
    if debug:
        #sleep(0.001)
        cv2.putText(frame, '{:.5}'.format(ts), (10, 300), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    ## Wait for "q" key
    if cv2.waitKey(1) == ord('q'):
        break

    cv2.imshow('video', frame)
cap.release()
cv2.destroyAllWindows()
