
from flask import Blueprint, render_template,jsonify,redirect,request, url_for, session,send_file,flash
from app.logic.services import create_performance_graph, create_trend_graph
from app.logic.services import generate_alerts
from app.data.models import get_sensor_info
import plotly.io as pio
from fpdf import FPDF
import io
from app.logic.services import query_data  # Assuming query_data gets the required data
from app.auth.auth_logic import authenticate_user, register_user, approve_user, deny_user, get_pending_users,login_required
import plotly.graph_objs as go
from app.logic.services import get_temperature_highlights
from app.logic.services import get_thresholds, set_thresholds
from app.logic.services import create_historical_graph


views = Blueprint('views', __name__)

# Admin credentials
ADMIN_USER = "etm"

@views.route('/')
@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Save the selected sensor group in the session
        sensor_group = request.form.get('sensor_group')
        if sensor_group:
            session['sensor_group'] = sensor_group
            flash(f"Sensor group updated to {sensor_group}.", "success")
        else:
            flash("Please select a valid sensor group.", "error")

    return render_template('dashboard.html', page_id="dashboard", sensor_group=session.get('sensor_group', 'All'))

sensor_coordinates = [{'coords': '205,103,15'}, {'coords': '235,86,12'}, {'coords': '261,74,12'}, {'coords': '452,121,12'}, {'coords': '553,103,12'}, {'coords': '429,142,12'}, {'coords': '460,149,12'}, {'coords': '525,88,12'}, {'coords': '463,726,12'}, {'coords': '494,716,12'}, {'coords': '523,704,15'}, {'coords': '298,641,14'}, {'coords': '86,571,12'}, {'coords': '71,540,14'}, {'coords': '253,417,15'}, {'coords': '253,375,15'}, {'coords': '74,333,14'}, {'coords': '418,546,16'}, {'coords': '681,463,15'}, {'coords': '501,414,15'}, {'coords': '502,375,16'}, {'coords': '359,273,15'}, {'coords': '441,569,15'}, {'coords': '43,338,14'}, {'coords': '50,309,14'}, {'coords': '60,280,12'}, {'coords': '71,249,14'}, {'coords': '86,221,12'}, {'coords': '292,64,12'}, {'coords': '285,96,12'}, {'coords': '315,88,14'}, {'coords': '435,58,16'}, {'coords': '466,64,14'}, {'coords': '670,222,12'}, {'coords': '686,250,14'}, {'coords': '698,278,14'}, {'coords': '705,309,11'}, {'coords': '714,341,12'}, {'coords': '714,452,12'}, {'coords': '707,481,14'}, {'coords': '697,513,14'}, {'coords': '684,541,14'}, {'coords': '669,569,12'}, {'coords': '432,732,12'}, {'coords': '471,693,15'}, {'coords': '442,701,14'}, {'coords': '292,725,12'}, {'coords': '261,715,12'}]

@views.route('/variables')
@login_required
def variables():
    sensor_info = get_sensor_info() 
    sensors = [
        {**info, **coord}
        for info, coord in zip(sensor_info, sensor_coordinates)
    ]
    return render_template('variables.html', sensors=sensors, page_id="variables")

@views.route('/alerts')
@login_required
def alerts():
    return render_template('alerts.html', page_id="alerts")

@views.route('/reports')
@login_required
def reports():
    return render_template('reports.html', page_id="reports")

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'time_range':
            # Handle time range selection
            time_range = request.form.get('time_range')
            if time_range:
                session['time_range'] = time_range
                flash(f"Time range updated to {time_range}.", "success")
            else:
                flash("Please select a valid time range.", "error")

        elif form_type == 'thresholds':
            # Handle threshold updates
            try:
                max_threshold = int(request.form['max_threshold'])
                min_threshold = int(request.form['min_threshold'])

                # Validate the input values
                if min_threshold >= max_threshold:
                    flash("Minimum threshold must be less than the maximum threshold.", "error")
                else:
                    set_thresholds(max_threshold, min_threshold)
                    flash("Threshold values updated successfully.", "success")
            except ValueError:
                flash("Please enter valid integer values.", "error")

        return redirect(url_for('views.settings'))

    thresholds = get_thresholds()
    time_range = session.get('time_range', '1m')  # Default to 1 minute if not set
    return render_template('settings.html', page_id="settings", thresholds=thresholds, time_range=time_range)

@views.route('/api/performance_data')
def get_performance_data():
    performance_graph = create_performance_graph()
    return jsonify(pio.to_json(performance_graph))

