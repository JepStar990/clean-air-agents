"""
LangGraph supervisor (optional) for iterative loop:
fetch -> analyze -> draft policy -> evaluate -> loop until score >= 0.8.

References:
- LangGraph orchestration patterns: loops, state, conditional edges. [7](https://success.valiant2001.com/azure-nv-series-pricing-azure-virtual-machine-cost/) [8](https://www.youtube.com/watch?v=bcYmfHOrOPM)
"""

from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from app.tools.openaq_api import fetch_measurements
from app.agents.analytics_agent import analyze_measurements
from app.agents.policy_agent import draft_policy
from app.agents.eval_agent import evaluate_policy


class State(TypedDict):
    city: str
    country: str
    parameter: str
    measurements: Any
    analytics: Any
    policy: str
    eval: Any
    score: float


# Nodes
async def etl_node(state: State):
    data = await fetch_measurements(country=state["country"], city=state["city"], parameter=state.get("parameter", "pm25"), limit=500)
    state["measurements"] = data
    return state


def analytics_node(state: State):
    state["analytics"] = analyze_measurements(state["measurements"])
    return state


async def policy_node(state: State, model: str):
    state["policy"] = await draft_policy(model=model, city=state["city"], analytics_summary=state["analytics"])
    return state


async def eval_node(state: State, model: str):
    j = await evaluate_policy(model=model, policy_text=state["policy"])
    state["eval"] = j
    state["score"] = float(j.get("overall", 0.0))
    return state


def build_graph(model: str = "llama3:8b-instruct-q4"):
    g = StateGraph(State)
    g.add_node("etl", etl_node)
    g.add_node("analytics", analytics_node)
    g.add_node("policy", lambda s: policy_node(s, model))
    g.add_node("eval", lambda s: eval_node(s, model))

    g.add_edge("etl", "analytics")
    g.add_edge("analytics", "policy")
    g.add_edge("policy", "eval")

    def route(state: State):
        return "policy" if float(state.get("score", 0.0)) < 0.8 else END

    g.add_conditional_edges("eval", route)
    return g.compile()

