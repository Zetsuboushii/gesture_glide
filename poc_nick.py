def cam():

    import cv2
    import mediapipe as mp

    print("Start")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()


    while True:
        success, frame = cap.read()
        if success:
            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(RGB_frame)
            if result.multi_hand_landmarks:
                for hand_landmark in result.multi_hand_landmarks:
                    print(hand_landmark)
                    mp_drawing.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)
            cv2.imshow('mein frame', frame)
            if cv2.waitKey(1) == ord('q'):
                break
        else:
            print("knecht")
            break

    cv2.destroyAllWindows()

def switching():
    from pywinauto import application

    app = application.Application()
    app2 = application.Application()
    app.start("Notepad.exe")
    app2.start(r"C:\Users\nickb\Downloads\Gluecksrad\Gluecksrad.bat")

    # switch to Notepad
    app.UntitledNotepad.SetFocus()
    # select and copy next line (this is not the only way, just for example)
    app.UntitledNotepad.Edit.TypeKeys('{DOWN}{HOME}+{END}^c')

    # switch to your app
    app2.SpeakEditWindowTitle.SetFocus()
    # paste somewhere

print("do selected")
cam()