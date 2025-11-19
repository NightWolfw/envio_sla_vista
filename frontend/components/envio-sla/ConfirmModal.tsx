"use client";

type Props = {
  title: string;
  description: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
};

export default function ConfirmModal({ title, description, confirmLabel, cancelLabel, onConfirm, onCancel }: Props) {
  return (
    <div className="modal-backdrop">
      <div className="modal max-w-lg">
        <div className="modal-header">
          <h3>{title}</h3>
        </div>
        <p className="text-sm text-textMuted">{description}</p>
        <div className="flex justify-end gap-3">
          <button type="button" className="secondary" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button type="button" className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-slate-900" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
