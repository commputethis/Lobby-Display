#!/usr/bin/env python3
"""
Standalone slideshow display service
Runs independently of the web server
"""
import pygame
import requests
import time
import os
from io import BytesIO
from PIL import Image

API_URL = 'http://localhost:5000/api/slideshow-data'
CHECK_INTERVAL = 5

class SlideshowDisplay:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.screen = None
        self.current_resolution = None
        self.current_rotation = 0
        self.images = []
        self.current_index = 0
        self.last_check = 0
        self.last_image_change = 0
        self.current_duration = 10
        
    def init_display(self, resolution, rotation):
        width, height = map(int, resolution.split('x'))
        
        if rotation in [90, 270]:
            width, height = height, width
            
        if self.screen is None or resolution != self.current_resolution or rotation != self.current_rotation:
            if self.screen:
                pygame.display.quit()
            
            flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
            
            try:
                self.screen = pygame.display.set_mode((width, height), flags)
            except:
                self.screen = pygame.display.set_mode((width, height))
            
            self.current_resolution = resolution
            self.current_rotation = rotation
    
    def load_image(self, image_data):
        try:
            if image_data['url'].startswith('http'):
                response = requests.get(image_data['url'], timeout=10)
                img = Image.open(BytesIO(response.content))
            else:
                path = image_data['url'].lstrip('/')
                if path.startswith('uploads/'):
                    data_dir = os.environ.get('LOBBY_DATA_DIR', '/opt/lobby-display')
                    path = os.path.join(data_dir, path)
                img = Image.open(path)
            
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            if self.current_rotation == 90:
                img = img.transpose(Image.ROTATE_270)
            elif self.current_rotation == 180:
                img = img.transpose(Image.ROTATE_180)
            elif self.current_rotation == 270:
                img = img.transpose(Image.ROTATE_90)
            
            screen_w, screen_h = self.screen.get_size()
            img_w, img_h = img.size
            
            scale = min(screen_w/img_w, screen_h/img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            py_image = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            x = (screen_w - new_w) // 2
            y = (screen_h - new_h) // 2
            
            return py_image, (x, y)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return None, (0, 0)
    
    def fetch_data(self):
        try:
            response = requests.get(API_URL, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"API error: {e}")
        return None
    
    def run(self):
        print("Slideshow display starting...")
        
        data = self.fetch_data()
        if data:
            self.init_display(data['settings']['resolution'], 
                            data['settings']['rotation'])
            self.images = data['images']
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.last_image_change = 0
            
            if current_time - self.last_check > CHECK_INTERVAL:
                new_data = self.fetch_data()
                if new_data:
                    if (new_data['settings']['resolution'] != self.current_resolution or
                        new_data['settings']['rotation'] != self.current_rotation):
                        self.init_display(new_data['settings']['resolution'],
                                        new_data['settings']['rotation'])
                    self.images = new_data['images']
                self.last_check = current_time
            
            if self.images:
                if current_time - self.last_image_change > self.current_duration:
                    self.current_index = (self.current_index + 1) % len(self.images)
                    self.last_image_change = current_time
                    self.preloaded_image = None
                
                current_image_data = self.images[self.current_index]
                self.current_duration = current_image_data.get('duration', 10)
                
                if not hasattr(self, 'preloaded_image') or self.preloaded_image is None:
                    self.preloaded_image, self.preloaded_pos = self.load_image(current_image_data)
                
                if self.preloaded_image:
                    self.screen.fill((0, 0, 0))
                    self.screen.blit(self.preloaded_image, self.preloaded_pos)
                    pygame.display.flip()
                else:
                    self.screen.fill((0, 0, 0))
                    pygame.display.flip()
            else:
                self.screen.fill((0, 0, 0))
                font = pygame.font.Font(None, 74)
                text = font.render("No Images", True, (128, 128, 128))
                text_rect = text.get_rect(center=self.screen.get_rect().center)
                self.screen.blit(text, text_rect)
                pygame.display.flip()
            
            clock.tick(30)
        
        pygame.quit()

if __name__ == '__main__':
    time.sleep(5)
    display = SlideshowDisplay()
    display.run()