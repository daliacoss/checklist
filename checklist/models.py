from flask.ext.sqlalchemy import SQLAlchemy
from checklist import app, db

class Task(db.Model):
	__tablename__ = "tasks"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), index=False, nullable=False)
	comment = db.Column(db.String(300), index=False)
	parent_task_id = db.Column(db.Integer)
	datetime_added = db.Column(db.DateTime)
	datetime_completed = db.Column(db.DateTime, nullable=True)
	is_today = db.Column(db.Boolean, nullable=False)

	def __init__(self, name, is_today, comment="", **kwargs):
		self.name = name
		self.is_today = is_today
		for k,v in kwargs.items():
			setattr(self, k, v)

class Milestone(db.Model):
	__tablename__ = "milestones"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), index=False, nullable=False)

	def __init__(self, name):
		self.name = name

class MilestoneTask(db.Model):
	__tablename__ = "milestone_tasks"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), index=False, nullable=False)
	comment = db.Column(db.String(300), index=False)
	parent_task_id = db.Column(db.Integer)
	datetime_added = db.Column(db.DateTime)
	datetime_completed = db.Column(db.DateTime, nullable=True)
	milestone_id = db.Column(db.Integer, db.ForeignKey("milestones.id"), nullable=False)

	def __init__(self, name):
		self.name = name

db.create_all()
