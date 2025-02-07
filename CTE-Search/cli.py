import platform
import os 
from pynput import keyboard
from typing import Callable,Any,Optional
def clear():

    if "windows" in platform.platform().lower():
        os.system("cls")
    else:
        os.system("clear")

class Menu:
    options:list[str]
    max_index:int

    def __init__(self):
        raise NotImplementedError("Menu is a abstract class")
    def __call__(self,index:int):
        for x in range(len(self.options)):
            if index == x:
                print(f"{self.options[x]} <#####")
            else:
                print(self.options[x])
    def on_option(self,index:int)->Optional['Menu']:# If a menu is returned it will load that Menu 
        raise NotImplementedError("Menu is a abstract class")
class MainMenu(Menu):
    def __init__(self):
        self.options = ["hello world","this kind of works","does it though"]
        self.max_index = len(self.options) -1
    def on_option(self, index):
        return print(self.options[index])
class Interface:
    index:int
    current_menu:Menu
    def __init__(self):
        self.index = 0
        self.current_menu = MainMenu() 
    def __re_render(self):
        clear()
        self.current_menu(self.index)
    def __on_press(self,key):
        try:
            if key == keyboard.Key.up:
                if not self.index == 0:
                    self.index-=1
                    self.__re_render()
            elif key == keyboard.Key.down:
                if not self.index == self.current_menu.max_index:
                    self.index+=1
                    self.__re_render()
            elif key == keyboard.Key.enter:
                menu = self.current_menu.on_option(self.index)
                if isinstance(menu,Menu):
                    self.index = 0
                    self.current_menu = menu
        except AttributeError as e:
            print("got error")
    def __on_release(self,key):
        if key == keyboard.Key.esc:
            clear()
            return False
    def run(self):
        with keyboard.Listener(on_press=self.__on_press,on_release=self.__on_release) as listener:
            self.__re_render()
            listener.join()
    