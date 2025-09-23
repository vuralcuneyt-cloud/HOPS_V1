from core.database import connect_db, insert_design_pack

RATIOS = {
    "Ratio_24x36": (24/36, {"H_36": 36, "W_24": 24}),
    "Ratio_18x24": (18/24, {"H_24": 24, "W_18": 18}),
    "Ratio_24x30": (24/30, {"H_30": 30, "W_24": 24}),
    "Ratio_11x14": (11/14, {"H_14": 14, "W_11": 11}),
    "Ratio_A_Series": (23.386/33.110, {"H_33.110": 33.110, "W_23.386": 23.386}),
}

MASTER_CODES = {
    "Ratio_24x36": "R24x36",
    "Ratio_18x24": "R18x24",
    "Ratio_24x30": "R24x30",
    "Ratio_11x14": "R11x14",
    "Ratio_A_Series": "RA1",
}

def calculate_diff(img_ratio, target_ratio):
    return abs((img_ratio - target_ratio) / target_ratio) * 100

def process_design_pack(trimming=8, progress_cb=None):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.sku, r.width, r.height, r.ratio
        FROM raw_data r
        LEFT JOIN design_pack d ON d.sku = r.sku
        WHERE r.orientation = 'vertical' AND d.sku IS NULL
        """
    )
    rows = cur.fetchall()
    conn.close()

    total = len(rows)

    for idx, (sku, width, height, ratio) in enumerate(rows, start=1):
        matched = []  # (result_path, master_code)
        best_nearest = None  # (nearest_name, nearest_diff)

        for name, (target_ratio, folders) in RATIOS.items():
            diff = calculate_diff(ratio, target_ratio)

            if diff <= trimming:
                h_folder, h_val = list(folders.items())[0]
                w_folder, w_val = list(folders.items())[1]

                if abs(height - h_val) < abs(width - w_val):
                    result_path = f"{name}\\{h_folder}"
                else:
                    result_path = f"{name}\\{w_folder}"

                master_code = None
                if name in MASTER_CODES:
                    master_code = f"{sku}_{MASTER_CODES[name]}_300DPI_sRGB"

                matched.append((result_path, master_code))
            else:
                # Trimming dışı: en yakını takip et
                if best_nearest is None or diff < best_nearest[1]:
                    nearest_name = f"Nearest_{name.replace('Ratio_', '')}"
                    best_nearest = (nearest_name, diff)

        if matched:
            for res_path, code in matched:
                insert_design_pack(sku, res_path, code)
        else:
            if best_nearest:
                nearest_msg = f"{best_nearest[0]} (%{round(best_nearest[1], 2)})"
                insert_design_pack(sku, nearest_msg, None)

        if progress_cb:
            progress_cb(idx, total, f"Design Pack: {idx}/{total} kayıt işlendi...")
