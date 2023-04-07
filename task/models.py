from datetime import datetime
from flask_login import UserMixin
from task import manager

from task import db


class Task(db.Model):
    """
    параметры: id - автоматически заполняемое уникальное поле
               title - краткий заголовок задачи
               text - подробный текст задачи
               status - статус задачи: 0 - в работе, 1 - исполнена
               deadline - крайний срок выполнения задачи, дедлайн
               date - дата и время создания задачи

    методы: get_status() - выдергивает статус задачи, дополняя статусом 2,
                который высчитывается автоматически, исходя из текущей даты и дедлайна.
                Статус 2 - просроченная задача
                Статус 3 - срочная задача (меньше суток)

            get_text() - меняет символ перевода строки на html-тег перевода строки в
                подробном тексте задачи
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=0) #статус задачи: 0 - в работе, 1 - исполнена
    deadline = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

    def get_status(self):
        if self.deadline < datetime.now() and self.status != 1:
            return 2 #статус 2 - просрочена
        elif (self.deadline - datetime.now()).days < 1 and self.status != 1:
            return 3 #статус 3 - срочно (меньше суток)
        else:
            return self.status

    def get_text(self):
        text = self.text.replace('\n', '<br>')
        return text


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    @manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)