"""
RAG Retriever - retrieves compliance guidance from vector store.
POC 0: ChromaDB (local, zero cost)
POC 1: Azure AI Search (swap VECTOR_STORE env var - no code changes)
"""
from __future__ import annotations
from typing import Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class ComplianceRetriever:
      """
          Retrieves relevant compliance guidance for a given asset.
              Uses ChromaDB for POC 0 (local) or Azure AI Search for POC 1.
                  Swap is config-only via VECTOR_STORE env var.
                      """

    def __init__(self) -> None:
              self.settings = get_settings()
              self._client: chromadb.Client | None = None
              self._collection = None

    def _get_chroma_client(self) -> chromadb.Client:
              """Lazy-initialize ChromaDB client."""
              if self._client is None:
                            self._client = chromadb.PersistentClient(
                                              path=self.settings.chroma_path,
                                              settings=ChromaSettings(anonymized_telemetry=False),
                            )
                        return self._client

    def _get_collection(self):
              """Get or create ChromaDB collection."""
        if self._collection is None:
                      client = self._get_chroma_client()
                      self._collection = client.get_or_create_collection(
                          name=self.settings.chroma_collection_compliance,
                          metadata={"hnsw:space": "cosine"},
                      )
                  return self._collection

    async def retrieve_for_asset(
              self,
              asset_content: str,
              asset_metadata: dict[str, Any] | None = None,
              n_results: int = 5,
    ) -> str:
              """
                      Retrieve relevant compliance guidance for an asset.
                              Returns formatted context string for injection into agent prompts.
                                      """
        metadata = asset_metadata or {}

        if self.settings.vector_store == "chroma":
                      return await self._retrieve_chroma(asset_content, metadata, n_results)
elif self.settings.vector_store == "azure_search":
            return await self._retrieve_azure_search(asset_content, metadata, n_results)
else:
            logger.warning("unknown_vector_store", store=self.settings.vector_store)
            return ""

    async def _retrieve_chroma(
              self,
              query: str,
              metadata: dict[str, Any],
              n_results: int,
    ) -> str:
              """Retrieve from local ChromaDB (POC 0)."""
        try:
                      collection = self._get_collection()
                      doc_count = collection.count()

            if doc_count == 0:
                              logger.warning(
                                                    "chroma_collection_empty",
                                                    collection=self.settings.chroma_collection_compliance,
                                                    hint="Run: uv run python -m knowledge_base.document_loader",
                              )
                              return "No compliance guidance loaded. Please run the knowledge base setup."

            results = collection.query(
                              query_texts=[query[:500]],  # Limit query length
                              n_results=min(n_results, doc_count),
                              include=["documents", "metadatas", "distances"],
            )

            if not results["documents"] or not results["documents"][0]:
                              return ""

            # Format retrieved chunks with source citations
            context_parts = []
            for doc, meta, distance in zip(
                              results["documents"][0],
                              results["metadatas"][0],
                              results["distances"][0],
            ):
                              source = meta.get("source", "Unknown")
                              section = meta.get("section", "")
                              relevance = round(1 - distance, 3)  # Convert distance to similarity
                context_parts.append(
                                      f"[Source: {source} | Section: {section} | Relevance: {relevance}]\n{doc}"
                )

            return "\n\n---\n\n".join(context_parts)

except Exception as exc:
            logger.error("chroma_retrieval_failed", error=str(exc))
            return ""

    async def _retrieve_azure_search(
              self,
              query: str,
              metadata: dict[str, Any],
              n_results: int,
    ) -> str:
              """
                      Retrieve from Azure AI Search (POC 1).
                              TODO: Implement when migrating to POC 1.
                                      """
              # POC 1 implementation placeholder
              # from azure.search.documents.aio import SearchClient
        # from azure.core.credentials import AzureKeyCredential
        # client = SearchClient(
        #     endpoint=self.settings.azure_search_endpoint,
        #     index_name=self.settings.azure_search_index,
        #     credential=AzureKeyCredential(self.settings.azure_search_key),
        # )
        raise NotImplementedError("Azure AI Search retrieval: implement for POC 1")
