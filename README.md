Indenty
=======

Vim plugin that detects what indent options were used in the file and sets them.

## Description

Indenty detects **indent type** (tabs/spaces, *expandtab*), and **indent size** (*shiftwidth*/[*soft*]*tabstop*) for spaces. The latter is sometimes detected for tabs, but requires a columns indented inside the text with varying number of tabs, e.g.:

```
/* good look with ts=4 */
struct example {
⇥   int⇥⇥   tabstop;
⇥   int⇥⇥   softtabstop;
⇥   int⇥⇥   shiftwidth
⇥   bool⇥   tabstop
};

/* messed up with ts=8 */
struct example {
⇥       int⇥    ⇥       tabstop;
⇥       int⇥    ⇥       softtabstop;
⇥       int⇥    ⇥       shiftwidth;
⇥       bool⇥   expandtab;
};
```

Tabstop detection for tabs uses **configurable priorities**. The default priorities are [4, 8, 2], so 4 was chosen in the example, despite the fact that it also looks good with *tabstop* set to 2.

Only the **current file** is scanned. By default, the plugin **respects modelines** in a 5 first/last lines and stops detection when it is found. Nothing is changed also when the detection fails to find something reasonable.

## Requirements

Vim with Python 3. Python 2 might work, it is not tested yet.

## Settings

 Option                      | Type    | Description
-----------------------------|---------|----------------------------------------
`g:indenty_tabstop_priority` | list    | Specifies what *tabstop* widths to check when the tab indentation is detected. The first good looking width is used.
`g:indenty_modelines`        | number  | The number of lines that are checked for a *modeline* presence.
`g:indenty_blacklist`        | list    | Filetypes for which **automatic** detection is not triggered. `IndentyDetect()` still works.
`g:indenty_min_lines`        | number  | The minimum number of indented lines required to set detected settings.
`g:indenty_max_lines`        | number  | The maximum number of lines that are scanned.
`g:indenty_show_msg`         | boolean | Specifies whether to show message with detected settings.
`g:indenty_onload`           | boolean | When on, the file is scanned automatically when it is opened.
`g:indenty_msg_as_warning`   | boolean | When on, message is displayed as a warning.

Defaults:

```
g:indenty_tabstop_priority  = [4, 8, 2]
g:indenty_modelines         = &modelines
g:indenty_blacklist         = ['help', 'man', '', 'make']
g:indenty_min_lines         = 4
g:indenty_max_lines         = 1024
g:indenty_show_msg          = 1
g:indenty_onload            = 1
```

## Commands

 Function         | Description
------------------|-------------------------------------------------------------
`IndentyDetect()` | Triggers detection.

