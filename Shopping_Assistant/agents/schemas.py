"""
agents/schemas.py
Pydantic models for strict structured output across all agents.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ── Agent-level schemas ────────────────────────────────────────────────────

class QueryUnderstanding(BaseModel):
    product_type: str = Field(description="Main product category the user wants")
    budget: float = Field(description="Maximum budget in INR (rupees)")
    brand_preference: Optional[str] = Field(None, description="Preferred brand if mentioned")
    key_features: list[str] = Field(default_factory=list, description="Must-have features")
    search_query: str = Field(description="Optimised search query for product lookup")


class ProductItem(BaseModel):
    name: str = Field(description="Full product name")
    price: float = Field(description="Price in INR")
    rating: float = Field(description="Rating out of 5")
    features: list[str] = Field(default_factory=list, description="Key features")
    url: Optional[str] = Field(None, description="Product URL if available")


class ProductSearchResult(BaseModel):
    products: list[ProductItem] = Field(description="List of found products")


class ProductComparison(BaseModel):
    name: str
    price: float
    rating: float
    pros: list[str]
    cons: list[str]
    value_score: float = Field(description="Computed value score 0-10")


class ComparisonResult(BaseModel):
    comparisons: list[ProductComparison]
    best_value: str = Field(description="Name of best value product")


class BudgetItem(BaseModel):
    name: str
    price: float
    within_budget: bool
    note: str = Field(default="", description="Reason if excluded")


class BudgetOptimizationResult(BaseModel):
    budget: float
    items: list[BudgetItem]
    recommended: list[str] = Field(description="Names of budget-approved products")
    alternatives: list[dict] = Field(default_factory=list)


class ReviewInsights(BaseModel):
    product_name: str
    positives: list[str]
    negatives: list[str]
    common_issues: list[str]
    sentiment: str = Field(description="overall: positive/neutral/negative")


class FinalProduct(BaseModel):
    name: str
    price: float
    rating: float
    features: list[str]
    pros: list[str]
    cons: list[str]


class BestChoice(BaseModel):
    name: str
    reason: str


class AlternativeProduct(BaseModel):
    name: str
    price: float


# ── Master output schema ───────────────────────────────────────────────────

class ShoppingAssistantOutput(BaseModel):
    query: str
    budget: float
    products: list[FinalProduct]
    best_choice: BestChoice
    alternatives: list[AlternativeProduct]
    review_summary: Optional[dict] = None
