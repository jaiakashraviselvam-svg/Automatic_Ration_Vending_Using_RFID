from flask import Flask
from models import db, User
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'rationvending'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ration_vending.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Razorpay credentials (replace with your actual test/live keys)
    app.config['RAZORPAY_KEY_ID'] = 'rzp_test_SptV17ZjerwEjC'
    app.config['RAZORPAY_KEY_SECRET'] = 'waYzGgNHYmvHguD9vdDBhKwI'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    from flask import request, redirect, url_for
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.blueprint == 'admin':
            return redirect(url_for('admin.login'))
        return redirect(url_for('main.login'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
