from flask import render_template, request, redirect, jsonify
from flask_login import login_user, login_required, logout_user

from app import app, dao, login, db

from app import staff, admin
from models import QuyDinhEnum, QuyDinh


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/index.html', methods=['GET'])
def home1():
    return render_template('index.html')


@app.route("/admin/login", methods=['GET', 'POST'])
def login_admin():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.authenticate_user(username, password)
        if user is not None:
            login_user(user)
            return redirect('/admin')
        else:
            error = 'Thong tin dang nhap sai'

    return render_template('login.html', error=error)


@app.route('/about.html', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/testimonial.html', methods=['GET'])
def testimonial():
    return render_template('testimonial.html')


@app.route('/contact.html', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/booking.html')
def booking_view():
    phong_trong = dao.get_phong_trong()
    so_nguoi = dao.get_nguoi_toi_da()
    return render_template('booking.html', phong_trong=phong_trong, so_nguoi=so_nguoi)


@app.route('/room.html', methods=['GET'])
def room():
    return render_template('room.html')


@app.route('/api/booking', methods=['POST'])
def booking():
    data = request.json
    ten_nguoi_dat = data.get('ten_nguoi_dat')
    ngay_dat_phong = data.get('ngay_dat_phong')
    ngay_tra_phong = data.get('ngay_tra_phong')
    cac_chi_tiet_dat_phong = data.get('cac_chi_tiet_dat_phong')

    # try:
    #     dao.dat_phong(ten_nguoi_dat, ngay_dat_phong, ngay_tra_phong, cac_chi_tiet_dat_phong)
    # except Exception as e:
    #     return str(e), 500
    dao.dat_phong(ten_nguoi_dat, ngay_dat_phong, ngay_tra_phong, cac_chi_tiet_dat_phong)

    return jsonify('')


@app.route('/api/baocaodoanhthu', methods=['GET'])
def stats_sale():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    return dao.stats_sale(from_date, to_date)

@app.route('/api/baocaomatdo', methods=['GET'])
def stats_mat_do():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    return dao.stats_mat_do(from_date, to_date)
@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/api/tinhtienphong', methods=['POST'])
def tinh_tien_phong():
    data = request.json
    cac_chi_tiet_dat_phong = data.get('cac_chi_tiet_dat_phong')

    return jsonify({'tong_tien': dao.tinh_tien_phieu_dat(cac_chi_tiet_dat_phong)})

def khoi_tao_quy_dinh():
    quy_dinh = [
        (QuyDinhEnum.SO_KHACH_TOI_DA_TRONG_PHONG, 3),
        (QuyDinhEnum.SO_LUONG_KHACH_PHU_THU, 3),
        (QuyDinhEnum.TY_LE_PHU_THU, 150),
    ]

    for key, value in quy_dinh:
        quy_dinh_db = db.session.query(QuyDinh).filter_by(key=key).first()
        if quy_dinh_db is None:
            quy_dinh_db = QuyDinh(key=key, value=value)
            db.session.add(quy_dinh_db)
            db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        khoi_tao_quy_dinh()

    app.run(debug=True)
    # app.run()
