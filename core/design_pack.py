from core.database import connect_db, insert_design_pack

RATIOS = {
    "Ratio_24x36": (24/36, {"H_36": 36, "W_24": 24}),
    "Ratio_18x24": (18/24, {"H_24": 24, "W_18": 18}),
    "Ratio_24x30": (24/30, {"H_30": 30, "W_24": 24}),
    "Ratio_11x14": (11/14, {"H_14": 14, "W_11": 11}),
    "Ratio_A_Series": (23.386/33.110, {"H_33.110": 33.110, "W_23.386": 23.386}),
}

MASTER_CODES = {
    "Ratio_18x24": "R18x24",
    "Ratio_24x30": "R24x30",
    "Ratio_11x14": "R11x14",
    "Ratio_A_Series": "RA1",
}

def calculate_diff(img_ratio, target_ratio):
    return abs((img_ratio - target_ratio) / target_ratio) * 100

def process_design_pack(trimming=8):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT sku, width, height, ratio FROM raw_data WHERE orientation='vertical'")
    rows = cur.fetchall()
    conn.close()

    for sku, width, height, ratio in rows:
        matched = []
        best_nearest = None

        for name, (target_ratio, folders) in RATIOS.items():
            diff = calculate_diff(ratio, target_ratio)

            if diff <= trimming:
                h_folder, h_val = list(folders.items())[0]
                w_folder, w_val = list(folders.items())[1]

                if abs(height - h_val) < abs(width - w_val):
                    result = f"{name}\\{h_folder}"
                else:
                    result = f"{name}\\{w_folder}"

                master_code = None
                if name in MASTER_CODES:
                    master_code = f"{sku}_{MASTER_CODES[name]}_300DPI_sRGB"

                matched.append((result, master_code))
            else:
                if best_nearest is None or diff < best_nearest[1]:
                    best_nearest = (name, diff)

        if matched:
            for res, code in matched:
                insert_design_pack(sku, res, code)
        else:
            if best_nearest:
                insert_design_pack(sku, f"{best_nearest[0]} (%{round(best_nearest[1],2)})", None)
