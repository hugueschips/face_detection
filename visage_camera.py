import numpy as np
import cv2
import json
from time import sleep

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
            out.append(item.title())
    if out:
        out.insert(0, 'FACE')
    if text2:
        out.append('VOICE')
        out.append(text2.title())
    return(out)

def text_color(text):
    return (0, 255, 0)

class Bubble:
    def __init__(self, pt1, pt2, text, bg_color, font_face, scale, thickness, margin):
        if not text: return None
        self.bg_color = bg_color
        self.font_face = font_face
        self.scale = scale
        self.thickness = thickness
        self.margin = margin
        self.pt1 = pt1
        self.pt2 = pt2
        self.text = text
        self.p1 = self.get_p1()
        self.p2 = self.get_p2(text)
        self.triangle = self.get_triangle()
        self.x_text = self.p1[0]
        self.y_text = self.p2[1] + self.dy

    def get_p1(self):
        return (self.pt2[0] + 4 * (self.pt2[0] - self.pt1[0]), self.pt2[1])

    def get_p2(self, text):
        n_lines = len(text)
        longuest_line = max(text, key=len)
        txt_size = cv2.getTextSize(longuest_line, self.font_face, self.scale, self.thickness)
        self.dy = txt_size[0][1] + 3
        x1 = self.p1[0]
        y1 = self.p1[1]
        x2 = x1 + txt_size[0][0] + self.margin
        y2 = y1 - n_lines * self.dy - self.margin
        return (x2, y2)

    def get_triangle(self):
        def get_coord_on_line(t, x, y):
            return int(t * y + (1 - t) * x)
        x1 = self.p1[0]
        y1 = self.p1[1]
        x2 = self.p2[0]
        y2 = self.p2[1]
        p3 = [get_coord_on_line(2. / 7., x1, x2), y1]
        p4 = [x1, self.pt1[1]]
        p5 = [get_coord_on_line(3. / 7., x1, x2), y1]
        triangle = np.array([p3, p4, p5], np.int32)
        triangle = triangle.reshape((-1, 1, 2))
        return triangle

    def get_new_line_y(self):
        self.y_text += self.dy

def draw_label(img, text, pt1, pt2):
    bg_color = (0, 255, 0)
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = .8
    thickness = 2
    margin = 5
    b = Bubble(pt1, pt2, text, bg_color, font_face, scale, thickness, margin)
    cv2.rectangle(img, b.p1, b.p2, b.bg_color, b.thickness)
    cv2.fillConvexPoly(img, b.triangle, b.bg_color)
    for line in b.text:
        color = text_color(text)
        cv2.putText(img, line, (b.x_text, b.y_text), b.font_face, b.scale, color, 1, cv2.LINE_AA)
        b.get_new_line_y()

init_index_face = {key : 0 for key in emo_dic.keys()}
while True:
    ret, frame = cap.read()
    ts = cap.get(cv2.CAP_PROP_POS_MSEC)/1000.
    idx_voice = int(round(ts, 0))
    if idx_voice < len(aud_dic):
        voice_emotion = aud_dic[idx_voice]['emotion']
    for key, value in emo_dic.items():
        idx = get_index_list(ts, fps, value, init_index_face[key])
        if idx:
            init_index_face[key] = idx
            text = [emo_dic[key][idx]['emotion'], emo_dic[key][idx]['meaningful_expression']]
            x1, y1 = int(pos_dic[key][idx]['x1']), int(pos_dic[key][idx]['y1'])
            x2, y2 = int(pos_dic[key][idx]['x2']), int(pos_dic[key][idx]['y2'])
            text = get_text(text, voice_emotion)
            if text:
                draw_label(frame, text, (x1, y1), (x2, y2))

    if detect_faces:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        for x, y, w, h in face:
           cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    if debug:
        sleep(0.001)
        cv2.putText(frame, '{:.5}'.format(ts), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    if cv2.waitKey(1) == ord('q'):
        break
    cv2.imshow('video', frame)
cap.release()
cv2.destroyAllWindows()