@views.route('/api/trend_data')
def get_trend_data():
    trend_graph = create_trend_graph()
    return jsonify(pio.to_json(trend_graph))

@views.route('/api/alerts')
def get_alerts():
    # Return the generated alerts in JSON format
    alerts = generate_alerts()
    return jsonify(alerts)

@views.route('/generate_report', methods=['GET'])
def generate_report():
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            # Adjust the x position for the logo to be on the right
            self.image('app/static/images/javeranaLogo.png', 160, 8, 33)  # 170 aligns it to the right for a standard A4 page
            self.cell(0, 10, 'Sensor Data Report', border=0, ln=True, align='C')

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    # Fetch and process data
    df = query_data()
    df['sensor_number'] = df['name'].str.extract(r'voltage_(\d+)\.value$')[0].astype(int)
    sensor_stats = df.groupby('sensor_number')['original_value_float'].agg(['mean', 'std']).reset_index()

    overall_mean = df['original_value_float'].mean()
    overall_std = df['original_value_float'].std()

    # Create PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Number of Sensors: {len(sensor_stats)}", ln=True)
    pdf.cell(0, 10, f"Overall Mean Temperature: {overall_mean:.2f}°C", ln=True)
    pdf.cell(0, 10, f"Overall Standard Deviation: {overall_std:.2f}°C", ln=True)

    # Add table header
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Sensor', 1)
    pdf.cell(60, 10, 'Average Temperature (°C)', 1)
    pdf.cell(60, 10, 'Standard Deviation', 1)
    pdf.ln()

    # Add sensor statistics to the table
    pdf.set_font('Arial', '', 12)
    for _, row in sensor_stats.iterrows():
        pdf.cell(40, 10, str(int(row['sensor_number'])), 1)
        pdf.cell(60, 10, f"{row['mean']:.2f}", 1)
        pdf.cell(60, 10, f"{row['std']:.2f}", 1)
        pdf.ln()

    # Save PDF to a BytesIO object
    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)

    return send_file(pdf_output, mimetype='application/pdf', as_attachment=True, download_name='sensor_report.pdf')


@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        auth_result = authenticate_user(username, password)

        if auth_result is True:
            session["username"] = username
            return redirect(url_for("views.dashboard"))
        elif auth_result == "not_approved":
            return "Your account is not approved yet."
        else:
            return "Invalid credentials."
    return render_template("auth_login.html")

@views.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        register_user(username, password)
        return "Registration successful. Wait for admin approval."
    return render_template("auth_register.html")

@views.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if session.get("username") != ADMIN_USER:
        return "Access denied."

    if request.method == "POST":
        if "approve" in request.form:
            approve_user(request.form["username"])
        elif "deny" in request.form:
            deny_user(request.form["username"])

    pending_users = get_pending_users()
    return render_template("admin_approval.html", pending_users=pending_users)

@views.route('/logout')
@login_required
def logout():
    session.clear()  # Clear the session
    return redirect(url_for("views.login"))  # Redirect to the login page

@views.route('/api/temperature_highlights', methods=['GET'])
def get_temperature_highlights_api():
    highlights = get_temperature_highlights()
    return jsonify(highlights)

@views.route('/api/histogram_data', methods=['GET'])
def get_histogram_data():
    df = query_data()
    histogram_data = go.Histogram(x=df['original_value_float'])
    layout = go.Layout(title="Temperature Distribution", xaxis_title="Temperature (°C)", yaxis_title="Frequency")
    return jsonify(pio.to_json({"data": [histogram_data], "layout": layout}))

@views.route('/api/std_data', methods=['GET'])
def get_std_data():
    df = query_data()
    grouped = df.groupby('name')['original_value_float'].std().reset_index()
    std_bar = go.Bar(x=grouped['name'], y=grouped['original_value_float'])
    layout = go.Layout(title="Standard Deviation per Sensor", xaxis_title="Sensor", yaxis_title="Standard Deviation (°C)")
    return jsonify(pio.to_json({"data": [std_bar], "layout": layout}))

@views.route('/historical', methods=['GET', 'POST'])
@login_required
def historical():
    fig = None
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        end_date = request.form.get('end_date')
        end_time = request.form.get('end_time')

        if start_date and start_time and end_date and end_time:
            start_datetime = f"{start_date}T{start_time}:00Z"
            end_datetime = f"{end_date}T{end_time}:00Z"
            
            # Generate the historical graph
            fig = create_historical_graph(start_datetime, end_datetime)
        else:
            flash("Please provide both start and end date-time.", "error")

    graph_json = fig.to_json() if fig else None
    return render_template('historical.html', page_id="historical", graph_json=graph_json)
