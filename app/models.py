from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    tasks = relationship('Task', back_populates='user', cascade="all, delete-orphan")
    schedules = relationship('Schedule', back_populates='user', cascade="all, delete-orphan")
    reminders = relationship('Reminder', back_populates='user', cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(TIMESTAMP)
    priority = Column(Integer)
    status = Column(String(50), default='pending')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship('User', back_populates='tasks')
    reminders = relationship('Reminder', back_populates='task', cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('priority >= 1 AND priority <= 5', name='priority_range'),
    )


class Schedule(Base):
    __tablename__ = 'schedules'

    event_id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'))
    title = Column(String(255), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    calendar_id = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship('User',  back_populates='schedules')

class Reminder(Base):
    __tablename__ = 'reminders'

    reminder_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    user_id = Column(String(50), ForeignKey('users.user_id'))
    reminder_time = Column(TIMESTAMP, nullable=False)
    method = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    task = relationship('Task', back_populates='reminders')
    user = relationship('User', back_populates='reminders')

