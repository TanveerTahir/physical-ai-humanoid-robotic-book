# Data Model for Physical AI & Humanoid Robotics Textbook

## Overview
This document defines the core data entities and relationships for the Physical AI & Humanoid Robotics textbook platform, including user management, content organization, personalization, and AI integration features.

## Core Entities

### 1. User
**Description**: Platform users with authentication and personalization data

**Fields**:
- `id` (string, UUID): Unique user identifier
- `email` (string): User's email address
- `name` (string): User's display name
- `createdAt` (timestamp): Account creation date
- `lastLoginAt` (timestamp): Last login timestamp
- `preferences` (JSON): User preferences and settings
- `learningPath` (JSON): Current learning progress and path
- `personalizationProfile` (JSON): Personalization settings and preferences

**Relationships**:
- One-to-Many: User → UserProgress
- One-to-Many: User → UserInteraction

### 2. Chapter
**Description**: Individual textbook chapters with content and metadata

**Fields**:
- `id` (string, UUID): Unique chapter identifier
- `title` (string): Chapter title
- `slug` (string): URL-friendly identifier
- `section` (string): Section identifier (A-H)
- `number` (integer): Chapter number within section
- `content` (text): Chapter content in MDX format
- `createdAt` (timestamp): Creation timestamp
- `updatedAt` (timestamp): Last update timestamp
- `gpuNotes` (text): GPU workstation deployment notes
- `jetsonNotes` (text): Jetson deployment notes
- `prerequisites` (array): Prerequisites for this chapter
- `learningObjectives` (array): Learning objectives
- `embeddedContent` (JSON): URDF examples, diagrams, etc.

**Relationships**:
- One-to-Many: Chapter → ChapterEmbedding
- One-to-Many: Chapter → UserProgress
- One-to-Many: Chapter → ChapterInteraction

### 3. Section
**Description**: Grouping of related chapters (A-H as defined in spec)

**Fields**:
- `id` (string, UUID): Unique section identifier
- `name` (string): Section name (e.g., "Foundations", "ROS2 Nervous System")
- `description` (text): Section description
- `order` (integer): Section order in textbook
- `createdAt` (timestamp): Creation timestamp

**Relationships**:
- One-to-Many: Section → Chapter

### 4. ChapterEmbedding
**Description**: Vector embeddings for RAG system

**Fields**:
- `id` (string, UUID): Unique embedding identifier
- `chapterId` (string): Reference to chapter
- `contentChunk` (text): Chunk of chapter content
- `embeddingVector` (array): Vector representation of content
- `chunkIndex` (integer): Position of chunk in chapter
- `contextWindow` (text): Context around the chunk
- `createdAt` (timestamp): Creation timestamp

**Relationships**:
- Many-to-One: ChapterEmbedding → Chapter

### 5. UserProgress
**Description**: User progress tracking through the textbook

**Fields**:
- `id` (string, UUID): Unique progress identifier
- `userId` (string): Reference to user
- `chapterId` (string): Reference to chapter
- `completed` (boolean): Whether chapter is completed
- `progressPercentage` (float): Progress percentage (0-100)
- `timeSpent` (integer): Time spent on chapter in seconds
- `lastAccessedAt` (timestamp): Last access timestamp
- `quizScores` (JSON): Quiz scores for the chapter
- `completedActivities` (array): List of completed activities

**Relationships**:
- Many-to-One: UserProgress → User
- Many-to-One: UserProgress → Chapter

### 6. UserInteraction
**Description**: User interactions with AI features and content

**Fields**:
- `id` (string, UUID): Unique interaction identifier
- `userId` (string): Reference to user
- `chapterId` (string): Reference to chapter (optional)
- `interactionType` (string): Type of interaction (query, translation, personalization)
- `input` (text): User input
- `output` (text): System output
- `context` (JSON): Context of the interaction
- `timestamp` (timestamp): When interaction occurred
- `satisfactionRating` (integer): User satisfaction rating (1-5)

