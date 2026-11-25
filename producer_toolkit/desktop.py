"""Small local desktop front end for the canonical PTK CLI."""
from pathlib import Path
import queue
import subprocess
import sys
import threading

from .limits import public_message
from .runtime import process_environment

OPERATIONS = {
    'Four stems': ['-s', '-n', '4'],
    'Vocals + accompaniment': ['-s', '-n', '2'],
    'Analyze local audio': ['--analyze'],
    'Download audio': ['-a'],
    'Compatible MP4': ['-v'],
    'Best source video': ['-v', '--video-quality', 'best'],
}


def command_for(source, operation, output, metadata=False, analyze=True):
    if not source.strip():
        raise ValueError('Choose an audio file or enter a video URL.')
    if operation not in OPERATIONS:
        raise ValueError('Choose a supported operation.')
    command = [sys.executable, '-m', 'producer_toolkit', source, *OPERATIONS[operation]]
    if operation != 'Analyze local audio':
        if not output.strip():
            raise ValueError('Choose an output folder.')
        command += ['-o', output]
    if operation in ('Four stems', 'Vocals + accompaniment') and not analyze:
        command.append('--no-analysis')
    if metadata and operation != 'Analyze local audio':
        command.append('--metadata')
    return command


class Desktop:
    def __init__(self, root):
        import tkinter as tk
        from tkinter import filedialog, messagebox, scrolledtext, ttk
        self.root, self.tk = root, tk
        self.filedialog, self.messagebox = filedialog, messagebox
        self.busy = False
        self.events = queue.Queue(maxsize=1000)
        self.source = tk.StringVar()
        self.output = tk.StringVar(value=str(Path.home() / 'Downloads'))
        self.operation = tk.StringVar(value='Four stems')
        self.metadata = tk.BooleanVar(value=False)
        self.analyze = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value='Ready')
        root.title('PTK — Producer Toolkit')
        root.minsize(740, 520)
        root.protocol('WM_DELETE_WINDOW', self.close)
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(9, weight=1)
        ttk.Label(frame, text='Producer Toolkit', font=('Helvetica', 20, 'bold')).grid(row=0, column=0, columnspan=3, sticky='w')
        ttk.Label(frame, text='Prepare media and aligned stems locally. CPU processing.').grid(row=1, column=0, columnspan=3, sticky='w', pady=(4, 18))
        ttk.Label(frame, text='Source').grid(row=2, column=0, sticky='w', padx=(0, 12))
        ttk.Entry(frame, textvariable=self.source, width=55).grid(row=2, column=1, sticky='ew')
        ttk.Button(frame, text='Choose file', command=self.browse_source).grid(row=2, column=2, padx=(8, 0))
        ttk.Label(frame, text='Operation').grid(row=3, column=0, sticky='w', pady=10)
        ttk.Combobox(frame, textvariable=self.operation, values=list(OPERATIONS), state='readonly').grid(row=3, column=1, sticky='ew')
        ttk.Label(frame, text='Output folder').grid(row=4, column=0, sticky='w')
        ttk.Entry(frame, textvariable=self.output).grid(row=4, column=1, sticky='ew')
        ttk.Button(frame, text='Choose folder', command=self.browse_output).grid(row=4, column=2, padx=(8, 0))
        ttk.Checkbutton(frame, text='Estimate tempo and key for stems', variable=self.analyze).grid(row=5, column=1, sticky='w', pady=(12, 0))
        ttk.Checkbutton(frame, text='Save download provenance', variable=self.metadata).grid(row=6, column=1, sticky='w')
        self.run_button = ttk.Button(frame, text='Run', command=self.run)
        self.run_button.grid(row=7, column=0, sticky='w', pady=14)
        ttk.Label(frame, textvariable=self.status).grid(row=7, column=1, columnspan=2, sticky='w')
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        self.log = scrolledtext.ScrolledText(frame, height=12, state='disabled', wrap='word')
        self.log.grid(row=9, column=0, columnspan=3, sticky='nsew')
        ttk.Label(frame, text='Development build. Pretrained model licensing is unresolved; see the model notes before commercial use.',
                  wraplength=680).grid(row=10, column=0, columnspan=3, sticky='w', pady=(12, 0))
        ttk.Button(frame, text='Model licence notes', command=self.model_notes).grid(row=11, column=0, columnspan=2, sticky='w', pady=(8, 0))
        self.poll_id = root.after(100, self.poll)

    def browse_source(self):
        path = self.filedialog.askopenfilename(title='Choose source audio')
        if path:
            self.source.set(path)

    def browse_output(self):
        path = self.filedialog.askdirectory(title='Choose output folder')
        if path:
            self.output.set(path)

    def model_notes(self):
        import webbrowser
        webbrowser.open('https://github.com/adefossez/demucs#license')

    def run(self):
        if self.busy:
            return
        try:
            command = command_for(self.source.get(), self.operation.get(), self.output.get(),
                                  self.metadata.get(), self.analyze.get())
        except ValueError as error:
            self.messagebox.showerror('PTK', str(error), parent=self.root)
            return
        self.busy = True
        self.run_button.configure(state='disabled')
        self.status.set('Running — see log for progress')
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')
        self.progress.start()
        threading.Thread(target=self.worker, args=(command,), daemon=True).start()

    def worker(self, command):
        environment = process_environment()
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, encoding='utf-8', errors='replace', env=environment) as process:
                for line in process.stdout:
                    self.events.put(('line', public_message(line.rstrip())))
                code = process.wait()
        except (OSError, ValueError) as error:
            self.events.put(('line', public_message(error)))
            code = 1
        self.events.put(('done', code))

    def poll(self):
        for _ in range(100):
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == 'line':
                self.log.configure(state='normal')
                self.log.insert('end', value + '\n')
                if int(self.log.index('end-1c').split('.')[0]) > 2000:
                    self.log.delete('1.0', '2.0')
                self.log.see('end')
                self.log.configure(state='disabled')
            else:
                self.busy = False
                self.progress.stop()
                self.run_button.configure(state='normal')
                self.status.set('Finished' if value == 0 else f'Failed — exit {value}; see log')
        self.poll_id = self.root.after(100, self.poll)

    def close(self):
        if self.busy:
            self.messagebox.showinfo('PTK', 'A job is still running. Wait for it to finish before closing.', parent=self.root)
            return
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def main():
    try:
        import tkinter as tk
        root = tk.Tk()
    except ImportError:
        print('PTK desktop needs Python with Tk support. Install Python 3.11 from python.org, or a Tk-enabled Python build.', file=sys.stderr)
        return 1
    except tk.TclError:
        print('PTK desktop needs a working desktop display and Tk installation. The CLI remains available.', file=sys.stderr)
        return 1
    Desktop(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
