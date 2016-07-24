import re

class Indents:
    UNKNOWN = 0
    SPACES = 1
    TABS = 2

    __slots__ = ['kind', 'width']
    def __init__(self, kind=UNKNOWN, width=0):
        self.kind = kind
        self.width = width


class Location:
    def __init__(self, begin=-1, end=-1):
        self.begin = begin
        self.end = end


class _LineInfo:
    def __init__(self, kind=Indents.UNKNOWN):
        self.kind = kind
        self.whitespaces = []


    def tab_columns_pos(self, ts):
        pos_list = []
        diff = 0

        for ws in self.whitespaces:
            width = ws.end - ws.begin
            pos = ws.begin + diff   # accommodate for previous tabs
            pos = pos // ts + width # convert to tabstop count
            pos *= ts               # and back to characters
            pos_list.append(pos)
            diff = pos - ws.end

        return pos_list


    def cmp_columns_pos(a, b):
        for i in range(0, min(len(a), len(b))):
            if a[i] != b[i]:
                return False

        return True


class Scanner:

    def __init__(self):
        self.modelines = 0
        self.tabstop_priority = [4, 8, 2]
        self.min_lines = 0
        self.max_lines = -1

        self.modeline_re = re.compile(r'.*(?:(?:^| )vim?| ex):.*')


    def scan(self, lines):
        if self._has_modeline(lines):
            return Indents()

        scores = {
            Indents.SPACES: {0:0},
            Indents.TABS: {0:0}
        }
        prev_w = 0
        prev_rel_w = 0
        prev_info = _LineInfo()

        for line in lines[:self.max_lines]:
            info = self._scan_line(line)
            width = 0

            if info.kind == Indents.SPACES:
                indent = info.whitespaces[0]
                w = indent.end - indent.begin
                rel_w = abs(prev_w - w)
                if rel_w > 0:
                    prev_rel_w = rel_w
                    if(w % rel_w == 0):
                        width = rel_w
                elif prev_w == w:
                    if(w % prev_rel_w == 0):
                        width = prev_rel_w
                else:
                    width = 0

                if width > 0:
                    if width not in scores[Indents.SPACES]:
                        scores[Indents.SPACES][width] = 0
                    scores[Indents.SPACES][width] += 1

                prev_w = w

            elif info.kind == Indents.TABS:
                if len(info.whitespaces) > 1 and len(prev_info.whitespaces) > 1:
                    # TODO: collect info from succesive lines with the same
                    #       indent, then compare them all
                    for ts in self.tabstop_priority:
                        ts = int(ts)
                        prev_cols = prev_info.tab_columns_pos(ts)
                        cols = info.tab_columns_pos(ts)

                        if _LineInfo.cmp_columns_pos(prev_cols, cols):
                            if ts not in scores[Indents.TABS]:
                                scores[Indents.TABS][ts] = 0
                            scores[Indents.TABS][ts] += 1

                    prev_whitespaces = info.whitespaces
                else:
                    prev_whitespaces = []

            if info.kind != Indents.UNKNOWN:
                prev_info = info
                scores[info.kind][0] += 1

        spaces_score = scores[Indents.SPACES][0]
        tabs_score = scores[Indents.TABS][0]
        # Too few indents, sorry
        if spaces_score + tabs_score < self.min_lines:
            return Indents()

        best = Indents()
        if spaces_score > tabs_score:
            best.kind = Indents.SPACES
            scores[Indents.SPACES].pop(0, None)
            if scores[Indents.SPACES]:
                best.width = max(scores[Indents.SPACES],
                                 key=scores[Indents.SPACES].get)
        elif tabs_score > spaces_score:
            best.kind = Indents.TABS
            scores[Indents.TABS].pop(0, None)
            # In a case where two widths have the same score, max() would
            # return the first one from the dictionary, which is not necessary
            # the one with larger priority.
            best_width_score = 0
            for ts in self.tabstop_priority:
                ts = int(ts)
                if scores[Indents.TABS].get(ts, 0) > best_width_score:
                    best_width_score = scores[Indents.TABS][ts]
                    best.width = ts
            # Too few columns, ignore tab width
            if best_width_score < self.min_lines:
                best.width = 0

        return Indents(best.kind, best.width)


    def _scan_line(self, line):
        line += '\0' # HACK: handle whitespace-only lines
        info = _LineInfo()
        ws_c = None

        START, START_ONE_SPACE, ONE_SPACE, IN_WHITESPACE, IN_TEXT = range(0, 5)
        state = START
        for i in range(0, len(line)):
            if state == START:
                if line[i] == ' ':
                    ws = Location(i)
                    state = START_ONE_SPACE
                elif line[i] == '\t':
                    ws = Location(i)
                    ws_c = '\t'
                    state = IN_WHITESPACE
            elif state == START_ONE_SPACE:
                if line[i] == ' ':
                    if ws.begin != 0: # For spaces, search for indents only
                        break
                    ws_c = ' '
                    state = IN_WHITESPACE
                else:
                    state = START
            elif state == IN_WHITESPACE:
                if line[i] != ws_c:
                    # FIXME: WORKAROUND:
                    # In a files with multiline C-like comments where stars
                    # are aligned vertically, there is one additional space.
                    # This results in invalid one-space width detected in
                    # a files with large amount of comments (documentation).
                    #
                    # The comment looks like:
                    # /*
                    #  *  <- +1 space!
                    #  */ <- +1 space!
                    #
                    # For now, ignore additional space if the indent width
                    # is odd. This should break only real odd-width space
                    # indents where a lot of multiplication is moved to
                    # a following line.
                    #
                    # It would be better to detect common line continuation
                    # patterns (like ',' at the end of a line, block comments,
                    # etc) and fix detected values.
                    if (ws_c == ' ' and line[i] == '*'
                            and (i - ws.begin) % 2 != 0):
                        ws.end = i - 1
                    else:
                        ws.end = i

                    info.whitespaces.append(ws)
                    if ws_c == ' ':  # For spaces, search for indents only
                        break
                    state = IN_TEXT
            elif state == ONE_SPACE:
                state = IN_WHITESPACE if line[i] == ' ' else IN_TEXT
            elif state == IN_TEXT:
                if line[i] == ws_c:
                    ws = Location(i)
                    state = ONE_SPACE if ws_c == ' ' else IN_WHITESPACE

        if ws_c == ' ':
            info.kind = Indents.SPACES
        elif ws_c == '\t':
            info.kind = Indents.TABS

        return info


    def _has_modeline(self, lines):
        nb = len(lines)

        for n in range(0, self.modelines):
            if self.modeline_re.match(lines[n]):
                return True

            nb = nb - 1
            if nb <= n:
                break

            if self.modeline_re.match(lines[nb]):
                return True

        return False
