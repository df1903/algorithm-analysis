"""
Cliente de Supabase para el proyecto.
Maneja la conexión y configuración.
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """
    Singleton para manejar la conexión a Supabase
    """
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa la conexión a Supabase"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL y SUPABASE_KEY deben estar en .env"
            )
        
        self._client = create_client(url, key)
        print("--> --> Conexión a Supabase establecida <-- <--")
    
    @property
    def client(self) -> Client:
        """Retorna el cliente de Supabase"""
        return self._client


# Instancia global
supabase_client = SupabaseClient()