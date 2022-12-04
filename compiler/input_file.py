class InputFile(object):

    def __init__(self, file_path):
        f = open(file_path, "r")
        self.lines = f.readlines()
        self.line_num = len(self.lines)
        self.line_len = [len(line) for line in self.lines]
        self.cur_col = 0
        self.cur_line = 0

    def getch(self):
        if self.cur_line >= self.line_num:
            return (None, None)
        if self.cur_col >= self.line_len[self.cur_line]:
            self.cur_col = 0
            self.cur_line += 1
            return self.getch()
        ch = (self.lines[self.cur_line][self.cur_col], self.cur_line)
        self.cur_col += 1
        return ch

    def retract(self):
        self.cur_col -= 1
