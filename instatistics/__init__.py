from ._scraper import Scraper
from ._statistical import *

# para compatibilidad con tus mmds, luego se lo quitamos
# <!---
class Core:
    def __init__(self):
        self.Instadistics = Scraper

core = Core()
# -->
