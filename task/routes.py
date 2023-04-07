from flask import render_template, url_for, request, redirect, flash
from datetime import datetime

from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from task import db, app
from task.models import Task, User


@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    основная страница сайта, на которой формируется список всех задач
    со статусом 0, то есть не закрытых. Передаётся в переменной tasks
    """
    tasks = Task.query.order_by(Task.deadline).filter_by(status=0).all()
    return render_template("index.html", tasks=tasks)


@app.route('/about')
def about():
    """
    страница О сайте. Ничего не передаём, лишь обрабатываем заготовленный шаблон.
    """
    return render_template("about.html")


@app.route('/tasks')
@login_required
def tasks():
    """
    Страница со всеми когда-либо созданными задачами.
    Задачи передаются в переменной tasks
    """
    tasks = Task.query.order_by(Task.date).all()
    return render_template("tasks.html", tasks=tasks)


@app.route('/tasks/<int:id>')
@login_required
def task_detail(id):
    """
    Подробная информация по конкретной задаче под указанным id. Например ссылка /tasks/13
    передаст задачу с id 13.
    Передаётся в переменной task
    """
    task = Task.query.get(id)
    return render_template("task_detail.html", task=task)


@app.route('/tasks/<int:id>/delete')
@login_required
def task_delete(id):
    """
    Удаление задачи под указанным id. Например ссылка /tasks/13/delete
    удалит задачу с id 13. После удачного удаления перекинет на страницу со всеми задачами.
    """
    task = Task.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/tasks')
    except:
        return 'При удалении задачи произошла ошибка'


@app.route('/tasks/<int:id>/update', methods=['POST', 'GET'])
@login_required
def task_update(id):
    """
    Изменение задачи под указанным id. Например ссылка /tasks/13/update
    позволит изменить задачу с id 13.
    Если обращение методом POST, после удачного изменения перекинет на страницу с задачей.
    Если обращение методом GET, то создаёт страницу с формой и предыдущими данными,
    которые передаются через переменную task. Форма уже заполнена этими данными.
    """
    task = Task.query.get(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.text = request.form['text']
        deadline_str = request.form['deadline']
        task.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')

        try:
            db.session.commit()
            return redirect(f'/tasks/{id}')
        except:
            return 'При изменении задачи произошла ошибка'
    else:
        return render_template("update_task.html", task=task)


@app.route('/tasks/<int:id>/change_status_<int:new_status>')
@login_required
def task_change_status(id, new_status):
    """
    Меняет статус задачи с указанным id на указанный статус new_status
    Ссылка вида /tasks/13/change_status_1 изменит статус задачи под id 13 на 1, то есть задача закрыта.
    """
    task = Task.query.get(id)
    task.status = new_status
    try:
        db.session.commit()
        return redirect(f'/tasks/{id}')
    except:
        return 'При изменении статуса произошла ошибка'


@app.route('/create_task', methods=['POST', 'GET'])
@login_required
def create_task():
    """
    Создание новой задачи.
    Если обращение методом POST, после добавления новой задачи перекинет на главную страницу.
    Если обращение методом GET, то создаёт страницу с формой с нужными полями.
    """
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        deadline_str = request.form['deadline']
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')

        try:
            new_task = Task(title=title, text=text, deadline=deadline)
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'При добавлении задачи произошла ошибка'
    else:
        return render_template("create_task.html")


@app.route('/tasks/completed')
@login_required
def tasks_completed():
    """
    Cтраница сайта, на которой формируется список всех задач
    со статусом 1, то есть закрытых. Передаётся в переменной tasks
    """
    tasks = Task.query.order_by(Task.date.desc()).filter_by(status = 1).all()
    return render_template("tasks_completed.html", tasks=tasks)


@app.route('/tasks/overdue')
@login_required
def tasks_overdue():
    """
    Cтраница сайта, на которой формируется список всех задач
    со статусом 2, то есть просроченных. Передаётся в переменной tasks.
    Используется метод get_status() модели Task.
    """
    overdue_tasks = Task.query.order_by(Task.date.desc()).filter_by(status=0).all()
    tasks = []
    for task in overdue_tasks:
        if task.get_status() == 2:
            tasks.append(task)
    return render_template("tasks_overdue.html", tasks=tasks)


@app.route('/tasks/deadline')
@login_required
def tasks_deadline():
    """
     Cтраница сайта, на которой формируется список всех задач
    со статусом 3, то есть срочных. Передаётся в переменной tasks
    """
    deadline_tasks = Task.query.order_by(Task.date.desc()).filter_by(status=0).all()
    tasks = []
    for task in deadline_tasks:
        if task.get_status() == 3:
            tasks.append(task)
    return render_template("tasks_deadline.html", tasks=tasks)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Неверный логин или пароль.")
    else:
        flash("Пожалуйста, заполните все поля.")
    return render_template("login.html")


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if request.method == "POST":
        if not (login or password or password2):
            flash("Пожалуйста, заполните все поля.")
        elif password != password2:
            print(password, password2)
            flash("Пароли не совпадают.")
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))

    else:
        flash("Заполните все поля.")
    return render_template("register.html")

