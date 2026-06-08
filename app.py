import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import re
import pandas as pd
import os
import tempfile
import math
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from flask import Flask, render_template, request, session, send_file
from flask_session import Session
from PIL import Image
from fpdf import FPDF

# --- IMPORT MODULE SENDIRI ---
from generator import get_ai_design, generate_dalle_blueprint
from validator import validate_design

app = Flask(__name__)

# --- KONFIGURASI SESSION ---
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def clean_text_for_pdf(text):
    return text.encode('latin-1', 'ignore').decode('latin-1')


# --- FUNGSI 1: JANA DXF (CAD) ---
def create_dxf_doc(components):
    doc = ezdxf.new()
    msp = doc.modelspace()
    cursor_x, cursor_y, max_row_height, gap = 0, 0, 0, 25
    exclude_keywords = ['screw', 'nail', 'glue', 'hinge', 'handle', 'knob', 'slide', 'pin', 'bracket', 'paku', 'skru',
                        'gam']

    valid_components = []
    for comp in components:
        name = comp.get('name', '').lower()
        if not any(k in name for k in exclude_keywords):
            valid_components.append(comp)

    def get_area(c):
        dim_str = c.get('dimensions', '')
        nums = [float(n) for n in re.findall(r"[\d\.]+", dim_str)]
        return (nums[0] * nums[1]) if len(nums) >= 2 else 0

    valid_components.sort(key=get_area, reverse=True)

    for comp in valid_components:
        dim_str = comp.get('dimensions', '')
        numbers = [float(n) for n in re.findall(r"[\d\.]+", dim_str)]
        length, width = 50, 50
        if len(numbers) >= 2: length, width = numbers[0], numbers[1]

        # --- PEMBETULAN: Filter 1cm supaya komponen kecil tak hilang ---
        if length < 1 or width < 1: continue

        qty = 1
        try:
            qty = int(float(comp.get('quantity', 1)))
        except:
            qty = 1

        for _ in range(qty):
            p1 = (cursor_x, cursor_y)
            p2 = (cursor_x + length, cursor_y)
            p3 = (cursor_x + length, cursor_y + width)
            p4 = (cursor_x, cursor_y + width)
            msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 4})

            min_side = min(length, width)
            text_size = max(2.5, min(min_side * 0.3, 8.0))
            display_name = comp['name']
            if len(display_name) > 25: display_name = display_name[:22] + "..."

            # --- PEMBETULAN: Warna Teks 7 (Hitam/Putih Auto) ---
            msp.add_text(display_name, dxfattribs={
                'height': text_size, 'color': 7,
                'insert': (cursor_x + 1, cursor_y + (width / 2) - (text_size / 2))
            })

            cursor_x += length + gap
            max_row_height = max(max_row_height, width)
            if cursor_x > 1000:
                cursor_x = 0
                cursor_y += max_row_height + gap
                max_row_height = 0
    return doc


# --- FUNGSI 2: DXF PREVIEW ---
def generate_dxf_preview(doc):
    try:
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(doc.modelspace(), finalize=True)
        ax.set_axis_off()
        fig.patch.set_facecolor('#2d3436')
        img = io.BytesIO()
        plt.savefig(img, format='png', facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.1, dpi=300)
        img.seek(0)
        plt.close(fig)
        return base64.b64encode(img.getvalue()).decode()
    except Exception as e:
        print(f"Error preview DXF: {e}")
        return None


# --- FUNGSI 3: DOWNLOAD FILE ---
def generate_dxf_file(components, filename):
    doc = create_dxf_doc(components)
    doc.saveas(filename)


# --- FUNGSI PENGIRAAN ---
def calculate_bom(components):
    bom_data, total_est = [], 0
    csv_path = os.path.join(os.path.dirname(__file__), 'bom_template.csv')
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.DataFrame()

    for comp in components:
        comp_name = comp.get('name', '').lower()
        try:
            qty = float(comp.get('quantity', 1))
        except:
            qty = 1.0
        unit_price = 10.00
        if not df.empty:
            for index, row in df.iterrows():
                if str(row['component']).lower() in comp_name:
                    unit_price = float(row['unit_price_myr'])
                    break
        total_price = unit_price * qty
        total_est += total_price
        qty_display = int(qty) if qty.is_integer() else qty
        bom_data.append(f"{qty_display}x {comp['name']} - RM{total_price:.2f}")
    return bom_data, total_est


def calculate_raw_materials(components):
    total_area_cm2 = 0
    wood_keywords = ['wood', 'plywood', 'mdf', 'board', 'timber', 'plank', 'kayu', 'papan', 'panel', 'top', 'shelf',
                     'door', 'drawer', 'leg', 'apron', 'cabinet', 'frame', 'desk', 'table', 'side', 'back', 'bottom']
    for comp in components:
        name = comp.get('name', '').lower()
        material = comp.get('material', '').lower()
        if any(k in material for k in wood_keywords) or any(k in name for k in wood_keywords):
            dim_str = comp.get('dimensions', '')
            numbers = [float(n) for n in re.findall(r"[\d\.]+", dim_str)]
            if len(numbers) >= 2: total_area_cm2 += numbers[0] * numbers[1] * float(comp.get('quantity', 1))
    sheets_needed = math.ceil((total_area_cm2 * 1.2) / (122 * 244)) if total_area_cm2 > 0 else 0
    return {"total_area_m2": round(total_area_cm2 / 10000, 2), "sheets_needed": sheets_needed,
            "sheet_size": "4' x 8' (122x244 cm)"}


