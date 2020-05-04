import cv2
import json
from time import sleep

debug = True
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
    if text[0] or text[1]:
        text = [item.title() for item in text]
        text.insert(0, 'FACE')
    else:
        text = []
    if text2:
        text.append('VOICE')
        text.append(text2)
    return(text)

def text_color(text):
    return (255, 255, 255)

def draw_label(img, text, pt1, pt2):
    bg_color = (255, 255, 255)
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = .8
    color = (36,255,12)
    thickness = 2
    margin = 5
    n_lines = len(text)
    txt_size = cv2.getTextSize('1234556789011', font_face, scale, thickness)
    dy = txt_size[0][1] + 3
    x1, y1 = pt2[0] + 4*(pt2[0]-pt1[0]), pt2[1]
    x2 = x1 + txt_size[0][0] + margin
    y2 = y1 - (n_lines+1)*dy - margin
    cv2.rectangle(img, (x1, y1), (x2, y2), bg_color, thickness)
    y = y2 + dy
    for line in text:
        color = text_color(text)
        cv2.putText(img, line, (x1, y), font_face, scale, color, 1, cv2.LINE_AA)
        y += dy





#exit()

init_range = {key : 0 for key in emo_dic.keys()}
while True:
    ret, frame = cap.read()
    ts = cap.get(cv2.CAP_PROP_POS_MSEC)/1000.
    for key, value in emo_dic.items():
        idx = get_index_list(ts, fps, value, init_range[key])
        if idx:
            init_range[key] = idx
            text = [emo_dic[key][idx]['emotion'], emo_dic[key][idx]['meaningful_expression']]
            x1, y1 = int(pos_dic[key][idx]['x1']), int(pos_dic[key][idx]['y1'])
            x2, y2 = int(pos_dic[key][idx]['x2']), int(pos_dic[key][idx]['y2'])
            text = get_text(text, '')
            if text:
                draw_label(frame, text, (x1, y1), (x2, y2))


    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #face = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    #for x, y, w, h in face:
    #   cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    if debug:
        sleep(0.01)
        cv2.putText(frame, '{:.5}'.format(ts), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    if cv2.waitKey(1) == ord('q'):
        break
    cv2.imshow('video', frame)
cap.release()
cv2.destroyAllWindows()
