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
from dental_agent.tools.csv_reader import get_patient_appointments
from dental_agent.tools.csv_writer import cancel_appointment
from dental_agent.utils import sanitize_messages

CANCEL_TOOLS = [get_patient_appointments, cancel_appointment]

CANCEL_SYSTEM = f"""You are the Cancellation Agent for a dental appointment management system.

Your ONLY job is to cancel existing appointments.

## Reference Data
- Valid Doctors: {", ".join(VALID_DOCTORS)}

## Workflow
1. Collect REQUIRED information:
   - patient_id  : numeric patient ID
   - date_slot   : the specific slot to cancel in M/D/YYYY H:MM format

2. If the patient does not know the exact slot, ALWAYS call get_patient_appointments(patient_id)
   to list their bookings, then ask them to confirm which one to cancel.

3. Confirm with the user before actually calling the cancellation tool.

4. Once confirmed, call cancel_appointment(patient_id, date_slot).

5. Inform the user of the outcome.

## Rules
- Be concise.
- If the patient has no appointments, inform them kindly.
- Use Reference Data to help with doctor names if mentioned.

## Date Format
M/D/YYYY H:MM (e.g., 5/8/2026 8:30)
"""

cancellation_tool_node = ToolNode(tools=CANCEL_TOOLS)


def cancellation_agent_node(state: AppointmentState) -> dict:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
    ).bind_tools(CANCEL_TOOLS)

    messages = [SystemMessage(content=CANCEL_SYSTEM)] + sanitize_messages(state["messages"])
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "final_response": response.content if not response.tool_calls else None,
    }