# --- ROUTES ---
@app.route('/download_dxf')
def download_dxf():
    if not session.get('design_data'): return "Tiada data."
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as temp_dxf:
        generate_dxf_file(session.get('raw_components', []), temp_dxf.name)
        return send_file(temp_dxf.name, as_attachment=True, download_name="blueprint_autocad.dxf")


@app.route('/export_pdf')
def export_pdf():
    if not session.get('design_data'): return "Tiada data."
    data = session['design_data']
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, txt="AI-FURNIQ Manufacturing Report", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, txt=f"Project: {clean_text_for_pdf(data.get('design_name', ''))}", ln=True, align='C')
    pdf.ln(5)

    if session.get('cad_preview_url'):
        try:
            img_data = base64.b64decode(session['cad_preview_url'])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
                temp_img.write(img_data)
                temp_img_path = temp_img.name
            pdf.image(temp_img_path, x=15, w=180)
            os.unlink(temp_img_path)
        except:
            pass

    # AI CONFIDENCE IN PDF
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"AI Confidence Score: {data.get('confidence_score', 'N/A')}%", ln=True)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 6, f"Reason: {clean_text_for_pdf(data.get('confidence_reason', ''))}")
    pdf.ln(5)

    sections = [
        ("1. Factory Validator Status", data.get('validation', [])),
        ("2. Required Components List", [f"- {c}" for c in data.get('components', [])]),
        ("3. Cost Estimation", data.get('bom', [])),
        ("4. Assembly Instructions", [f"{i}. {s}" for i, s in enumerate(data.get('steps', []), 1)])
    ]

    for title, content in sections:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, f"  {title}", ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", size=11)
        if not content:
            pdf.cell(0, 8, "No data.", ln=True)
        else:
            for item in content:
                pdf.multi_cell(0, 7, txt=clean_text_for_pdf(str(item)))
        pdf.ln(5)

    buffer = io.BytesIO()
    try:
        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
    except:
        pdf_output = pdf.output(dest='S').encode('utf-8', 'ignore')
    buffer.write(pdf_output)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="plan.pdf", mimetype='application/pdf')


@app.route('/', methods=['GET', 'POST'])
def index():
    output, user_input, cad_preview_url = None, "", None
    if request.method == 'POST':
        user_input = request.form.get('furniture_request')
        image_file = request.files.get('furniture_image')
        image_data = None
        if image_file and image_file.filename != '':
            try:
                img_temp = Image.open(image_file.stream)
                if img_temp.mode != 'RGB': img_temp = img_temp.convert('RGB')
                img_temp.thumbnail((1024, 1024))
                image_data = img_temp
            except:
                pass

        design_json = get_ai_design(user_input, image_input=image_data)

        if not design_json.get('components'):
            validation_msgs, bom_list, total_cost, cutting_list, clean_steps_list = ["Error AI."], [], 0, {}, []
        else:
            is_valid, validation_msgs = validate_design(design_json)
            bom_list, total_cost = calculate_bom(design_json.get('components', []))
            cutting_list = calculate_raw_materials(design_json.get('components', []))
            clean_steps_list = [re.sub(r'^\d+[\.\)]\s*', '', step) for step in design_json.get('assembly_steps', [])]

            try:
                doc = create_dxf_doc(design_json.get('components', []))
                prompt_text = user_input if user_input else design_json.get('design_name', 'Furniture')
                cad_preview_url = generate_dalle_blueprint(prompt_text)
                if not cad_preview_url: cad_preview_url = generate_dxf_preview(doc)
            except:
                cad_preview_url = None

        output = {
            "design_name": design_json.get('design_name', 'Ralat'),
            # --- UPDATE: DATA CONFIDENCE ---
            "confidence_score": design_json.get('confidence_score', 85),
            "confidence_reason": design_json.get('confidence_reason', 'Standard generation.'),
            "components": [f"{c['quantity']}x {c['name']} - {c.get('dimensions', '')}" for c in
                           design_json.get('components', [])],
            "steps": clean_steps_list, "bom": bom_list, "total_cost": f"RM {total_cost:.2f}",
            "validation": validation_msgs, "cutting_list": cutting_list
        }
        session['design_data'] = output
        session['raw_components'] = design_json.get('components', [])
        session['cad_preview_url'] = cad_preview_url

    return render_template('index.html', output=output, user_input=user_input,
                           cad_preview_url=session.get('cad_preview_url'))


if __name__ == '__main__':
    app.run(debug=True)