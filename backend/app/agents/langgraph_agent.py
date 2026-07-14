import json
import re
from typing import Any, TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.tools.interaction_tools import build_tools
from app.utils.config import get_settings


class AgentState(TypedDict, total=False):
    user_message: str
    action: str
    arguments: dict[str, Any]
    result: Any
    response: str


ROUTER_PROMPT = """
You are an AI CRM assistant for pharmaceutical field representatives.
Choose exactly one tool for the user's request.

Available tools:
1. search_hcp(query)
2. summarize_interaction(notes)
3. recommend_follow_up(notes, sentiment)
4. log_interaction(hcp_id, interaction_type, interaction_date, interaction_time,
   topics_discussed, attendees, materials_shared, samples_distributed,
   sentiment, outcomes, follow_up_actions)
5. edit_interaction(interaction_id, field, value)

Return JSON only:
{"action":"tool_name","arguments":{...}}

For dates use YYYY-MM-DD. For time use HH:MM:SS.
If required information is missing, return:
{"action":"clarify","arguments":{"message":"Ask a concise clarification question."}}
"""


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {"action": "clarify", "arguments": {"message": "Please provide more details."}}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"action": "clarify", "arguments": {"message": "Please rephrase the request with the necessary details."}}


def create_agent(db: Session):
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing in backend/.env")

    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0,
    )

    def summarize(notes: str) -> str:
        response = llm.invoke(
            "Summarize these HCP interaction notes in 2-3 concise sentences. "
            "Keep only clinically and commercially relevant facts. Notes:\n" + notes
        )
        return str(response.content).strip()

    def recommend(notes: str, sentiment: str) -> str:
        response = llm.invoke(
            "Recommend 2 practical, compliant follow-up actions for a pharmaceutical "
            f"field representative. Sentiment: {sentiment}. Notes:\n{notes}"
        )
        return str(response.content).strip()

    tools = build_tools(db, summarize, recommend)

    def router_node(state: AgentState) -> AgentState:
        response = llm.invoke(
            [
                ("system", ROUTER_PROMPT),
                ("human", state["user_message"]),
            ]
        )
        decision = _extract_json(str(response.content))
        return {
            **state,
            "action": decision.get("action", "clarify"),
            "arguments": decision.get("arguments", {}),
        }

    def tool_node(state: AgentState) -> AgentState:
        action = state.get("action", "clarify")
        args = state.get("arguments", {})

        if action == "clarify":
            message = args.get("message", "Please provide more details.")
            return {**state, "result": None, "response": message}

        selected_tool = tools.get(action)
        if selected_tool is None:
            return {
                **state,
                "action": "clarify",
                "result": None,
                "response": "I could not determine the correct CRM action. Please rephrase.",
            }

        try:
            result = selected_tool.invoke(args)
        except Exception as exc:
            return {
                **state,
                "result": {"error": str(exc)},
                "response": f"I could not complete {action}: {exc}",
            }

        response = llm.invoke(
            "Write a concise, helpful confirmation for the CRM user. "
            f"Action: {action}. Tool result: {json.dumps(result, default=str)}"
        )
        return {
            **state,
            "result": result,
            "response": str(response.content).strip(),
        }

    graph = StateGraph(AgentState)
    graph.add_node("route", router_node)
    graph.add_node("execute_tool", tool_node)
    graph.set_entry_point("route")
    graph.add_edge("route", "execute_tool")
    graph.add_edge("execute_tool", END)
    return graph.compile()


def run_agent(db: Session, user_message: str) -> dict:
    agent = create_agent(db)
    result = agent.invoke({"user_message": user_message})
    return {
        "action": result.get("action", "clarify"),
        "message": result.get("response", ""),
        "data": result.get("result"),
    }
