import json
from queue import Queue

from sandstock.models import ChangeLog
from sandstock.extensions import db
from sqlalchemy import event

class ChangeLogQueue:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChangeLogQueue, cls).__new__(cls, *args, **kwargs)
            cls._instance.queue = Queue()
        return cls._instance

    def put(self, change_log):
        self.queue.put(change_log)

    def pop_all(self):
        items = []
        while not self.queue.empty():
            items.append(self.queue.get())
        return items


    def commit(self):
        for item in self.pop_all():
            db.session.add(item)
        db.session.commit()

    def size(self):
        return self.queue.qsize()

    def __repr__(self):
        return f"ChangeLogQueue(size={self.queue.qsize()})"



def log_changes(mapper, connection, target, operation):
    old_data = {}
    new_data = {}

    if operation == "UPDATE":
        state = db.inspect(target)
        for attr in state.attrs:
            hist = state.get_history(attr.key, True)
            if hist.has_changes():
                old_data[attr.key] = hist.deleted[0]
                new_data[attr.key] = hist.added[0]

    elif operation == "INSERT":
        new_data = {c.name: getattr(target, c.name) for c in target.__table__.columns}

    elif operation == "DELETE":
        old_data = {c.name: getattr(target, c.name) for c in target.__table__.columns}

    if old_data or new_data:
        change_log = ChangeLog(
            table_name=target.__tablename__,
            operation=operation,
            old_data=json.dumps(old_data, default=lambda x: x.isoformat(), indent=4) if old_data else None,
            new_data=json.dumps(new_data, default=lambda x: x.isoformat(), indent=4) if new_data else None,
        )
        ChangeLogQueue().put(change_log)


def add_listeners(model):
    event.listen(model, "after_insert", lambda m, c, t: log_changes(m, c, t, "INSERT"))
    event.listen(model, "after_update", lambda m, c, t: log_changes(m, c, t, "UPDATE"))
    event.listen(model, "after_delete", lambda m, c, t: log_changes(m, c, t, "DELETE"))
