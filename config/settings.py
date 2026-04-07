"""
Application settings using pydantic-settings.
All config driven by environment variables / .env file.
POC 0 → POC 1 transition: only .env changes, no code changes.
"""
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
            env_file=".env",
                    env_file_encoding="utf-8",
                            case_sensitive=False,
                                    extra="ignore",
                                        )

                                            # ── Environment ───────────────────────────────────────
                                                env: Literal["local", "poc", "prod", "test"] = "local"

                                                    # ── LLM (LiteLLM unified - swap env var for POC 0 → POC 1) ──
                                                        llm_model: str = "ollama/llama3"
                                                            llm_base_url: str = "http://localhost:11434"
                                                                llm_temperature: float = 0.0
                                                                    llm_max_tokens: int = 2048

                                                                        # Azure OpenAI (POC 1 - set these in .env)
                                                                            azure_api_key: str | None = None
                                                                                azure_api_base: str | None = None
                                                                                    azure_api_version: str = "2024-02-01"

                                                                                        # ── Embeddings ────────────────────────────────────────
                                                                                            embedding_model: str = "ollama/nomic-embed-text"
                                                                                                embedding_base_url: str = "http://localhost:11434"

                                                                                                    # ── Vector Store ──────────────────────────────────────
                                                                                                        vector_store: Literal["chroma", "azure_search"] = "chroma"
                                                                                                        
                                                                                                            # ChromaDB (POC 0)
                                                                                                                chroma_path: str = "./data/chroma_db"
                                                                                                                    chroma_collection_compliance: str = "compliance_docs"
                                                                                                                    
                                                                                                                        # Azure AI Search (POC 1)
                                                                                                                            azure_search_endpoint: str | None = None
                                                                                                                                azure_search_key: str | None = None
                                                                                                                                    azure_search_index: str = "compliance-docs"
                                                                                                                                    
                                                                                                                                        # ── Database ──────────────────────────────────────────
                                                                                                                                            database_url: str = "sqlite+aiosqlite:///./data/compliance.db"
                                                                                                                                            
                                                                                                                                                # ── Redis ─────────────────────────────────────────────
                                                                                                                                                    redis_url: str = "redis://localhost:6379/0"
                                                                                                                                                    
                                                                                                                                                        # ── API ───────────────────────────────────────────────
                                                                                                                                                            api_host: str = "0.0.0.0"
                                                                                                                                                                api_port: int = 8000
                                                                                                                                                                    api_reload: bool = True
                                                                                                                                                                        api_secret_key: str = "change-me-in-production"
                                                                                                                                                                        
                                                                                                                                                                            # ── Compliance Review ─────────────────────────────────
                                                                                                                                                                                review_domains: str = "brand,legal,accessibility,global_readiness,product_marketing"
                                                                                                                                                                                    escalation_threshold: Literal["high", "medium", "low"] = "high"
                                                                                                                                                                                    
                                                                                                                                                                                        # RAG chunking
                                                                                                                                                                                            chunk_size: int = 512
                                                                                                                                                                                                chunk_overlap: int = 50
                                                                                                                                                                                                
                                                                                                                                                                                                    # ── Logging ───────────────────────────────────────────
                                                                                                                                                                                                        log_level: str = "INFO"
                                                                                                                                                                                                            log_format: Literal["json", "console"] = "json"
                                                                                                                                                                                                            
                                                                                                                                                                                                                @property
                                                                                                                                                                                                                    def review_domain_list(self) -> list[str]:
                                                                                                                                                                                                                            return [d.strip() for d in self.review_domains.split(",")]
                                                                                                                                                                                                                            
                                                                                                                                                                                                                                @property
                                                                                                                                                                                                                                    def is_local(self) -> bool:
                                                                                                                                                                                                                                            return self.env == "local"
                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                            @lru_cache
                                                                                                                                                                                                                                            def get_settings() -> Settings:
                                                                                                                                                                                                                                                """Cached settings instance - single source of truth."""
                                                                                                                                                                                                                                                    return Settings()
