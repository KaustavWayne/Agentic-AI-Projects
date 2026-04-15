import pandas as pd
import json
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

@tool
def get_available_slots(specialization: str = "", doctor_name: str = "", date_filter: str = "") -> str:
    """Return available slots as JSON string."""
    df = _load_df()
    mask = df["is_available"]
    if specialization:
        mask &= (df["specialization"] == specialization.lower().strip())
    if doctor_name:
        mask &= (df["doctor_name"] == doctor_name.lower().strip())
    if date_filter:
        try:
            target_date = pd.to_datetime(date_filter).date()
            mask &= (df["date_slot"].dt.date == target_date)
        except: pass
    
    res = df[mask].head(20)[["date_slot", "specialization", "doctor_name"]].copy()
    res["date_slot"] = res["date_slot"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(res.to_dict(orient="records"))

@tool
def get_patient_appointments(patient_id: str) -> str:
    """Return patient appointments as JSON string."""
    df = _load_df()
    mask = df["patient_to_attend"] == str(patient_id).strip()
    res = df[mask][["date_slot", "specialization", "doctor_name"]].copy()
    res["date_slot"] = res["date_slot"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(res.to_dict(orient="records"))

@tool
def check_slot_availability(doctor_name: str, date_slot: str) -> str:
    """Check if slot is available. Returns JSON string."""
    df = _load_df()
    try:
        dt = pd.to_datetime(date_slot)
    except:
        return json.dumps({"found": False, "error": "Invalid date"})
    
    mask = (df["doctor_name"] == doctor_name.lower().strip()) & (df["date_slot"] == dt)
    rows = df[mask]
    if rows.empty:
        return json.dumps({"found": False})
    
    row = rows.iloc[0]
    return json.dumps({
        "found": True, 
        "is_available": bool(row["is_available"]),
        "patient_to_attend": row["patient_to_attend"]
    })

@tool
def list_doctors_by_specialization(specialization: str) -> str:
    """List doctors. Returns JSON string."""
    df = _load_df()
    mask = df["specialization"] == specialization.lower().strip()
    return json.dumps(sorted(df[mask]["doctor_name"].unique().tolist()))
