from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from dental_agent.config.settings import (
    GROQ_API_KEY, 
    MODEL_NAME, 
    TEMPERATURE,
    VALID_SPECIALIZATIONS,
    VALID_DOCTORS
)
from dental_agent.models.state import AppointmentState
from dental_agent.tools.csv_reader import (
    get_available_slots,
    get_patient_appointments,
    check_slot_availability,
    list_doctors_by_specialization,
)
from dental_agent.utils import sanitize_messages

INFO_TOOLS = [
    get_available_slots,
    get_patient_appointments,
    check_slot_availability,
    list_doctors_by_specialization,
]

INFO_SYSTEM = f"""You are the Information Agent for a dental appointment system.

Your role is to answer queries about doctor availability, schedules, and appointment status.

## Reference Data
- Valid Specializations: {", ".join(VALID_SPECIALIZATIONS)}
- Valid Doctors: {", ".join(VALID_DOCTORS)}

## Guidelines
1. Use tools to fetch real data. Never invent slot times.
2. If the user's specialization or doctor name has a typo, use the Reference Data to correct it before calling tools.
3. If the user has not provided enough parameters, ask a focused clarifying question.
4. Present results in a clear, friendly, numbered list.
5. After answering, ask if the user needs anything else.

## Date Format
All dates follow M/D/YYYY H:MM format (e.g., 5/10/2026 9:00).
"""

info_tool_node = ToolNode(tools=INFO_TOOLS)


def info_agent_node(state: AppointmentState) -> dict:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
    ).bind_tools(INFO_TOOLS)

    messages = [SystemMessage(content=INFO_SYSTEM)] + sanitize_messages(state["messages"])
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "final_response": response.content if not response.tool_calls else None,
    }
