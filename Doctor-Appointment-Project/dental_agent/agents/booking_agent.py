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
from dental_agent.tools.csv_reader import get_available_slots, check_slot_availability
from dental_agent.tools.csv_writer import book_appointment
from dental_agent.utils import sanitize_messages

BOOKING_TOOLS = [get_available_slots, check_slot_availability, book_appointment]

BOOKING_SYSTEM = f"""You are the Booking Agent for a dental appointment management system.

Your ONLY job is to book NEW appointments for patients.

## Reference Data
- Valid Specializations: {", ".join(VALID_SPECIALIZATIONS)}
- Valid Doctors: {", ".join(VALID_DOCTORS)}

## Workflow
1. Collect REQUIRED information:
   - patient_id       : numeric patient ID
   - specialization   : the type of dentist needed (correct typos using the Reference Data)
   - doctor_name      : specific doctor name
   - date_slot        : desired date/time in M/D/YYYY H:MM format

2. If you have the doctor and date_slot, ALWAYS call check_slot_availability first.
   - If available, call book_appointment.
   - If NOT available, call get_available_slots to find alternatives for that doctor or specialization.

3. Do not explain why you are calling a tool, just call it.
4. If information is missing, ask for exactly ONE missing item at a time.

## Date Format
M/D/YYYY H:MM (e.g., 5/10/2026 9:00)
"""

booking_tool_node = ToolNode(tools=BOOKING_TOOLS)


def booking_agent_node(state: AppointmentState) -> dict:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
    ).bind_tools(BOOKING_TOOLS)

    messages = [SystemMessage(content=BOOKING_SYSTEM)] + sanitize_messages(state["messages"])
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "final_response": response.content if not response.tool_calls else None,
    }
