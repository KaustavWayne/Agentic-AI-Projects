"""
agents/aggregator_agent.py
Combines all agent results into the final ShoppingAssistantOutput.
"""

from .schemas import (
    QueryUnderstanding, ProductSearchResult, ComparisonResult,
    BudgetOptimizationResult, ReviewInsights, BestChoice,
    ShoppingAssistantOutput, FinalProduct, AlternativeProduct
)


def run_aggregator_agent(
    query_info: QueryUnderstanding,
    search_result: ProductSearchResult,
    comparison: ComparisonResult,
    budget_result: BudgetOptimizationResult,
    review: ReviewInsights | None,
    best_choice: BestChoice,
) -> ShoppingAssistantOutput:

    # Build lookup maps
    comp_map = {c.name: c for c in comparison.comparisons}

    final_products: list[FinalProduct] = []
    for product in search_result.products:
        comp = comp_map.get(product.name)
        final_products.append(FinalProduct(
            name=product.name,
            price=product.price,
            rating=product.rating,
            features=product.features,
            pros=comp.pros if comp else [],
            cons=comp.cons if comp else [],
        ))

    alternatives = [
        AlternativeProduct(name=a["name"], price=a["price"])
        for a in budget_result.alternatives[:3]
    ]

    review_summary = None
    if review:
        review_summary = {
            "positives": review.positives,
            "negatives": review.negatives,
            "common_issues": review.common_issues,
            "sentiment": review.sentiment,
        }

    return ShoppingAssistantOutput(
        query=query_info.product_type,
        budget=query_info.budget,
        products=final_products,
        best_choice=best_choice,
        alternatives=alternatives,
        review_summary=review_summary,
    )
