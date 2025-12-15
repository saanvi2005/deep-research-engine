"""
ResearchSession model.

This model will track individual research sessions, including user queries,
status, and session metadata.
"""

import uuid
from django.db import models
from django.utils import timezone


class ResearchSession(models.Model):
    """
    Model representing a research session in a deep research system.
    Tracks the lifecycle of a research query from initiation to completion.
    """
    
    # Status choices for the research session lifecycle
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    # UUID primary key for unique identification
    # Provides globally unique identifiers suitable for distributed systems
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User identifier to associate research sessions with specific users
    # Integer field for user ID (can be migrated to ForeignKey later if needed)
    user_id = models.IntegerField()
    
    # The original research query that initiated this session
    # Stores the user's question or topic to be researched
    original_query = models.TextField()
    
    # Current state of the research session
    # Status is required for async jobs because:
    # - Research operations are long-running and execute asynchronously
    # - Clients need to poll or check status without blocking
    # - Allows tracking progress through the research lifecycle
    # - Enables proper error handling and retry logic for failed sessions
    # - Supports webhooks/notifications when status changes
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Final research report generated upon completion
    # Stores the comprehensive research findings and analysis
    # Nullable because it's only populated when status is COMPLETED
    final_report = models.TextField(blank=True, null=True)
    
    # Self-referencing foreign key for research continuation
    # parent_research exists to enable iterative and hierarchical research workflows:
    # - Allows a new research session to build upon or continue a previous one
    # - Enables follow-up questions that reference earlier research
    # - Supports multi-step research where each step depends on previous findings
    # - Creates a research chain/tree structure for complex investigations
    # - Useful for "dive deeper" or "explore related topic" functionality
    parent_research = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_researches'
    )
    
    # Trace ID for observability and debugging
    # trace_id is stored to enable:
    # - Linking research sessions to LangSmith/LangChain traces for debugging
    # - Tracking LLM API calls and agent interactions across the research pipeline
    # - Performance monitoring and cost analysis per research session
    # - Reproducing issues by replaying specific traces
    # - Correlating logs and metrics with specific research executions
    trace_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamp when the research session was created
    # Used for auditing, sorting, and understanding research session history
    created_at = models.DateTimeField(default=timezone.now)
    
    # Timestamp when the research session was last modified
    # Automatically updated on each save to track when changes occurred
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Research Session'
        verbose_name_plural = 'Research Sessions'
    
    def __str__(self):
        return f"ResearchSession {self.id} - {self.status}"
