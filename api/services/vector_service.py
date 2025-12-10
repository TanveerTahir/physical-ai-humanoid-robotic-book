"""
Vector service for the Physical AI & Humanoid Robotics textbook platform.
This module handles Qdrant vector database operations for the RAG system.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import numpy as np
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from ..database import get_vector_db_client
from ..models.chapter_embedding import ChapterEmbedding


class VectorService:
    """
    Service class for handling vector database operations with Qdrant.
    """

    def __init__(self):
        self.collection_name = "textbook_embeddings"
        self.client = get_vector_db_client()
        self.vector_size = 1536  # Default size for OpenAI embeddings

    async def initialize_collection(self):
        """
        Initialize the embeddings collection in Qdrant if it doesn't exist.
        """
        try:
            # Check if collection exists
            await self.client.get_collection(self.collection_name)
        except:
            # Create collection if it doesn't exist
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    async def add_embedding(self, embedding: ChapterEmbedding) -> bool:
        """
        Add a single embedding to the collection.
        """
        await self.initialize_collection()

        point = PointStruct(
            id=str(embedding.id),
            vector=embedding.embedding_vector,
            payload={
                "chapter_id": str(embedding.chapter_id),
                "content_chunk": embedding.content_chunk,
                "chunk_index": embedding.chunk_index,
                "context_window": embedding.context_window,
                "created_at": embedding.created_at.isoformat() if embedding.created_at else None
            }
        )

        operation_info = await self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return operation_info.status == models.UpdateStatus.COMPLETED

    async def add_embeddings_batch(self, embeddings: List[ChapterEmbedding]) -> bool:
        """
        Add multiple embeddings to the collection in a batch.
        """
        await self.initialize_collection()

        points = []
        for embedding in embeddings:
            point = PointStruct(
                id=str(embedding.id),
                vector=embedding.embedding_vector,
                payload={
                    "chapter_id": str(embedding.chapter_id),
                    "content_chunk": embedding.content_chunk,
                    "chunk_index": embedding.chunk_index,
                    "context_window": embedding.context_window,
                    "created_at": embedding.created_at.isoformat() if embedding.created_at else None
                }
            )
            points.append(point)

        operation_info = await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return operation_info.status == models.UpdateStatus.COMPLETED

    async def search_similar(
        self,
        query_vector: List[float],
        chapter_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings to the query vector.
        """
        # Prepare filters
        filters = []
        if chapter_id:
            filters.append(models.FieldCondition(
                key="chapter_id",
                match=models.MatchValue(value=str(chapter_id))
            ))

        filter_obj = models.Filter(must=filters) if filters else None

        # Perform search
        search_results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=filter_obj,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        # Format results
        results = []
        for hit in search_results:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            })

        return results

    async def get_embedding_by_id(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific embedding by its ID.
        """
        records = await self.client.retrieve(
            collection_name=self.collection_name,
            ids=[embedding_id],
            with_payload=True,
            with_vectors=True
        )

        if records:
            record = records[0]
            return {
                "id": record.id,
                "vector": record.vector,
                "payload": record.payload
            }

        return None

    async def delete_embedding(self, embedding_id: str) -> bool:
        """
        Delete an embedding by its ID.
        """
        operation_info = await self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(points=[embedding_id])
        )

        return operation_info.status == models.UpdateStatus.COMPLETED

    async def delete_embeddings_by_chapter(self, chapter_id: UUID) -> bool:
        """
        Delete all embeddings associated with a specific chapter.
        """
        operation_info = await self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="chapter_id",
                            match=models.MatchValue(value=str(chapter_id))
                        )
                    ]
                )
            )
        )

        return operation_info.status == models.UpdateStatus.COMPLETED

    async def update_embedding(self, embedding: ChapterEmbedding) -> bool:
        """
        Update an existing embedding.
        """
        # First delete the old embedding
        await self.delete_embedding(str(embedding.id))

        # Then add the updated one
        return await self.add_embedding(embedding)

    async def get_all_embeddings_for_chapter(self, chapter_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all embeddings for a specific chapter.
        """
        records = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="chapter_id",
                        match=models.MatchValue(value=str(chapter_id))
                    )
                ]
            ),
            limit=10000,  # Adjust as needed
            with_payload=True,
            with_vectors=True
        )

        results = []
        for record in records[0]:  # records is a tuple (records, next_page_offset)
            results.append({
                "id": record.id,
                "vector": record.vector,
                "payload": record.payload
            })

        return results


# Create a global vector service instance
vector_service = VectorService()