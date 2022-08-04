from sys import stdout

class Progress():
    def __init__(self, total, text="Progress: ", verbose=True):
        self.total = total
        self.perc = 0
        self.text = text
        self.verbose = verbose
        
    def print_progress(self, n):
        if self.verbose:
            p = int(((n / self.total) * 100))
            if self.perc != p and self.perc < 100:
                self.perc = p
                stdout.write(f"\r{self.text}{self.perc : >3}%")
                stdout.flush()
                if self.perc == 100:
                    print("")