**Relationships**:
- Many-to-One: UserInteraction → User
- Many-to-One: UserInteraction → Chapter (optional)

### 7. Quiz
**Description**: Chapter quizzes for assessment

**Fields**:
- `id` (string, UUID): Unique quiz identifier
- `chapterId` (string): Reference to chapter
- `title` (string): Quiz title
- `description` (text): Quiz description
- `questions` (JSON): Array of quiz questions
- `createdAt` (timestamp): Creation timestamp
- `updatedAt` (timestamp): Last update timestamp

**Relationships**:
- Many-to-One: Quiz → Chapter
- One-to-Many: Quiz → QuizSubmission

### 8. QuizSubmission
**Description**: User quiz submissions and results

**Fields**:
- `id` (string, UUID): Unique submission identifier
- `quizId` (string): Reference to quiz
- `userId` (string): Reference to user
- `answers` (JSON): User answers
- `score` (float): Score percentage (0-100)
- `completedAt` (timestamp): Completion timestamp
- `timeTaken` (integer): Time taken in seconds

**Relationships**:
- Many-to-One: QuizSubmission → Quiz
- Many-to-One: QuizSubmission → User

### 9. TranslationCache
**Description**: Caching layer for Urdu translations

**Fields**:
- `id` (string, UUID): Unique cache identifier
- `originalText` (text): Original English text
- `urduTranslation` (text): Urdu translation
- `chapterId` (string): Reference to chapter (optional)
- `createdAt` (timestamp): Creation timestamp
- `expiresAt` (timestamp): Expiration timestamp
- `usageCount` (integer): How many times used

**Relationships**:
- Many-to-One: TranslationCache → Chapter (optional)

### 10. AgentSession
**Description**: Sessions for Claude Code subagents

**Fields**:
- `id` (string, UUID): Unique session identifier
- `userId` (string): Reference to user
- `agentType` (string): Type of agent (quiz, personalization, etc.)
- `sessionData` (JSON): Agent session data
- `createdAt` (timestamp): Creation timestamp
- `lastInteractionAt` (timestamp): Last interaction timestamp
- `isActive` (boolean): Whether session is active

**Relationships**:
- Many-to-One: AgentSession → User

## Relationships Summary

```
User ||--o{ UserProgress: has
User ||--o{ UserInteraction: creates
User ||--o{ QuizSubmission: submits
Chapter ||--o{ UserProgress: tracks
Chapter ||--o{ UserInteraction: interacts_with
Chapter ||--o{ ChapterEmbedding: generates
Chapter ||--o{ Quiz: contains
Section ||--o{ Chapter: contains
Quiz ||--o{ QuizSubmission: receives
```

## Validation Rules

### User
- Email must be valid format
- Name must be 2-50 characters
- Preferences must be valid JSON

### Chapter
- Title and slug are required
- Content must be valid MDX
- Number must be positive
- GPU and Jetson notes required if applicable

### ChapterEmbedding
- embeddingVector must be consistent dimension
- chapterId must reference valid chapter
- chunkIndex must be non-negative

### UserProgress
- progressPercentage must be 0-100
- userId and chapterId required
- timeSpent must be non-negative

### UserInteraction
- interactionType must be valid enum
- timestamp required
- satisfactionRating 1-5 if provided

## State Transitions

### UserProgress States
- `not_started` → `in_progress` → `completed`
- Transitions triggered by user activity and completion criteria

### QuizSubmission States
- `submitted` → `graded` (final state)
- Automatic grading for objective questions
- Manual review for subjective questions possible

## Indexing Strategy

### Required Indexes
- User.email (for authentication)
- Chapter.slug (for routing)
- ChapterEmbedding.chapterId (for RAG)
- UserProgress.userId + chapterId (for progress lookup)
- UserInteraction.userId + timestamp (for activity history)