import cv2
import numpy as np
import pyaudio
import audioop

# Constants for ball properties
BALL_RADIUS = 50
BALL_COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 255)]  # france colors

# set up webcam
cap = cv2.VideoCapture(0)
# 0 represents the default webcam device

# set up pyaudio
audio = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

_, prev_frame = cap.read()
prev_light_intensity = 0
prev_motion_intensity = 0

# Calculate motion intensity
def calculate_motion_intensity(frame, prev_frame):

    # Convert frames to grayscale

    #The grayscale conversion is used in the code to simplify the image processing operations that follow.
    # By converting the frames to grayscale, we reduce the complexity of the data and focus only on the intensity values,
    # which are sufficient for calculating motion intensity and light intensity.


    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Calculate the absolute difference between frames
    diff = cv2.absdiff(frame_gray, prev_frame_gray)

    # Calculate the motion intensity as the mean of the absolute difference for accuracy
    motion_intensity = np.mean(diff)

    return motion_intensity

# Calculate light intensity
def calculate_light_intensity(frame):
    # Convert frames to grayscale
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate the average pixel value as light intensity
    light_intensity = np.mean(frame_gray)

    return light_intensity

# Calculate sound intensity
def calculate_sound_intensity():
    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)  # Calculate Root Mean Square (RMS) value
    sound_intensity = rms / 1500  # Adjust the scaling factor based on the sound intensity
    return sound_intensity

# Generate visuals based on sensor intensities
def generate_visuals(motion_intensity, light_intensity, sound_intensity):
    # Create a black background image
    visuals = np.zeros((800, 1200, 3), dtype=np.uint8)

    # Adjust ball position based on motion intensity
    ball1_radius = BALL_RADIUS - int(motion_intensity * 0.2)
    ball1_position = (200, int(300 + motion_intensity * 0.4))


    # Pulse ball3 based on sound beat
    ball3_radius = BALL_RADIUS + int(sound_intensity * 50)

    # create three balls
    for i, color in enumerate(BALL_COLORS):
        if i == 0:
            center = ball1_position
            radius = BALL_RADIUS
        elif i == 1:
            center = (600, 300)
            radius = BALL_RADIUS
            color = (0, 0, int(light_intensity))  # Change color based on light intensity
        else:
            center = (1000, 300)
            radius = ball3_radius
        cv2.circle(visuals, center, radius, color, -1)

    return visuals



while True:
    ret, frame = cap.read()  # Read the current frame

    # Calculate motion intensity
    motion_intensity = calculate_motion_intensity(frame, prev_frame)

    # Calculate light intensity
    light_intensity = calculate_light_intensity(frame)

    # Calculate sound intensity
    sound_intensity = calculate_sound_intensity()

    visuals = generate_visuals(motion_intensity, light_intensity, sound_intensity)
    cv2.imshow('Demo', visuals)

    prev_frame = frame.copy()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#stop libraries
cap.release()
cv2.destroyAllWindows()
stream.stop_stream()
stream.close()
audio.terminate()