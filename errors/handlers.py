from flask import Blueprint, redirect, url_for, flash, session


def not_found_error(error):
    flash('Oops, that page couldn\'t be found. (404)', 'danger')
    return redirect(url_for('main.index'))

def internal_server_error(error):
    flash('Oops, something went wrong. That\'s probably my fault. (500)', 'danger')
    if 'timetable' in session and session['timetable']:
        return redirect(url_for('timetable.index'))
    return redirect(url_for('main.index'))
