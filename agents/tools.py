from langchain_core.tools import tool
from database import SessionLocal
from models import User, Appointment, Reminder
from pydantic import BaseModel, Field
import datetime

class BookAppointmentInput(BaseModel):
    doctor_name: str = Field(description="The name of the doctor to book")
    time_str: str = Field(description="The time for the appointment in YYYY-MM-DD HH:MM format")

@tool("book_appointment", args_schema=BookAppointmentInput)
def book_appointment(doctor_name: str, time_str: str) -> str:
    """Books an appointment for the demo patient with a specific doctor."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "patient@demo.com").first()
        if not user:
            return "Error: Patient not found."
            
        appointment_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        
        new_apt = Appointment(
            patient_id=user.id,
            doctor_name=doctor_name,
            appointment_time=appointment_time
        )
        db.add(new_apt)
        db.commit()
        return f"Successfully booked appointment with {doctor_name} at {time_str}."
    except ValueError:
        return "Error: Invalid time format. Please use YYYY-MM-DD HH:MM."
    except Exception as e:
        db.rollback()
        return f"An error occurred: {str(e)}"
    finally:
        db.close()

class SetReminderInput(BaseModel):
    reminder_text: str = Field(description="The text of the reminder, e.g., 'Take medication'")
    time_str: str = Field(description="The time for the reminder in YYYY-MM-DD HH:MM format")

@tool("set_reminder", args_schema=SetReminderInput)
def set_reminder(reminder_text: str, time_str: str) -> str:
    """Sets a health or medication reminder for the patient."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "patient@demo.com").first()
        if not user:
            return "Error: Patient not found."
            
        reminder_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        
        new_reminder = Reminder(
            patient_id=user.id,
            reminder_text=reminder_text,
            reminder_time=reminder_time
        )
        db.add(new_reminder)
        db.commit()
        return f"Successfully set reminder: '{reminder_text}' at {time_str}."
    except ValueError:
        return "Error: Invalid time format. Please use YYYY-MM-DD HH:MM."
    except Exception as e:
        db.rollback()
        return f"An error occurred: {str(e)}"
    finally:
        db.close()

@tool("get_patient_records")
def get_patient_records(query: str = "") -> str:
    """Retrieves the digital health records, appointments, and reminders for the demo patient."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "patient@demo.com").first()
        if not user:
            return "Error: Patient not found."
            
        appointments = db.query(Appointment).filter(Appointment.patient_id == user.id).all()
        reminders = db.query(Reminder).filter(Reminder.patient_id == user.id).all()
        
        record = f"Patient: {user.name}\n\nAppointments:\n"
        if not appointments:
            record += "No upcoming appointments.\n"
        for apt in appointments:
            record += f"- {apt.doctor_name} at {apt.appointment_time.strftime('%Y-%m-%d %H:%M')} ({apt.status})\n"
            
        record += "\nReminders:\n"
        if not reminders:
            record += "No active reminders.\n"
        for rem in reminders:
            status = "Completed" if rem.is_completed else "Pending"
            record += f"- {rem.reminder_text} at {rem.reminder_time.strftime('%Y-%m-%d %H:%M')} ({status})\n"
            
        return record
    finally:
        db.close()
