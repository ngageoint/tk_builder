"""
Sets out the main interface for something which provides image data.
"""

__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


import logging
import tkinter


class TextHandler(logging.Handler):
    """
    This class allows you to log to a Tkinter Text or ScrolledText widget
    """

    def __init__(self, text):
        """

        Parameters
        ----------
        text : tkinter.Text
            A tkinter text type object.
        """

        logging.Handler.__init__(self)
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(tkinter.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tkinter.END)

        self.text.after(0, append)

    def clear(self):
        """
        Clear the text widget.
        """

        self.text.configure(state='normal')
        self.text.delete('1.0', 'end')
        self.text.configure(state='disabled')

    def get_value(self):
        """
        Fetches the string value of the widget.

        Returns
        -------
        str
        """

        return self.text.get("1.0", 'end')

    def save_to_file(self, filename):
        """
        Save the text contents to a file.

        Parameters
        ----------
        filename : str
        """

        with open(filename, 'w') as fi:
            fi.write(self.get_value())
