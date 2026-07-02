# import pyttsx3
# import subprocess
import os
import pygame

	    
def run_voic(num):
	file_path = "./voice"
	# subprocess.run(['aplay -r 44100', os.path.join(file_path,f"{num}.wav")])


	pygame.mixer.init()
	pygame.mixer.music.load(os.path.join(file_path,f"{num}.mp3"))
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy():
		pygame.time.Clock().tick(10)
	pygame.mixer.quit()

	
if __name__=="__main__":
	run_voic(3)
