# model_loader.py
import torch
from pathlib import Path

class YOLOModel:
    _instance = None
    _model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        folder_path = Path('C:/Users/jairg/Desktop/CacaoAPP/cacaoApp/model/best.pt')  # Asegúrate de que la ruta sea correcta y accesible en producción
        self._model = torch.hub.load('ultralytics/yolov5',  'custom' , path=folder_path, force_reload=True)

    def get_model(self):
        return self._model
