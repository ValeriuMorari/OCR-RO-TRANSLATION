from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from ocr_translation.errors import AppError
from ocr_translation.processor import process_document


BUTTON_TEXT = "CLICK AICI PENTRU A INCARCA PDF"
DONE_TEXT = "AM TERMINAT, BRAVO!, CU DRAG, VALERIU"


class OcrTranslationGui:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("OCR Translation")
        self.root.geometry("560x220")
        self.root.resizable(False, False)

        self._messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self._worker: threading.Thread | None = None

        container = tk.Frame(self.root, padx=28, pady=28)
        container.pack(fill=tk.BOTH, expand=True)

        self.button = tk.Button(
            container,
            text=BUTTON_TEXT,
            command=self._select_pdf,
            font=("Segoe UI", 14, "bold"),
            height=3,
            wraplength=440,
        )
        self.button.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="")
        self.status = tk.Label(
            container,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            anchor="center",
            wraplength=490,
            justify=tk.CENTER,
        )
        self.status.pack(fill=tk.X, pady=(22, 0))

    def run(self) -> None:
        self.root.mainloop()

    def _select_pdf(self) -> None:
        if self._worker and self._worker.is_alive():
            return

        selected = filedialog.askopenfilename(
            title="Selecteaza PDF",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not selected:
            return

        self._set_busy(True)
        self.status_var.set("Se proceseaza documentul...")

        self._worker = threading.Thread(
            target=self._process_in_background,
            args=(Path(selected),),
            daemon=True,
        )
        self._worker.start()
        self.root.after(150, self._poll_worker_messages)

    def _process_in_background(self, input_path: Path) -> None:
        try:
            process_document(input_path, progress=self._post_progress)
        except AppError as exc:
            self._messages.put(("error", str(exc)))
        except Exception as exc:
            self._messages.put(("error", f"Unexpected error: {exc}"))
        else:
            self._messages.put(("done", DONE_TEXT))

    def _post_progress(self, message: str) -> None:
        self._messages.put(("progress", message))

    def _poll_worker_messages(self) -> None:
        while True:
            try:
                kind, message = self._messages.get_nowait()
            except queue.Empty:
                break

            if kind == "progress":
                self.status_var.set(message)
            elif kind == "error":
                self._set_busy(False)
                self.status_var.set("")
                messagebox.showerror("Eroare", message)
                return
            elif kind == "done":
                self._set_busy(False)
                self.status_var.set("")
                messagebox.showinfo("Gata", message)
                return

        if self._worker and self._worker.is_alive():
            self.root.after(150, self._poll_worker_messages)

    def _set_busy(self, busy: bool) -> None:
        self.button.configure(state=tk.DISABLED if busy else tk.NORMAL)


def main() -> int:
    app = OcrTranslationGui()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
