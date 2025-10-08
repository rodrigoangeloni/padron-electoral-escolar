class Candidate:
    def __init__(self, id=None, nombre="", posicion="", foto="assets/images/default_candidate.jpg"):
        """
        Inicializa un objeto Candidate
        
        :param id: ID del candidato en la base de datos
        :param nombre: Nombre completo del candidato
        :param posicion: Posición a la que se postula ('directora' o 'vice_directora')
        :param foto: Ruta a la imagen del candidato
        """
        self.id = id
        self.nombre = nombre
        self.posicion = posicion
        self.foto = foto
    
    def __str__(self):
        return f"{self.nombre} - {self.posicion}"
    
    def to_dict(self):
        """Convierte el objeto a un diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'posicion': self.posicion,
            'foto': self.foto
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Candidate desde un diccionario"""
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre'),
            posicion=data.get('posicion'),
            foto=data.get('foto')
        )