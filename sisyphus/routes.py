from flask import Blueprint, render_template


bp = Blueprint('sisyphus', __name__)


@bp.route('/')
def index():
    return render_template("sisyphus/index.html", title='Sisyphus cooling')
