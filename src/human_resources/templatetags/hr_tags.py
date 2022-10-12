from django import template
from ..evaluation import allTimeEvaluation

# Register template library
register = template.Library()


@register.simple_tag
def getAllTimeEvaluation(pk: int) -> float:
    """
    This tag gets the employee overall all time evaluation.

    Args:
        pk (int): Employee ID

    Returns:
        float: Overall employee's evaluation
    """
    return allTimeEvaluation(pk)


@register.simple_tag
def calculateTaskRate(a: float, b: float) -> float:
    """
    This tag for calculating the task rate.
    The task has 2 rating, the task rate and the submission time's rate.

    Args:
        a (float): Task rate
        b (float): Submission time's rate

    Returns:
        float: _description_
    """
    return (a+b) / 2
