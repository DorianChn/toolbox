import { useEffect, useRef, useState } from 'react';
import type { Task } from '../types';

interface Props {
  task: Task;
  onToggle: (task: Task) => void;
  onDelete: (task: Task) => void;
  onSave: (task: Task, patch: { title: string; notes: string }) => void;
}

export function TaskItem({ task, onToggle, onDelete, onSave }: Props) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [notes, setNotes] = useState(task.notes);
  const titleRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) titleRef.current?.focus();
  }, [editing]);

  function startEditing() {
    setTitle(task.title);
    setNotes(task.notes);
    setEditing(true);
  }

  function commit() {
    const nextTitle = title.trim();
    if (!nextTitle) {
      setTitle(task.title);
      setEditing(false);
      return;
    }
    onSave(task, { title: nextTitle, notes: notes.trim() });
    setEditing(false);
  }

  const done = task.status === 'done';

  if (editing) {
    return (
      <li className="task task--editing">
        <input
          ref={titleRef}
          className="task__edit-title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') commit();
            if (event.key === 'Escape') setEditing(false);
          }}
          maxLength={200}
        />
        <input
          className="task__edit-notes"
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Notes (optional)"
          maxLength={2000}
        />
        <div className="task__actions">
          <button className="btn" type="button" onClick={commit}>
            Save
          </button>
          <button className="btn btn--ghost" type="button" onClick={() => setEditing(false)}>
            Cancel
          </button>
        </div>
      </li>
    );
  }

  return (
    <li className={`task${done ? ' task--done' : ''}`}>
      <label className="task__toggle">
        <input type="checkbox" checked={done} onChange={() => onToggle(task)} />
        <span className="task__checkbox" aria-hidden="true" />
        <span className="task__title">{task.title}</span>
      </label>

      {task.notes ? <p className="task__notes">{task.notes}</p> : null}

      <div className="task__actions">
        <button className="btn btn--ghost" type="button" onClick={startEditing}>
          Edit
        </button>
        <button className="btn btn--danger" type="button" onClick={() => onDelete(task)}>
          Delete
        </button>
      </div>
    </li>
  );
}
