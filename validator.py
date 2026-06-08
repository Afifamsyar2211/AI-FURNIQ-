import json
import os
import re


def load_rules():
    """Membaca fail rules.json"""
    file_path = os.path.join(os.path.dirname(__file__), 'rules.json')
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: rules.json tidak dijumpai.")
        return {}


def detect_furniture_type(design_name):
    """
    Meneka jenis perabot berdasarkan nama design.
    """
    name = design_name.lower()

    # Keyword Mapping (Melayu & English) -> Keys dalam rules.json
    if any(x in name for x in ['wardrobe', 'almari', 'closet']):
        return 'wardrobe'
    elif any(x in name for x in ['shoe', 'kasut']):
        return 'shoe_rack'
    elif any(x in name for x in ['tv', 'console', 'television']):
        return 'tv_console'
    elif any(x in name for x in ['bed', 'katil', 'sleeping']):
        return 'bed'
    elif any(x in name for x in ['sofa', 'couch', 'lounge']):
        return 'sofa'
    elif any(x in name for x in ['chair', 'kerusi', 'seat', 'stool']):
        return 'chair'
    elif any(x in name for x in ['cabinet', 'kabinet', 'cupboard']):
        return 'cabinet'
    elif any(x in name for x in ['shelf', 'rak', 'bookshelf']):
        return 'shelf'
    else:
        return 'table'  # Default fallback


def validate_design(design_data):
    """
    Menyemak adakah design mematuhi had ukuran dan material.
    """
    rules = load_rules()
    messages = []
    is_valid = True

    # 1. Teka jenis perabot dengan lebih bijak
    design_name = design_data.get("design_name", "")
    furniture_type = detect_furniture_type(design_name)

    # Jika tiada rules untuk jenis ini, guna default table
    if furniture_type not in rules:
        furniture_type = 'table'

    rule = rules[furniture_type]

    # Semak Komponen & Dimensi
    for comp in design_data.get("components", []):
        # A. Semak Material
        mat = comp.get("material", "").lower()
        # Kelonggaran: Jika sebahagian perkataan material ada dalam list (cth: "plywood" dalam "laminated plywood")
        material_found = False
        for allowed_mat in rule.get("materials", []):
            if allowed_mat in mat or mat in allowed_mat:
                material_found = True
                break

        if not material_found:
            messages.append(
                f"Amaran: Material '{mat}' pada '{comp['name']}' mungkin tidak sesuai. Pilihan: {rule['materials']}")

        # B. Semak Dimensi
        dims = comp.get("dimensions", "")
        try:
            # Ambil semua nombor
            numbers = [float(n) for n in re.findall(r"[\d\.]+", dims)]
            if numbers:
                # Anggap dimensi terbesar adalah Panjang/Tinggi
                max_dim = max(numbers)

                # Semak Tinggi Maksimum
                if "max_height" in rule and max_dim > rule["max_height"]:
                    # Kita hanya anggap ia isu jika ia SANGAT besar (buffer 10%)
                    if max_dim > (rule["max_height"] * 1.1):
                        messages.append(
                            f"Isu: Ukuran {max_dim}cm pada '{comp['name']}' melebihi had {rule['max_height']}cm.")
                        is_valid = False
        except:
            pass

    if is_valid:
        messages.append(f"Design ({furniture_type}) lulus semakan validator.")
    else:
        messages.append(f"Design ({furniture_type}) gagal beberapa semakan keselamatan.")

    return is_valid, messages