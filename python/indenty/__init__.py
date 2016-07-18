from indenty.scanner import Scanner, Indents
try:
    import vim
except ImportError:
    vim = object()

def detect():
    scanner = Scanner()
    scanner.modelines = int(vim.eval('g:indenty_modelines'))
    scanner.tabstop_priority = vim.eval('g:indenty_tabstop_priority')
    scanner.min_lines = int(vim.eval('g:indenty_min_lines'))
    scanner.max_lines = int(vim.eval('g:indenty_max_lines'))

    indents = scanner.scan(vim.current.buffer)

    # Let VimL part know what happened
    vim.command("let indents = [%u, %u]" % (indents.kind, indents.width))

    # Set options if detected
    if indents.kind == Indents.SPACES:
        vim.command("setlocal et")
    elif indents.kind == Indents.TABS:
        vim.command("setlocal noet")
    if indents.width > 0:
        vim.command("setlocal sw={0} ts={0} sts={0}".format(indents.width))

