"""
Modular models package for the research app.

This package contains all Django models split into separate files for better
maintainability and organization in large AI systems.
"""

# Import all models here to maintain Django's expected model discovery
# This allows Django to find models using the standard 'research.models.ModelName' syntax

# Import all models here to maintain Django's expected model discovery
from .research_session import ResearchSession
# from .research_summary import ResearchSummary
# from .research_reasoning import ResearchReasoning
# from .uploaded_document import UploadedDocument
# from .research_cost import ResearchCost

__all__ = [
    'ResearchSession',
    # 'ResearchSummary',
    # 'ResearchReasoning',
    # 'UploadedDocument',
    # 'ResearchCost',
]

