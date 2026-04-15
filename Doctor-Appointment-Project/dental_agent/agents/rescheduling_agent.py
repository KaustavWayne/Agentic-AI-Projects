from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from dental_agent.config.settings import (
    GROQ_API_KEY, 
    MODEL_NAME, 
    TEMPERATURE,
    VALID_DOCTORS
)
from dental_agent.models.state import AppointmentState
from dental_agent.tools.csv_reader import get_patient_appointments, get_available_slots
from dental_agent.tools.csv_writer import reschedule_appointment
from dental_agent.utils import sanitize_messages

RESCHEDULE_TOOLS = [get_patient_appointments, get_available_slots, reschedule_appointment]

RESCHEDULE_SYSTEM = f"""You are the Rescheduling Agent for a dental appointment management system.

Your ONLY job is to move an existing appointment to a new time slot.

## Reference Data
- Valid Doctors: {", ".join(VALID_DOCTORS)}

## Workflow
1. Collect REQUIRED information:
   - patient_id         : numeric patient ID
   - current_date_slot  : the existing appointment to move (M/D/YYYY H:MM)
   - new_date_slot      : the desired new slot (M/D/YYYY H:MM)
   - doctor_name        : doctor name

2. If any info is missing (like the current slot), call get_patient_appointments(patient_id).
3. If they need a new slot, call get_available_slots(doctor_name=...).
4. Once all info is confirmed, call reschedule_appointment(patient_id, current_date_slot, new_date_slot, doctor_name).

## Rules
- The new slot is with the SAME doctor by default.
- Always show clear confirmation of what changed (old → new).
- If reschedule fails, explain why and offer alternatives using tools.

## Date Format
M/D/YYYY H:MM (e.g., 5/10/2026 9:00)
"""

rescheduling_tool_node = ToolNode(tools=RESCHEDULE_TOOLS)


def rescheduling_agent_node(state: AppointmentState) -> dict:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
    ).bind_tools(RESCHEDULE_TOOLS)

    messages = [SystemMessage(content=RESCHEDULE_SYSTEM)] + sanitize_messages(state["messages"])
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "final_response": response.content if not response.tool_calls else None,
    }
