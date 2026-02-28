from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Blockchain
    sepolia_rpc_url: str
    contract_address: str
    backend_private_key: str
    
    # AI Service
    ai_service_url: str
    
    # IPFS
    pinata_api_key: str
    pinata_secret_key: str
    
    # App
    cors_origins: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
