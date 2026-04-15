import pandas as pd
import json
import sys
from langchain_core.tools import tool
from dental_agent.config.settings import CSV_PATH

def _load_df() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()
    df["is_available"] = df["is_available"].astype(str).str.upper() == "TRUE"
    df["date_slot"] = pd.to_datetime(df["date_slot"])
    df["doctor_name"] = df["doctor_name"].str.lower().str.strip()
    df["specialization"] = df["specialization"].str.lower().str.strip()
    df["patient_to_attend"] = (
        df["patient_to_attend"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )
    return df

def _save_df(df: pd.DataFrame) -> None:
    out = df.copy()
    # Save in consistent ISO format
    out["date_slot"] = out["date_slot"].dt.strftime("%Y-%m-%d %H:%M:%S")
    out["is_available"] = out["is_available"].map({True: "TRUE", False: "FALSE"})
    out["patient_to_attend"] = out["patient_to_attend"].replace("nan", "")
    out.to_csv(CSV_PATH, index=False)

@tool
def book_appointment(patient_id: str, doctor_name: str, date_slot: str) -> str:
    """
    Book an appointment.
    Returns a JSON string with success/message.
    """
    df = _load_df()
    try:
        target_dt = pd.to_datetime(date_slot)
    except Exception:
        return json.dumps({"success": False, "message": f"Invalid date format: {date_slot}"})

    doc = doctor_name.lower().strip()
    mask = (df["doctor_name"] == doc) & (df["date_slot"] == target_dt)
    
    if df[mask].empty:
        return json.dumps({"success": False, "message": "Slot not found."})
    if not df.loc[mask, "is_available"].iloc[0]:
        return json.dumps({"success": False, "message": "Slot already taken."})

    df.loc[mask, "is_available"] = False
    df.loc[mask, "patient_to_attend"] = str(patient_id).strip()
    _save_df(df)
    return json.dumps({
        "success": True, 
        "message": f"Booked for {patient_id} with {doctor_name} at {date_slot}"
    })

@tool
def cancel_appointment(patient_id: str, date_slot: str) -> str:
    """Cancel an appointment. Returns JSON string."""
    df = _load_df()
    try:
        target_dt = pd.to_datetime(date_slot)
    except Exception:
        return json.dumps({"success": False, "message": "Invalid date format."})

    pid = str(patient_id).strip()
    mask = (df["patient_to_attend"] == pid) & (df["date_slot"] == target_dt)
    
    if df[mask].empty:
        return json.dumps({"success": False, "message": "Booking not found."})

    df.loc[mask, "is_available"] = True
    df.loc[mask, "patient_to_attend"] = ""
    _save_df(df)
    return json.dumps({"success": True, "message": "Cancelled."})

@tool
def reschedule_appointment(patient_id: str, current_date_slot: str, new_date_slot: str, doctor_name: str) -> str:
    """Reschedule an appointment. Returns JSON string."""
    # Simplified for robustness
    df = _load_df()
    try:
        cur_dt = pd.to_datetime(current_date_slot)
        new_dt = pd.to_datetime(new_date_slot)
    except Exception:
        return json.dumps({"success": False, "message": "Invalid date format."})

    doc = doctor_name.lower().strip()
    pid = str(patient_id).strip()

    old_mask = (df["patient_to_attend"] == pid) & (df["date_slot"] == cur_dt)
    new_mask = (df["doctor_name"] == doc) & (df["date_slot"] == new_dt)

    if df[old_mask].empty:
        return json.dumps({"success": False, "message": "Old booking not found."})
    if df[new_mask].empty or not df.loc[new_mask, "is_available"].iloc[0]:
        return json.dumps({"success": False, "message": "New slot unavailable."})

    df.loc[old_mask, "is_available"] = True
    df.loc[old_mask, "patient_to_attend"] = ""
    df.loc[new_mask, "is_available"] = False
    df.loc[new_mask, "patient_to_attend"] = pid
    _save_df(df)
    return json.dumps({"success": True, "message": "Rescheduled."})
