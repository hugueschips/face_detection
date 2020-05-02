import cv2

face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt2.xml')
cap = cv2.VideoCapture('./lab/video.mp4')

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    for x, y, w, h in face:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    if cv2.waitKey(1) == ord('q'):
        break
    cv2.imshow('video', frame)
cap.release()
cv2.destroyAllWindows()

