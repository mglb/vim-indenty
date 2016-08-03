if !(has ('python') || has('python3')) || &compatible || exists("g:loaded_indenty")
    finish
endif
let g:loaded_indenty = 1

if has('python3')
    let s:pyfile="py3file "
    let s:Py=function("py3eval")
else
    let s:pyfile="pyfile "
    let s:Py=function("pyeval")
endif

" Default settings

let g:indenty_tabstop_priority = get(g:, 'indenty_tabstop_priority', [4, 8, 2])
let g:indenty_modelines = get(g:, 'indenty_modelines', &modelines)
let g:indenty_blacklist = get(g:, 'indenty_blacklist', ['', 'make'])
let g:indenty_min_lines = get(g:, 'indenty_min_lines', 4)
let g:indenty_max_lines = get(g:, 'indenty_max_lines', 1024)
let g:indenty_show_msg = get(g:, 'indenty_show_msg', 1)
let g:indenty_onload = get(g:, 'indenty_onload', 1)
let g:indenty_msg_as_warning = get(g:, 'indenty_msg_as_warning', 1)
let g:indenty_msg_detailed = get(g:, 'indenty_msg_detailed', 0)

" Load python part

let s:python_dir = resolve(expand('<sfile>:h').'/../pythonx/')
exec s:pyfile.s:python_dir.'/indenty.py'

" User functions

function! IndentyDetect()
    let indents = s:Py('detect()')

    if indents[0] != 0 && g:indenty_show_msg
        call s:IndentyMsg(indents, 0)
    endif
endfunc

" Autoload and messages

function! s:IndentyMsg(indents, with_last_msg)
    let s:last_msg = ''
    if a:with_last_msg
        " Instead of getting the 'press ENTER...' or removing the default file
        " info message, re-display the message with additional info.
        redraw
        redir => s:messages
        silent! messages
        redir END
        let s:last_msg=get(split(s:messages, "\n"), -1, '')

        if s:last_msg != ""
            let s:last_msg = s:last_msg.'; '
        endif
    endif

    redraw
    if g:indenty_msg_as_warning
        echohl WarningMsg
    endif

    if g:indenty_detailed_msg
        echo s:last_msg.'indenty: '.(&et?'et':'noet').',ts='.&ts.',sw='.&sw
    else
        let s:kind_str = 'spaces'
        if a:indents[0] == 2
            let s:kind_str = 'tabs'
        endif

        let s:width_str = ''
        if a:indents[1] > 0
            let s:width_str = ' ('.a:indents[1].')'
        endif

        echo s:last_msg.'indenty: '.s:kind_str.s:width_str
    endif

    if g:indenty_msg_as_warning
        echohl None
    endif
endfunc


function! s:IndentyAutoDetect()
    for ft in g:indenty_blacklist
        if ft == &filetype
            return
        endif
    endfor

    let indents = s:Py('detect()')

    if indents[0] != 0 && g:indenty_show_msg
        call s:IndentyMsg(indents, 1)
    endif
endfunc

if g:indenty_onload
    aug Indenty
        au!
        au BufRead * :call s:IndentyAutoDetect()
    aug end
endif

