import cv2
import json
import numpy as np
import moviepy.editor as me
# from time import sleep

from geometry import Point, Rectangle
from bubble import Bubble

## Script options
debug = False
detect_faces = False
add_audio = True

if detect_faces:
    face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt2.xml')

## Import json files
with open('./lab/emotion.json', 'r') as f:
    emo_dic = json.load(f)
f.close()
with open('./lab/emotion_audio.json', 'r') as f:
    aud_dic = json.load(f)
f.close()
with open('./lab/position.json', 'r') as f:
    pos_dic = json.load(f)
f.close()

## Capture video
# videoClip = 0
inputvideo = './lab/video.mp4'
cap = cv2.VideoCapture(inputvideo)
fps = cap.get(cv2.CAP_PROP_FPS)

## Write video
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
outputvideo = 'output.avi'
out = cv2.VideoWriter(outputvideo, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, (frame_width, frame_height))

## Wrap some code chunks
def get_index_list(ts, fps, dic_list, init_range):
    """
    returns the index of the detected emotion matching timestamp ts
    """
    for i in range(init_range, len(dic_list)):
        if abs(ts - dic_list[i]['timestamp']) <= .9 / fps:
            return i

def get_text(text, text2, color_dic):
    """
    returns a clean list of strings to be written in the bubble and
    add new color in color_dic for each new text entry
    """

    def new_random_color():
        return (int(np.random.randint(0, 256)), int(np.random.randint(0, 256)), int(np.random.randint(0, 256)))

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


## Initiate variables
init_index_face = {key: 0 for key in emo_dic.keys()}
mouth_movement = {key: [0 for i in range(int(3*fps))] for key in emo_dic.keys()}
color_dic = {'FACE': (0, 0, 0), 'VOICE': (0, 0, 0)}

## Main loop
while True:
    ret, frame = cap.read()
    if frame is None:
        break
    ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.

    ## Get indices for each face
    idx_face = {}
    for key, value in emo_dic.items():
        idx_face[key] = get_index_list(ts, fps, value, init_index_face[key])
        if idx_face[key]:
            init_index_face[key] = idx_face[key]

    ## Identify speaker
    speaker_key = next(iter(pos_dic))
    mouth_std = 0.
    voice = False
    for key, value in pos_dic.items():
        if idx_face[key]:
            mouth_movement[key].append(value[idx_face[key]]['mouth'])
            val = np.std(mouth_movement[key][-int(fps):])
            if val > mouth_std:
                mouth_std = val
                speaker_key = key
                voice = True

    ## Get audio index and create an audio dic
    if voice:
        idx_voice = int(round(ts, 0))
        voice_dic = {key: None for key in pos_dic.keys()}
        if idx_voice < len(aud_dic):
            voice_dic[speaker_key] = aud_dic[idx_voice]['emotion']

    ## Store bubbles in a list called bubbles
    bubbles = []
    for key, idx in idx_face.items():
        if idx:
            text = [emo_dic[key][idx]['emotion'], emo_dic[key][idx]['meaningful_expression']]
            text = get_text(text, voice_dic[key], color_dic)
            pt1 = Point(int(pos_dic[key][idx]['x1']), int(pos_dic[key][idx]['y1']))
            pt2 = Point(int(pos_dic[key][idx]['x2']), int(pos_dic[key][idx]['y2']))
            if text:
                bubbles.append(Bubble(frame, pt1, pt2, text))

    ## Handle overlapping bubbles and draw all bubbles
    for i, bubble in enumerate(bubbles):
        for j, other_bubble in enumerate(bubbles[i + 1:]):
            if bubble.rec.do_overlap(other_bubble.rec):
                dxy, dim, sign = bubble.rec.min_overlap(other_bubble.rec)
                if dim == 0:
                    bubble.rec.shift_right(int(dxy/2+1) * sign)
                    other_bubble.rec.shift_right(-int(dxy/2+1) * sign)
                    bubble.avoid_eyes()
                elif dim == 1:
                    bubble.rec.shift_down(dxy * sign)
                    other_bubble.rec.shift_down(-dxy * sign)
                bubble.update_ac()
                other_bubble.update_ac()
        bubble.draw(frame, color_dic)

    ## Detect faces and draw rectangles around them
    if detect_faces:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        for x, y, w, h in face:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    ## Debug mode
    if debug and not add_audio:
        # sleep(0.01)
        cv2.putText(frame, '{:.5}'.format(ts), (10, 300), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    ## Wait for "q" key
    if cv2.waitKey(1) == ord('q'):
        break

    ## Write output file
    out.write(frame)

    ## Display frame
    cv2.imshow('video', frame)
cap.release()
out.release()
cv2.destroyAllWindows()

## Add audio to output file
if add_audio:
    audio = me.AudioFileClip(inputvideo)
    videoclip = me.VideoFileClip(outputvideo)
    videoclip = videoclip.set_audio(audio)
    videoclip.write_videofile('output2.avi', fps=fps, codec='png')
