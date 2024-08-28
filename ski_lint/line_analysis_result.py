class LineAnalysisResult:
    def __init__(self, line_num: int, line: str) -> None:
        self.line_num = line_num
        self.line = line.rstrip("\r\n")
        self.chars: dict[str, list[int]] = {}

    def add_char(self, char: str, char_pos: int) -> None:
        self.chars.setdefault(char, []).append(char_pos)
