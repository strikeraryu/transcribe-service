from flask import Blueprint

core_bp = Blueprint('core', __name__)

@core_bp.route('/health_check')
def health_check():
    return 'OK'
