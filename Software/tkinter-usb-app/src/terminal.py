import os
from tkinter import (
    END,
    Button,
    Frame,
    Label,
    PhotoImage,
    Scrollbar,
    Text,
    Toplevel,
    ttk,
)


class _Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        try:
            widget.bind("<Enter>", self.show)
            widget.bind("<Leave>", self.hide)
        except Exception:
            pass

    def show(self, event=None):
        if self.tw:
            return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
            self.tw = Toplevel(self.widget)
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry(f"+{x}+{y}")
            label = Label(
                self.tw,
                text=self.text,
                bg="#ffffe0",
                relief="solid",
                borderwidth=1,
                padx=4,
                pady=1,
            )
            label.pack()
        except Exception:
            self.tw = None

    def hide(self, event=None):
        try:
            if self.tw:
                self.tw.destroy()
                self.tw = None
        except Exception:
            self.tw = None


class TerminalView:
    def __init__(self, parent, write_command=None):
        self.parent = parent
        self.write_command = write_command

        # Frame already provided as parent; create widgets inside
        self.terminal = Text(self.parent, height=15, width=30)
        # add left padding to the output area
        self.terminal.grid(row=0, column=0, sticky="nsew", padx=(6, 0))

        self.scrollbar = Scrollbar(self.parent, command=self.terminal.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.terminal["yscrollcommand"] = self.scrollbar.set

        # placeholder icons
        self.clear_icon = None
        self.send_icon = None
        self.stop_icon = None

        # make room for input area that aligns with the terminal (excluding scrollbar)
        self.input_frame = Frame(self.parent)
        # place input below the clear button so the trash icon sits above the input row
        # add a small bottom margin for breathing room under the input
        self.input_frame.grid(row=2, column=0, columnspan=1, sticky="we", pady=(0, 8))
        self.input_frame.grid_columnconfigure(0, weight=1)

        # history (displayed in combobox dropdown)
        self.input_history = []

        # input combobox (editable) showing history as a pull-down
        self.entry = ttk.Combobox(self.input_frame, values=self.input_history)
        # add left padding to the input so it's aligned with the output
        self.entry.grid(row=0, column=0, sticky="we", padx=(6, 4))
        self.entry.bind("<Return>", self._on_send)
        # remove arrow-key history navigation - combobox provides pull-down

        # load send icon if available (prefer send.png)
        def _load_image(rel_path, max_size=16):
            try:
                base = os.path.dirname(__file__)
                path = os.path.abspath(os.path.join(base, rel_path))
                if not os.path.exists(path):
                    return None
                img = PhotoImage(file=path)
                try:
                    h = img.height()
                    w = img.width()
                    if h > max_size or w > max_size:
                        factor_h = max(1, int(h / max_size))
                        factor_w = max(1, int(w / max_size))
                        factor = max(factor_h, factor_w)
                        img = img.subsample(factor, factor)
                except Exception:
                    pass
                return img
            except Exception:
                return None

        self.send_icon = _load_image(os.path.join("assets", "icons", "send.png"), 16)
        if self.send_icon:
            self.send_btn = Button(
                self.input_frame,
                image=self.send_icon,
                command=self._on_send,
                relief="flat",
                bd=0,
                highlightthickness=0,
            )
        else:
            self.send_btn = Button(self.input_frame, text="Send", command=self._on_send)
        self.send_btn.grid(row=0, column=1, pady=(0, 4))
        try:
            # attach simple tooltip to send button
            _Tooltip(self.send_btn, "Send")
        except Exception:
            pass

        # stop button: use icon if available, otherwise simple text fallback
        self.stop_icon = _load_image(os.path.join("assets", "icons", "stop.png"), 16)
        if self.stop_icon:
            self.stop_btn = Button(
                self.input_frame,
                image=self.stop_icon,
                command=self._on_stop,
                relief="flat",
                bd=0,
                highlightthickness=0,
            )
        else:
            self.stop_btn = Button(self.input_frame, text="STOP", command=self._on_stop)
        self.stop_btn.grid(row=0, column=2, padx=(4, 0), pady=(0, 4))
        try:
            _Tooltip(self.stop_btn, "Send STOP")
        except Exception:
            pass

        # clear button below input_frame, spanning the terminal column only
        # clear/trash button: prefer trash.png (slightly smaller max size)
        self.clear_icon = _load_image(os.path.join("assets", "icons", "trash.png"), 14)
        if self.clear_icon:
            self.clear_btn = Button(
                self.parent,
                image=self.clear_icon,
                command=self.clear,
                relief="flat",
                bd=0,
                highlightthickness=0,
            )
        else:
            self.clear_btn = Button(self.parent, text="Clear", command=self.clear)
        # position clear/trash between the terminal (row 0) and the input (row 2)
        # align to the right side of the terminal column
        self.clear_btn.grid(
            row=1, column=0, columnspan=1, pady=10, sticky="e", padx=(0, 6)
        )

        try:
            _Tooltip(self.clear_btn, "Clear terminal")
        except Exception:
            pass

    def set_write_command(self, fn):
        self.write_command = fn

    def _store_history(self, cmd):
        try:
            # Normalize history entries to uppercase for display
            if cmd is None:
                return
            item = str(cmd).strip().upper()
            if not item:
                return
            # Ensure each entry appears only once: remove existing occurrence
            try:
                while item in self.input_history:
                    self.input_history.remove(item)
            except Exception:
                pass
            # Append to end (most recent last)
            self.input_history.append(item)
            # Trim history to last 200 entries
            if len(self.input_history) > 200:
                self.input_history = self.input_history[-200:]
        except Exception:
            pass

    def _on_send(self, event=None):
        try:
            cmd = str(self.entry.get()).strip()
            if cmd:
                if callable(self.write_command):
                    try:
                        self.write_command(cmd)
                    except Exception as e:
                        self.update(f"Error sending command: {e}")
                # store history and update combobox values
                self._store_history(cmd)
                try:
                    self.entry["values"] = self.input_history
                except Exception:
                    pass
            # keep focus on input
            try:
                self.entry.focus_set()
            except Exception:
                pass
        except Exception as e:
            print(f"TerminalView send error: {e}")
        return "break"

    def _on_stop(self):
        try:
            # show STOP in entry
            try:
                try:
                    # combobox: set current value
                    self.entry.set("STOP")
                except Exception:
                    # fallback for Entry-like behavior
                    try:
                        self.entry.delete(0, END)
                        self.entry.insert(0, "STOP")
                    except Exception:
                        pass
                self.entry.focus_set()
            except Exception:
                pass
            if self.write_command:
                try:
                    self.write_command("STOP")
                except Exception as e:
                    self.update(f"Error sending STOP command: {e}")
        except Exception as e:
            print(f"TerminalView stop error: {e}")

    def _history_prev(self, event=None):
        # deprecated: arrow-key history navigation removed in favor of combobox pull-down
        return "break"

    def _history_next(self, event=None):
        # deprecated: arrow-key history navigation removed in favor of combobox pull-down
        return "break"

    def update(self, message):
        try:
            # If the underlying widget was destroyed, skip update
            if not getattr(self, "terminal", None):
                return
            try:
                if not self.terminal.winfo_exists():
                    return
            except Exception:
                # If winfo_exists isn't available for some reason, proceed and handle exceptions
                pass

            self.terminal.insert(END, message + "\n")
            self.terminal.see(END)
        except Exception as e:
            # Avoid noisy Tcl errors when the widget was destroyed concurrently
            print(f"TerminalView update error: {e}")

    def clear(self):
        try:
            if not getattr(self, "terminal", None):
                return
            try:
                if not self.terminal.winfo_exists():
                    return
            except Exception:
                pass
            self.terminal.delete(1.0, END)
        except Exception as e:
            print(f"TerminalView clear error: {e}")

    def get_input(self):
        try:
            return self.entry.get()
        except Exception:
            return ""

    def set_input(self, text):
        try:
            try:
                self.entry.set(text)
            except Exception:
                try:
                    self.entry.delete(0, END)
                    self.entry.insert(0, text)
                except Exception:
                    pass
        except Exception:
            pass

    def focus_input(self):
        try:
            self.entry.focus_set()
        except Exception:
            pass
