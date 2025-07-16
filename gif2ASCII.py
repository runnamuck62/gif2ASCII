import cv2
import numpy as np
import os
from PIL import Image, ImageFont, ImageDraw

#Process GIF frames and return all frame values and GIF FPS
def process_frames(file):
    #Get all the Frames from the GIF, resize them, and convert to grayscale
    gif = cv2.VideoCapture(file)
    fps = gif.get(cv2.CAP_PROP_FPS)
    ms_per_frame = 1000 / fps
    frames = []
    while True:
        ret, frame = gif.read()
        if not ret:
            break

        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        original_height, original_width = grayscale.shape[:2]
        new_width = 75
        aspect_ratio = new_width / original_width
        new_height = int(original_height * aspect_ratio)
        resized = cv2.resize(grayscale, (new_width * 2, new_height))
        frames.append(resized)
    gif.release()
    return frames, ms_per_frame

#Convert grayscale value to ASCII char
def pixel_to_char(value):
    chars = [
        "$","8","#","h","p","Z","L","Y","v","r","/","/",")","[","_",
        ">","I","^"
    ]
    idx = min(value // 15, len(chars) - 1)
    return chars[idx]

#Convert grayscale frames to ASCII art
def convert_to_ascii(frames):
    text_frames = []
    for frame in frames:
        pixels = []
        for row in frame:
            row_pixels = []
            for char in row:
               character = pixel_to_char(char)
               row_pixels.append(character)
            pixels.append(row_pixels)
        text_frames.append(pixels)
    return text_frames

#Draw ASCII text to image for GIF creation    
def convert_to_img(text_frames):
    
    padding_top = 5
    padding_bottom = 5
    padding_left = 5
    padding_right = 5

    gif_frames = []
       
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FONT_PATH = os.path.join(BASE_DIR, "fonts", "UbuntuMono-B.ttf")

    fnt = ImageFont.truetype(FONT_PATH, 9)

    for image in text_frames:
        final_image = '\n'.join(''.join(row) for row in image)

        # Measure exact text block
        temp_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(temp_img)
        bbox = draw.multiline_textbbox(
            (0, 0),
            final_image,
            font=fnt,
            spacing=0
        )
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        #Use exact text block dimensions for canvas with padding
        img_width = text_width + padding_left + padding_right
        img_height = text_height + padding_top + padding_bottom

        #Draw images to Canvas
        img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.multiline_text(
            (padding_left, padding_top),
            final_image,
            font=fnt,
            fill=(0, 0, 0),
            spacing=0
        )
        gif_frames.append(img)

    return gif_frames

#Convert all frames to gif file  
def save_as_gif(gif_frames, ms_per_frame, output): 
    frame_one = gif_frames[0]
    frame_one.save(output, format="GIF", append_images=gif_frames[1:], save_all=True, duration=ms_per_frame, loop = 0)

