import cv2
import time
from datetime import datetime    ##### a = datetime.now().strftime('%S')
import numpy as np
import mediapipe as mp

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

_, frame = cam.read()
frame = cv2.flip(frame, 1)
cv2.imshow('Morse Code', frame)

encod = {"._":"A", "_...":"B", "_._.":"C", "_..":"D", ".":"E",
	     ".._.":"F", "__.":"G", "....":"H", "..":"I", ".___":"J", 
	     "_._":"K", "._..":"L", "__":"M", "_.":"N", "___":"O",
	     ".__.":"P", "__._":"Q", "._.":"R", "...":"S", "_":"T",
	     ".._":"U", "..._":"V", ".__":"W", "_.._":"X", "_.__":"Y",
	     "__..":"Z"
}

FirstBlinkFlag = 0
SecondBlinkFlag = 0

EyeCloseFlag = 0

timeStampStart = 0
timeStampEnd = 0

breakFlag = 0
morse_code =  ""
START = 1

breakTimeStart = 0
breakTimeEnd = 0

timeStampDelayFlag = 0
breakTimeDelayFlag = 0

blinkFlag = 0

spaceFlag = 0
spaceFlagStart = 0
spaceFlagEnd = 0
spaceCheckFlag = 0
result = ""
while True:
	#print(f"\ntimeStampStart = {timeStampStart}, timeStampEnd = {timeStampEnd}, FirstBlinkFlag = {FirstBlinkFlag}, SecondBlinkFlag = {SecondBlinkFlag}")
	if(START == 1):
		time.sleep(2)
		START = 0

	#Press 'q' to exit the loop
	if cv2.waitKey(1) == ord('q'):
		break
	_, frame = cam.read()
	frame = cv2.flip(frame, 1)
	
	timeStampStart = int(float((datetime.now().strftime('%S.%f')[:-3])) * 1000)

	breakTimeStart = timeStampStart
	spaceFlagStart = timeStampStart
	
	if(FirstBlinkFlag == 1):
		#modulus for keeping it under 60000ms period only
		timeStampEnd = (timeStampStart + 300) % 60000
		timeStampDelayFlag = 1
		FirstBlinkFlag = 0
		
	if(timeStampStart >= timeStampEnd and timeStampDelayFlag):
		breakFlag = 1
		SecondBlinkFlag = 0
		breakTimeEnd = (breakTimeStart + 300) % 60000
		timeStampDelayFlag = 0
		#print("TimeStampStart == TimeStampEnd")
		
	if(breakFlag == 1 and (breakTimeStart >= breakTimeEnd) ):
		breakFlag = 0
		if(SecondBlinkFlag ==0):
			try:
				print(encod[morse_code])
				result = result + encod[morse_code]
				
				morse_code = ""
				
				spaceFlag = 1
				spaceCheckFlag = 1
				#print(f"\n Morse_Code_Empty = {morse_code}")
			except:
				print("No such code exists")
				morse_code = ""
				spaceFlag = 1
				spaceCheckFlag = 1
		#######################################################################		
	if(spaceFlag==1):
		spaceFlagEnd = (spaceFlagStart + 4000) % 60000
		spaceFlag = 0
		
	if(spaceFlagStart >= spaceFlagEnd and spaceCheckFlag==1):
		print("\nYou have said so far-")
		print(result)
		result = result + " "
		
		spaceCheckFlag = 0
	 
	rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	output = face_mesh.process(rgb_frame)

	landmark_points = output.multi_face_landmarks

	frame_h, frame_w, _ = frame.shape

	if landmark_points:
		landmarks = landmark_points[0].landmark
		## Right Eye ##
		right = [landmarks[374], landmarks[385]]
		for landmark in right:
			x = int(landmark.x * frame_w)
			y = int(landmark.y * frame_h)
			cv2.circle(frame, (x, y), 3, (0, 255, 0))
            
		## Left Eye ##
		left = [landmarks[145], landmarks[159]]
		for landmark in left:
			x = int(landmark.x * frame_w)
			y = int(landmark.y * frame_h)
			cv2.circle(frame, (x, y), 3, (0, 255, 255))
		
		#Eye Close 
		if (((left[0].y - left[1].y) < 0.01 and (right[0].y - right[1].y) < 0.01) and EyeCloseFlag == 0 ):
			EyeCloseFlag = 1
			breakFlag = 0
			spaceFlag = 0
			spaceCheckFlag = 0
			#print(f"Eyes Close Flag = 1, Eyes Close \n{(left[0].y - left[1].y)} or {(right[0].y - right[1].y)}")
		if(EyeCloseFlag == 1):
			if (((left[0].y - left[1].y) > 0.01 and (right[0].y - right[1].y) > 0.01) ):
				#print(f"Eyes Open Flag = 0, Eyes Open \n{(left[0].y - left[1].y)} or {(right[0].y - right[1].y)}")
				if(SecondBlinkFlag == 0):
					FirstBlinkFlag = 1
					morse_code = morse_code + "."
					#print(f" SecondBlinkFlag = 1, FirstBlinkFlag = 1, morseCode = {morse_code}")
					SecondBlinkFlag = 1
				else:
					morse_code = morse_code[:-1]
					morse_code = morse_code + "_"
					#Second_BlinkFlag = 0
					#print(f" SecondBlinkFlag = 0, FirstBlinkFlag = 0 , morseCode = {morse_code}")
					
				EyeCloseFlag = 0
				
	
	cv2.putText(frame, f"{np.abs((timeStampStart - timeStampEnd))}", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
	cv2.putText(frame, f"TimeStampStart = {timeStampStart}", (80, 80), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
	cv2.putText(frame, f"TimeStampEnd = {timeStampEnd}", (90, 90), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
	cv2.putText(frame, f"BreakTimeEnd = {breakTimeEnd}", (110, 110), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
	#cv2.putText(frame, f"SpaceTimeEnd = {spaceFlagEnd}", (130, 130), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 1)
	
	cv2.imshow('Morse Code', frame)
	#cv2.waitKey(1)

# Release objects
cam.release()
cv2.destroyAllWindows()
