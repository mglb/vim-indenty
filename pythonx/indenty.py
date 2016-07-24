import vim
from indenty.scanner import Scanner, Indents


scanner = Scanner()

scanner.modelines           = vim.vars['indenty_modelines']
scanner.tabstop_priority    = vim.vars['indenty_tabstop_priority']
scanner.min_lines           = vim.vars['indenty_min_lines']
scanner.max_lines           = vim.vars['indenty_max_lines']


def detect():
    b = vim.current.buffer
    indents = scanner.scan(b)

    # Set options if detected
    if indents.kind == Indents.SPACES:
        b.options['et']     = True
    elif indents.kind == Indents.TABS:
        b.options['et']     = False
    if indents.width > 0:
        b.options['sw']     = indents.width
        b.options['ts']     = indents.width
        b.options['sts']    = indents.width

    return vim.List([indents.kind, indents.width])
