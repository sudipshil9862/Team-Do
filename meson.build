project('todo_list', version: '0.1.0')

py_installation = import('python').find_installation('python3')

install_data('css/styles.css', install_dir: join_paths(get_option('datadir'), 'todo_list/css'))

run_target('run', command: [py_installation, join_paths(meson.source_root(), 'src', 'main.py')])
