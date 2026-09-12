import { useState } from 'react';
import type { FormEvent } from 'react';

interface Props {
  disabled?: boolean;
  onCreate: (title: string) => Promise<void>;
}

export function TaskComposer({ disabled = false, onCreate }: Props) {
  const [title, setTitle] = useState('');
  const [busy, setBusy] = useState(false);

  const trimmed = title.trim();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!trimmed || busy) return;

    setBusy(true);
    try {
      await onCreate(trimmed);
      setTitle('');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <input
        className="composer__input"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        placeholder="What needs to be done?"
        maxLength={200}
        aria-label="New task title"
        disabled={disabled}
      />
      <button className="btn btn--primary" type="submit" disabled={disabled || !trimmed || busy}>
        Add
      </button>
    </form>
  );
}
