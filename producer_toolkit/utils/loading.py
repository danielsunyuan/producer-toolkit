"""
Loading animation utilities for better user experience.
"""

import sys
import time
import threading
from typing import Optional

class Spinner:
    """Simple spinning animation for loading indicators."""
    
    _spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message: str = "Loading", delay: float = 0.1):
        """
        Initialize a spinner.
        
        Args:
            message: Message to display before the spinner
            delay: Delay between spinner frames in seconds
        """
        self.message = message
        self.delay = delay
        self.spinning = False
        self._thread: Optional[threading.Thread] = None
    
    def _spin(self):
        """Internal method to run the spinner animation."""
        while self.spinning:
            for char in self._spinner_chars:
                if not self.spinning:
                    break
                sys.stdout.write(f'\r{self.message} {char}')
                sys.stdout.flush()
                time.sleep(self.delay)
    
    def start(self):
        """Start the spinner animation."""
        if self.spinning:
            return
        
        self.spinning = True
        self._thread = threading.Thread(target=self._spin)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self, final_message: Optional[str] = None):
        """
        Stop the spinner animation.
        
        Args:
            final_message: Optional message to display after stopping
        """
        if not self.spinning:
            return
        
        self.spinning = False
        if self._thread:
            self._thread.join()
        
        # Clear the spinner line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        
        if final_message:
            print(final_message)
        sys.stdout.flush()


def loading(message: str, delay: float = 0.1):
    """
    Context manager for loading animations.
    
    Usage:
        with loading("Downloading audio..."):
            # do work here
            pass
    """
    spinner = Spinner(message, delay)
    spinner.start()
    
    class LoadingContext:
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            spinner.stop()
            return False
    
    return LoadingContext()

