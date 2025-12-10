"""
Content embedding service for the Physical AI & Humanoid Robotics textbook platform.
This module handles the creation and management of content embeddings for the RAG system.
"""
import asyncio
from typing import List, Optional, Tuple
from uuid import UUID
from openai import AsyncOpenAI
import numpy as np
from ..models.chapter import Chapter
from ..models.chapter_embedding import ChapterEmbedding, ChapterEmbeddingCreate
from ..services.vector_service import vector_service
from ..database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging


class EmbeddingService:
    """
    Service class for handling content embedding operations.
    """

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-ada-002"  # Default embedding model
        self.chunk_size = 512  # Number of tokens per chunk
        self.chunk_overlap = 50  # Number of overlapping tokens

    async def create_embeddings_for_chapter(self, chapter: Chapter) -> List[ChapterEmbedding]:
        """
        Create embeddings for all content in a chapter.
        """
        # First, delete existing embeddings for this chapter
        await vector_service.delete_embeddings_by_chapter(chapter.id)

        # Split chapter content into chunks
        content_chunks = self._chunk_content(chapter.content or "", chapter.id)

        embeddings = []
        for i, (chunk, context) in enumerate(content_chunks):
            # Create embedding for the chunk
            embedding_vector = await self._create_embedding(chunk)

            # Create ChapterEmbedding object
            chapter_embedding = ChapterEmbedding(
                chapter_id=chapter.id,
                content_chunk=chunk,
                embedding_vector=embedding_vector,
                chunk_index=i,
                context_window=context
            )

            # Add to vector database
            success = await vector_service.add_embedding(chapter_embedding)
            if success:
                embeddings.append(chapter_embedding)

        return embeddings

    async def update_embeddings_for_chapter(self, chapter: Chapter) -> List[ChapterEmbedding]:
        """
        Update embeddings for a chapter (delete old, create new).
        """
        return await self.create_embeddings_for_chapter(chapter)

    async def _create_embedding(self, text: str) -> List[float]:
        """
        Create a single embedding for the given text using OpenAI API.
        """
        try:
            response = await self.openai_client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error creating embedding: {str(e)}")
            # Return a zero vector as fallback
            return [0.0] * 1536  # Standard size for OpenAI embeddings

    def _chunk_content(self, content: str, chapter_id: UUID) -> List[Tuple[str, str]]:
        """
        Split content into overlapping chunks with context windows.
        """
        # Simple approach: split by paragraphs first, then by character count if too large
        paragraphs = content.split('\n\n')
        chunks = []

        for para in paragraphs:
            if len(para) <= self.chunk_size:
                # Add context from chapter title and section
                context = f"Chapter: {chapter_id} - {chapter_id}"
                chunks.append((para, context))
            else:
                # Split large paragraphs
                para_chunks = self._split_large_text(para)
                for chunk in para_chunks:
                    context = f"Chapter: {chapter_id} - {chapter_id}"
                    chunks.append((chunk, context))

        # Add overlapping context between chunks
        final_chunks = []
        for i, (chunk, context) in enumerate(chunks):
            # Add previous and next chunks as context if available
            full_context = context
            if i > 0:
                full_context += f" Previous: {chunks[i-1][0][:100]}..."
            if i < len(chunks) - 1:
                full_context += f" Next: {chunks[i+1][0][:100]}..."

            final_chunks.append((chunk, full_context))

        return final_chunks

    def _split_large_text(self, text: str) -> List[str]:
        """
        Split large text into smaller chunks of approximately chunk_size characters.
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # If we're not at the end, try to break at a sentence or paragraph boundary
            if end < len(text):
                # Look for a good breaking point near the end
                search_start = max(start, end - 100)  # Look back up to 100 chars
                break_point = -1

                # Try to break at paragraph boundary first
                for i in range(end, search_start, -1):
                    if text[i:i+2] == '\n\n':
                        break_point = i + 2
                        break

                # If no paragraph break, try sentence boundary
                if break_point == -1:
                    for i in range(end, search_start, -1):
                        if text[i] in '.!?':
                            break_point = i + 1
                            break

                # If no sentence break, try word boundary
                if break_point == -1:
                    for i in range(end, search_start, -1):
                        if text[i] == ' ':
                            break_point = i
                            break

                # If we found a good break point, use it
                if break_point != -1 and break_point > start:
                    end = break_point
                else:
                    # If no good break point, just break at the limit
                    end = min(end, len(text))

            chunks.append(text[start:end])
            start = end

        return chunks

    async def get_relevant_embeddings(
        self,
        query: str,
        chapter_id: Optional[UUID] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        Get relevant embeddings for a query.
        """
        # Create embedding for the query
        query_embedding = await self._create_embedding(query)

        # Search in vector database
        results = await vector_service.search_similar(
            query_vector=query_embedding,
            chapter_id=chapter_id,
            limit=limit
        )

        return results

    async def embed_entire_textbook(self, chapters: List[Chapter]) -> bool:
        """
        Create embeddings for all chapters in the textbook.
        """
        success_count = 0
        total_count = len(chapters)

        for chapter in chapters:
            try:
                await self.create_embeddings_for_chapter(chapter)
                success_count += 1
                print(f"Embedded chapter: {chapter.title}")
            except Exception as e:
                print(f"Failed to embed chapter {chapter.title}: {str(e)}")

        print(f"Successfully embedded {success_count}/{total_count} chapters")
        return success_count == total_count


# Create a global embedding service instance
embedding_service = EmbeddingService()