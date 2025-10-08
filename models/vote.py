from datetime import datetime

class Vote:
    def __init__(self, id=None, candidato_id=None, fecha_hora=None, identificador_votante=None):
        """
        Inicializa un objeto Vote
        
        :param id: ID del voto en la base de datos
        :param candidato_id: ID del candidato por el que se votó
        :param fecha_hora: Fecha y hora del voto
        :param identificador_votante: Identificador único del votante (opcional)
        """
        self.id = id
        self.candidato_id = candidato_id
        self.fecha_hora = fecha_hora or datetime.now()
        self.identificador_votante = identificador_votante
    
    def __str__(self):
        return f"Voto para candidato {self.candidato_id} el {self.fecha_hora}"
    
    def to_dict(self):
        """Convierte el objeto a un diccionario"""
        return {
            'id': self.id,
            'candidato_id': self.candidato_id,
            'fecha_hora': self.fecha_hora,
            'identificador_votante': self.identificador_votante
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Vote desde un diccionario"""
        return cls(
            id=data.get('id'),
            candidato_id=data.get('candidato_id'),
            fecha_hora=data.get('fecha_hora'),
            identificador_votante=data.get('identificador_votante')
        )