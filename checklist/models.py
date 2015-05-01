from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from checklist import db
import datetime

class Task(db.Model):
	__tablename__ = "tasks"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), index=False, nullable=False)
	comment = db.Column(db.String(300), index=False)
	parent_task_id = db.Column(db.Integer)
	datetime_added = db.Column(db.DateTime(timezone=True))
	datetime_completed = db.Column(db.DateTime(timezone=True), nullable=True)
	is_today = db.Column(db.Boolean, nullable=False)

	def __init__(self, name, comment="", is_today=False, **kwargs):
		self.name = name
		self.is_today = is_today
		self.comment = comment
		for k,v in kwargs.items():
			setattr(self, k, v)

		self.children = []
		self.hidden = False

	def has_parent(self):
		return type(self.parent_task_id) == int and self.parent_task_id != self.id

	def collectChildren(self):
		self.children = Task.query.filter_by(parent_task_id=self.id).all()
		return self.children

	def deleteFromSession(self, deleteDescendants=False):
		"""delete this model from db.session (without committing)"""

		if deleteDescendants:
			for child in self.collectChildren():
				child.deleteFromSession(True)

		db.session.delete(self)

	def markComplete(self, markDescendants=False):

		self.datetime_completed = datetime.datetime.utcnow()
		if markDescendants:
			for child in self.collectChildren():
				child.markComplete(True)

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
