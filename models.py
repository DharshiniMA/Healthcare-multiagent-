from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    
    appointments = relationship("Appointment", back_populates="patient")
    reminders = relationship("Reminder", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_name = Column(String, index=True)
    appointment_time = Column(DateTime)
    status = Column(String, default="Scheduled") # Scheduled, Completed, Cancelled
    
    patient = relationship("User", back_populates="appointments")

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    reminder_text = Column(String)
    reminder_time = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    
    patient = relationship("User", back_populates="reminders")
