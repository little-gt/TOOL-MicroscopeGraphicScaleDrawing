import os
from PIL import Image, ImageDraw, ImageFont, ImageTk, ExifTags
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox  # pip install CTkMessagebox
from tkinter import filedialog, messagebox, colorchooser  # Standard tkinter, added colorchooser
import matplotlib.font_manager as fm  # pip install matplotlib
import re  # For parsing metadata

# --- Font Finding Logic (Condensed - unchanged) ---
preferred_fonts_list = [
    "SimHei.ttf", "msyh.ttf", "simsun.ttf", "DengXian.ttf", "arialuni.ttf",
    "msyh.ttc", "simsun.ttc", "STHeiti", "Heiti SC", "PingFang SC",
    "WenQuanYi Zen Hei", "WenQuanYi Micro Hei", "wqy-zenhei.ttc",
    "Noto Sans CJK SC", "Noto Serif CJK SC", "DejaVuSans.ttf", "Arial Unicode MS", "Arial.ttf"
]
font_path_selected = None;
print("Font Search Log:")
for font_name_or_file in preferred_fonts_list:
    try:
        ImageFont.truetype(font_name_or_file, 10);
        font_path_selected = font_name_or_file;
        print(
            f"  ✓ OK: '{font_name_or_file}'");
        break
    except:
        pass
if not font_path_selected:
    print("  --- Trying matplotlib search...");
    matplotlib_cjk_search_list = ["SimHei", "Microsoft YaHei", "Heiti", "Noto Sans CJK"]
    for fm_font_name in matplotlib_cjk_search_list:
        try:
            fm_path_candidate = fm.findfont(fm.FontProperties(family=fm_font_name));
            ImageFont.truetype(
                fm_path_candidate, 10);
            font_path_selected = fm_path_candidate;
            print(
                f"  ✓ OK (matplotlib): '{fm_font_name}' -> {fm_path_candidate}");
            break
        except:
            pass
if not font_path_selected:
    try:
        fm_sans_path = fm.findfont(fm.FontProperties(family='sans-serif'));
        ImageFont.truetype(fm_sans_path,
                           10);
        font_path_selected = fm_sans_path;
        print(
            f"  ✓ OK (matplotlib sans-serif): '{os.path.basename(fm_sans_path)}'")
    except Exception as e:
        print(f"  ✗ Error with matplotlib sans-serif: {e}")
if not font_path_selected: font_path_selected = "arial.ttf"; print(f"  ‼ FALLBACK: '{font_path_selected}'")
try:
    ImageFont.truetype(font_path_selected, 10);
    print(f"  ✓ Final font '{font_path_selected}' loaded.")
except Exception as e:
    print(f"  ‼‼ FAILED to load fallback '{font_path_selected}': {e}");
    font_path_selected = "arial.ttf"  # Ensure it's set if the try fails
font_path = font_path_selected;
print("-" * 30)

# --- Constants for Settings (unchanged from previous custom color version) ---
DEFAULT_SCREEN_WIDTH_CM_FLOAT = 12.7
DEFAULT_MAGNIFICATION_FLOAT = 100.0

KEY_MAG = "magnification"
KEY_SW = "screen_width_cm"
KEY_SAMPLE = "sample_name"
KEY_TIME = "shoot_time"
KEY_REMARK = "remark"
KEY_POS = "scalebar_position"
KEY_TEXT_COLOR = "text_color"
KEY_SCALEBAR_COLOR = "scalebar_color"

DEFAULT_TEXT_COLOR = "#FFFFFF"
DEFAULT_SCALEBAR_COLOR = "#FFFFFF"

DEFAULT_SETTINGS = {
    KEY_MAG: DEFAULT_MAGNIFICATION_FLOAT,
    KEY_SW: DEFAULT_SCREEN_WIDTH_CM_FLOAT,
    KEY_SAMPLE: "",
    KEY_TIME: "",
    KEY_REMARK: "",
    KEY_POS: "right_bottom",
    KEY_TEXT_COLOR: DEFAULT_TEXT_COLOR,
    KEY_SCALEBAR_COLOR: DEFAULT_SCALEBAR_COLOR,
}


# --- Core Drawing Logic (Updated to remove text stroke) ---
def choose_scalebar_length(magnification, img_width_px, screen_width_cm):
    actual_magnification = magnification if magnification > 0 else 1.0
    actual_screen_width_cm = screen_width_cm if screen_width_cm > 0 else 1.0

    if actual_magnification <= 0: actual_magnification = DEFAULT_MAGNIFICATION_FLOAT
    if actual_screen_width_cm <= 0: actual_screen_width_cm = DEFAULT_SCREEN_WIDTH_CM_FLOAT
    if img_width_px <= 0: img_width_px = 1024

    pixel_size_um = (actual_screen_width_cm * 10000) / (actual_magnification * img_width_px)
    if pixel_size_um <= 1e-9: pixel_size_um = 1e-3

    scalebar_options = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    min_px, max_px = img_width_px / 5, img_width_px / 3
    best_option = scalebar_options[0];
    found_option = False
    for val_um in scalebar_options:
        scalebar_px_for_option = val_um / pixel_size_um
        if min_px <= scalebar_px_for_option <= max_px:
            best_option = val_um;
            found_option = True;
            break
    if not found_option:
        closest_val = scalebar_options[0];
        min_diff_heuristic = float('inf')
        for val_um in scalebar_options:
            scalebar_px_for_option = val_um / pixel_size_um
            if scalebar_px_for_option > img_width_px * 0.9: continue
            if scalebar_px_for_option < 50 and len(scalebar_options) > 1 and val_um < scalebar_options[
                -1]: continue
            diff = abs(scalebar_px_for_option - min_px)
            if diff < min_diff_heuristic: min_diff_heuristic = diff; closest_val = val_um
        best_option = closest_val
    return best_option


def read_magnification_from_metadata(img):
    try:
        exif = img.getexif()
        if not exif: return None
        for tag_id, val in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if "Magnification" in str(tag_name) or "MAG" in str(tag_name).upper():
                if isinstance(val, (int, float)): return float(val)
                if isinstance(val, str):
                    match = re.search(r'(\d+\.?\d*)', val)
                    if match: return float(match.group(1))
            if tag_name == 'UserComment':
                comment_str = ""
                if isinstance(val, bytes):
                    try:
                        comment_str = val.decode('utf-8', errors='ignore')
                    except:
                        pass
                elif isinstance(val, str):
                    comment_str = val
                if comment_str:
                    match = re.search(r'(?:Magnification|Mag|Zoom|SEM MAG)\s*[:=]?\s*(\d+\.?\d*)\s*(k)?(?:x|X)?',
                                      comment_str, re.IGNORECASE)
                    if match:
                        num_str, is_kilo = match.group(1), match.group(2)
                        mag_val = float(num_str)
                        if is_kilo and is_kilo.lower() == 'k': mag_val *= 1000
                        return mag_val
    except:
        pass
    return None


def draw_scalebar_and_info(img, magnification, screen_width_cm, scalebar_length_um, position="right_bottom",
                           sample_name="", shoot_time="", remark="",
                           text_color="#FFFFFF", scalebar_fill_color="#FFFFFF"):
    W, H = img.size

    actual_magnification = magnification if magnification > 0 else 1.0
    actual_screen_width_cm = screen_width_cm if screen_width_cm > 0 else 1.0

    if actual_magnification <= 0: actual_magnification = DEFAULT_MAGNIFICATION_FLOAT
    if actual_screen_width_cm <= 0: actual_screen_width_cm = DEFAULT_SCREEN_WIDTH_CM_FLOAT

    if img.mode != 'RGB': img = img.convert('RGB')
    pixel_size_um = (actual_screen_width_cm * 10000) / (actual_magnification * W)
    if pixel_size_um <= 1e-9: pixel_size_um = 1e-3
    scalebar_px = int(scalebar_length_um / pixel_size_um)
    if scalebar_px <= 0: scalebar_px = W // 10

    draw = ImageDraw.Draw(img)
    margin = max(15, W // 70)
    font_size = max(18, H // 40);
    small_font_size = max(14, font_size - 4)
    try:
        font = ImageFont.truetype(font_path, font_size)
        small_font = ImageFont.truetype(font_path, small_font_size)
    except IOError:
        font = ImageFont.load_default();
        small_font = ImageFont.load_default()

    # --- New Scalebar Style Drawing ---
    line_thickness = max(2, int(scalebar_px / 40), int(H / 120))
    cap_height = max(line_thickness * 2.5, int(font_size * 0.8))

    bar_start_x = margin if position == "left_bottom" else W - scalebar_px - margin - line_thickness

    cap_bottom_y = H - margin
    main_bar_y = cap_bottom_y - cap_height / 2

    draw.line([(bar_start_x, main_bar_y - cap_height / 2),
               (bar_start_x, main_bar_y + cap_height / 2)],
              fill=scalebar_fill_color, width=line_thickness)
    draw.line([(bar_start_x + scalebar_px, main_bar_y - cap_height / 2),
               (bar_start_x + scalebar_px, main_bar_y + cap_height / 2)],
              fill=scalebar_fill_color, width=line_thickness)
    draw.line([(bar_start_x, main_bar_y),
               (bar_start_x + scalebar_px, main_bar_y)],
              fill=scalebar_fill_color, width=line_thickness)

    # Scalebar Text
    scalebar_text_content = f"{scalebar_length_um} μm"
    try:
        bbox_sb_text = draw.textbbox((0, 0), scalebar_text_content, font=font)
        sb_text_width = bbox_sb_text[2] - bbox_sb_text[0]
        sb_text_height = bbox_sb_text[3] - bbox_sb_text[1]
    except AttributeError:
        sb_text_width, sb_text_height_approx = draw.textsize(scalebar_text_content, font=font)
        sb_text_height = int(sb_text_height_approx * 1.2)

    sb_text_x = bar_start_x + (scalebar_px - sb_text_width) / 2
    if sb_text_x < margin: sb_text_x = margin

    gap_text_bar = max(2, line_thickness // 2, int(font_size * 0.1))
    sb_text_y_top = (main_bar_y - line_thickness / 2) - sb_text_height - gap_text_bar

    # Removed stroke_width and stroke_fill
    draw.text((sb_text_x, sb_text_y_top), scalebar_text_content, fill=scalebar_fill_color, font=font)

    # Remark Text
    if remark:
        try:
            bbox_remark_text = draw.textbbox((0, 0), remark, font=small_font)
            remark_text_width = bbox_remark_text[2] - bbox_remark_text[0]
            remark_text_height = bbox_remark_text[3] - bbox_remark_text[1]
        except AttributeError:
            remark_text_width, remark_text_height_approx = draw.textsize(remark, font=small_font)
            remark_text_height = int(remark_text_height_approx * 1.2)

        remark_y_top_default = sb_text_y_top + (sb_text_height / 2) - (remark_text_height / 2)
        remark_y_top = remark_y_top_default
        spacing_remark = font_size // 2
        scalebar_unit_left_edge_visual = min(bar_start_x, sb_text_x)
        scalebar_unit_right_edge_visual = max(bar_start_x + scalebar_px + line_thickness, sb_text_x + sb_text_width)

        if position == "left_bottom":
            remark_x_start = scalebar_unit_right_edge_visual + spacing_remark
            if remark_x_start + remark_text_width > W - margin:
                remark_x_start = W - margin - remark_text_width
                if remark_x_start < scalebar_unit_right_edge_visual + spacing_remark / 2:
                    remark_y_top = cap_bottom_y + spacing_remark // 2;
                    remark_x_start = bar_start_x
        else:
            remark_x_start = scalebar_unit_left_edge_visual - remark_text_width - spacing_remark
            if remark_x_start < margin:
                remark_x_start = margin
                if remark_x_start + remark_text_width > scalebar_unit_left_edge_visual - spacing_remark / 2:
                    remark_y_top = cap_bottom_y + spacing_remark // 2;
                    remark_x_start = bar_start_x + scalebar_px - remark_text_width

        # Removed stroke_width and stroke_fill
        draw.text((remark_x_start, remark_y_top), remark, fill=text_color, font=small_font)

    # Top Info Text
    current_y_offset = margin;
    top_info_lines = []
    if sample_name: top_info_lines.append(f"样品名称: {sample_name}")
    if shoot_time: top_info_lines.append(f"拍摄时间: {shoot_time}")
    for line_text in top_info_lines:
        # Removed stroke_width and stroke_fill
        draw.text((margin, current_y_offset), line_text, fill=text_color, font=small_font)
        try:
            bbox_line = small_font.getbbox(line_text)
            line_height = bbox_line[3] - bbox_line[1]
        except AttributeError:
            _, line_height_attr = small_font.getsize(line_text)
            line_height = int(line_height_attr * 1.2)
        current_y_offset += line_height + (small_font_size // 3)
    return img


# --- SelectImagesDialog (unchanged) ---
class SelectImagesDialog(ctk.CTkToplevel):
    def __init__(self, parent, image_paths_with_thumbs, current_settings_dict, callback):
        super().__init__(parent)
        self.title("选择要应用设置的图片")
        self.geometry("600x550")
        self.parent = parent
        self.image_paths_with_thumbs = image_paths_with_thumbs
        self.current_settings_dict = current_settings_dict
        self.callback = callback
        self.checkbox_vars = []
        self.transient(parent)
        self.grab_set()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="选择要将当前主面板设置应用到的图片：").pack(pady=(0, 10), anchor="w")

        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        for path, thumb_photo in self.image_paths_with_thumbs:
            var = ctk.StringVar(value="0")
            self.checkbox_vars.append((path, var))

            item_frame = ctk.CTkFrame(scroll_frame)
            item_frame.pack(fill="x", pady=2)

            if thumb_photo:
                thumb_label = ctk.CTkLabel(item_frame, image=thumb_photo, text="")
                thumb_label.pack(side="left", padx=5, pady=2)
            else:
                ctk.CTkLabel(item_frame, text="[无预览]", width=50, height=50, fg_color="gray20").pack(side="left",
                                                                                                       padx=5, pady=2)

            check_box = ctk.CTkCheckBox(item_frame, text=os.path.basename(path), variable=var, onvalue="1",
                                        offvalue="0")
            check_box.pack(side="left", padx=5, expand=True, anchor="w")

        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", pady=(10, 0))

        self.select_all_var = ctk.StringVar(value="0")
        select_all_checkbox = ctk.CTkCheckBox(controls_frame, text="全选/全不选", variable=self.select_all_var,
                                              onvalue="1", offvalue="0", command=self._toggle_all_individual_checkboxes)
        select_all_checkbox.pack(side="left", padx=5, pady=5)

        button_actions_frame = ctk.CTkFrame(controls_frame)
        button_actions_frame.pack(side="right", padx=5, pady=5)

        ctk.CTkButton(button_actions_frame, text="取消", command=self._cancel_dialog).pack(side="right", padx=(5, 0))
        ctk.CTkButton(button_actions_frame, text="应用选中", command=self._apply_selected).pack(side="right", padx=0)

        controls_frame.grid_columnconfigure(0, weight=1)

    def _toggle_all_individual_checkboxes(self):
        is_checked = self.select_all_var.get() == "1"
        for _, var in self.checkbox_vars:
            var.set("1" if is_checked else "0")

    def _apply_selected(self):
        selected_paths = [path for path, var in self.checkbox_vars if var.get() == "1"]
        if not selected_paths:
            CTkMessagebox(master=self, title="提示", message="未选择任何图片。", icon="info")
            return

        confirm_msg = (f"您确定要将主面板的当前设置应用到选中的 {len(selected_paths)} 张图片吗？\n\n"
                       "此操作不可撤销，并将覆盖这些图片的现有设置。")
        if CTkMessagebox(master=self, title="确认操作", message=confirm_msg, icon="question", option_1="否",
                         option_2="是").get() == "是":
            self.callback(selected_paths, self.current_settings_dict)
            self.destroy()

    def _cancel_dialog(self):
        any_selected = any(var.get() == "1" for _, var in self.checkbox_vars)
        if any_selected:
            if CTkMessagebox(master=self, title="确认取消",
                             message="当前已选中部分图片。确定要放弃选择并关闭此对话框吗？",
                             icon="question", option_1="否", option_2="是").get() == "是":
                self.destroy()
        else:
            self.destroy()


class MainWindowSEMApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("显微镜图像图注信息生成工具")
        self.geometry("1150x800")
        self.minsize(950, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.file_paths = []
        self.current_index = -1
        self.img_tk = None
        self.thumbnail_photos_for_list = []
        self.image_item_frames = []
        self.image_specific_settings = {}

        self.magnification_var = ctk.StringVar()
        self.screen_width_var = ctk.StringVar()
        self.scalebar_position_var = ctk.StringVar()
        self.sample_name_var = ctk.StringVar()
        self.shoot_time_var = ctk.StringVar()
        self.remark_var = ctk.StringVar()
        self.export_folder_var = ctk.StringVar()
        self.text_color_var = ctk.StringVar(value=DEFAULT_SETTINGS[KEY_TEXT_COLOR])
        self.scalebar_color_var = ctk.StringVar(value=DEFAULT_SETTINGS[KEY_SCALEBAR_COLOR])

        self.selected_item_bg_color = "#3a7ebf"
        _dummy_frame = ctk.CTkFrame(self)
        self.default_item_bg_color = _dummy_frame.cget("fg_color")
        _dummy_frame.destroy()

        self._ui_update_active = True
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_closing_app)
        self._clear_ui_fields()

    def create_widgets(self):
        nav_frame = ctk.CTkFrame(self, height=50);
        nav_frame.pack(fill="x", side="top", padx=10, pady=5)
        ctk.CTkButton(nav_frame, text="导入图片", command=self.select_files).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="选择导出文件夹", command=self.select_export_folder).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="开始批量处理", command=self.process_images).pack(side="left", padx=5)
        self.export_folder_label = ctk.CTkLabel(nav_frame, text="未选择导出文件夹");
        self.export_folder_label.pack(side="left", padx=10, fill="x", expand=True)

        main_frame = ctk.CTkFrame(self);
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        left_panel = ctk.CTkFrame(main_frame, width=320);
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0);
        left_panel.pack_propagate(False)
        ctk.CTkLabel(left_panel, text="图片列表").pack(anchor="w", pady=(5, 5), padx=10)
        self.image_list_frame = ctk.CTkScrollableFrame(left_panel, label_text="");
        self.image_list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        info_frame = ctk.CTkFrame(left_panel);
        info_frame.pack(fill="x", pady=(5, 0), padx=5)
        row_idx = 0
        ctk.CTkLabel(info_frame, text="放大倍数:").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        ctk.CTkEntry(info_frame, textvariable=self.magnification_var).grid(row=row_idx, column=1, pady=3, padx=5,
                                                                           sticky="ew");
        row_idx += 1
        ctk.CTkLabel(info_frame, text="图片标定宽度(cm):").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        ctk.CTkEntry(info_frame, textvariable=self.screen_width_var).grid(row=row_idx, column=1, pady=3, padx=5,
                                                                          sticky="ew");
        row_idx += 1
        ctk.CTkLabel(info_frame, text="标尺位置:").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        pos_radio_frame = ctk.CTkFrame(info_frame);
        pos_radio_frame.grid(row=row_idx, column=1, sticky="ew", pady=3, padx=5)
        ctk.CTkRadioButton(pos_radio_frame, text="左下", variable=self.scalebar_position_var, value="left_bottom").pack(
            side="left", padx=2, expand=True)
        ctk.CTkRadioButton(pos_radio_frame, text="右下", variable=self.scalebar_position_var,
                           value="right_bottom").pack(side="left", padx=2, expand=True);
        row_idx += 1
        ctk.CTkLabel(info_frame, text="样品名称:").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        ctk.CTkEntry(info_frame, textvariable=self.sample_name_var).grid(row=row_idx, column=1, sticky="ew", pady=3,
                                                                         padx=5);
        row_idx += 1
        ctk.CTkLabel(info_frame, text="拍摄时间:").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        ctk.CTkEntry(info_frame, textvariable=self.shoot_time_var).grid(row=row_idx, column=1, sticky="ew", pady=3,
                                                                        padx=5);
        row_idx += 1
        ctk.CTkLabel(info_frame, text="比例尺旁备注:").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        ctk.CTkEntry(info_frame, textvariable=self.remark_var).grid(row=row_idx, column=1, sticky="ew", pady=3, padx=5);

        row_idx += 1
        ctk.CTkLabel(info_frame, text="文字颜色:").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        text_color_frame = ctk.CTkFrame(info_frame)
        text_color_frame.grid(row=row_idx, column=1, sticky="ew", pady=3, padx=5)
        self.text_color_preview = ctk.CTkFrame(text_color_frame, width=20, height=20, border_width=1,
                                               border_color="gray50")
        self.text_color_preview.pack(side="left", padx=(0, 5))
        ctk.CTkButton(text_color_frame, text="选择", width=60,
                      command=lambda: self._select_color_for_var(self.text_color_var, self.text_color_preview,
                                                                 KEY_TEXT_COLOR)).pack(side="left")

        row_idx += 1
        ctk.CTkLabel(info_frame, text="标尺颜色:").grid(row=row_idx, column=0, sticky="w", pady=3, padx=5)
        scalebar_color_frame = ctk.CTkFrame(info_frame)
        scalebar_color_frame.grid(row=row_idx, column=1, sticky="ew", pady=3, padx=5)
        self.scalebar_color_preview = ctk.CTkFrame(scalebar_color_frame, width=20, height=20, border_width=1,
                                                   border_color="gray50")
        self.scalebar_color_preview.pack(side="left", padx=(0, 5))
        ctk.CTkButton(scalebar_color_frame, text="选择", width=60,
                      command=lambda: self._select_color_for_var(self.scalebar_color_var, self.scalebar_color_preview,
                                                                 KEY_SCALEBAR_COLOR)).pack(side="left")

        row_idx += 1
        info_frame.grid_columnconfigure(1, weight=1)

        apply_buttons_frame = ctk.CTkFrame(info_frame)
        apply_buttons_frame.grid(row=row_idx, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        ctk.CTkButton(apply_buttons_frame, text="批量运用到图片",
                      command=self._open_apply_to_selected_dialog).pack(expand=True, fill="x", padx=0)

        self.magnification_var.trace_add("write", lambda n, i, m: self._on_var_changed(self.magnification_var, KEY_MAG))
        self.screen_width_var.trace_add("write", lambda n, i, m: self._on_var_changed(self.screen_width_var, KEY_SW))
        self.scalebar_position_var.trace_add("write",
                                             lambda n, i, m: self._on_var_changed(self.scalebar_position_var, KEY_POS))
        self.sample_name_var.trace_add("write", lambda n, i, m: self._on_var_changed(self.sample_name_var, KEY_SAMPLE))
        self.shoot_time_var.trace_add("write", lambda n, i, m: self._on_var_changed(self.shoot_time_var, KEY_TIME))
        self.remark_var.trace_add("write", lambda n, i, m: self._on_var_changed(self.remark_var, KEY_REMARK))
        self.text_color_var.trace_add("write",
                                      lambda n, i, m: self._on_var_changed(self.text_color_var, KEY_TEXT_COLOR))
        self.scalebar_color_var.trace_add("write", lambda n, i, m: self._on_var_changed(self.scalebar_color_var,
                                                                                        KEY_SCALEBAR_COLOR))

        right_frame = ctk.CTkFrame(main_frame);
        right_frame.pack(side="left", fill="both", expand=True)
        self.preview_label = ctk.CTkLabel(right_frame, text="请导入图片", anchor="center", fg_color="#333333",
                                          corner_radius=10);
        self.preview_label.pack(fill="both", expand=True, padx=5, pady=5)
        self.preview_label.bind("<Configure>",
                                lambda event: self._refresh_preview_for_current_image(force_reload_image=False))

        self._update_color_preview(self.text_color_preview, self.text_color_var.get())
        self._update_color_preview(self.scalebar_color_preview, self.scalebar_color_var.get())

    def _update_color_preview(self, preview_widget, hex_color):
        try:
            if preview_widget and hex_color:
                preview_widget.configure(fg_color=hex_color)
        except Exception:
            if preview_widget: preview_widget.configure(fg_color="gray")

    def _select_color_for_var(self, color_var, preview_widget, key_changed):
        current_color = color_var.get()
        chosen_color = colorchooser.askcolor(title="选择颜色", initialcolor=current_color, parent=self)
        if chosen_color and chosen_color[1]:
            hex_color = chosen_color[1]
            if hex_color != current_color:
                color_var.set(hex_color)
            else:
                self._update_color_preview(preview_widget, hex_color)
                if self.current_index != -1:
                    self._refresh_preview_for_current_image()

    def _on_var_changed(self, var_obj, key_changed):
        if not self._ui_update_active: return
        if not (0 <= self.current_index < len(self.file_paths)): return

        current_path = self.file_paths[self.current_index]
        settings = self.image_specific_settings[current_path]

        old_value_in_settings = settings.get(key_changed)
        ui_value_str = var_obj.get()
        actual_value_for_setting = None
        ui_should_be_empty = False

        if key_changed == KEY_MAG:
            if not ui_value_str:
                actual_value_for_setting = 1.0;
                ui_should_be_empty = True
            else:
                try:
                    val_float = float(ui_value_str)
                    if val_float > 0: actual_value_for_setting = float(int(val_float))
                    if actual_value_for_setting and str(int(actual_value_for_setting)) != ui_value_str:
                        self._ui_update_active = False;
                        var_obj.set(str(int(actual_value_for_setting)));
                        self._ui_update_active = True
                except ValueError:
                    pass
        elif key_changed == KEY_SW:
            if not ui_value_str:
                actual_value_for_setting = 1.0;
                ui_should_be_empty = True
            else:
                try:
                    val_float = float(ui_value_str)
                    if val_float > 0: actual_value_for_setting = val_float
                except ValueError:
                    pass
        elif key_changed in [KEY_TEXT_COLOR, KEY_SCALEBAR_COLOR]:
            actual_value_for_setting = ui_value_str
            if key_changed == KEY_TEXT_COLOR:
                self._update_color_preview(self.text_color_preview, ui_value_str)
            elif key_changed == KEY_SCALEBAR_COLOR:
                self._update_color_preview(self.scalebar_color_preview, ui_value_str)
        else:
            actual_value_for_setting = ui_value_str

        if actual_value_for_setting is None and key_changed in [KEY_MAG, KEY_SW]:
            revert_val = old_value_in_settings if isinstance(old_value_in_settings, (float, int)) else (
                1.0 if key_changed in [KEY_MAG, KEY_SW] else "")
            actual_value_for_setting = revert_val
            revert_ui_str = str(int(revert_val)) if key_changed == KEY_MAG else str(revert_val)
            if var_obj.get() != revert_ui_str:
                self._ui_update_active = False;
                var_obj.set(revert_ui_str);
                self._ui_update_active = True
            ui_should_be_empty = False

        settings[key_changed] = actual_value_for_setting
        self._refresh_preview_for_current_image()

    def _create_image_list_item(self, parent_frame, index, file_path):
        item_frame = ctk.CTkFrame(parent_frame, corner_radius=5, fg_color=self.default_item_bg_color);
        item_frame.pack(fill="x", pady=2, padx=2)
        thumb_photo_for_list = None
        try:
            img = Image.open(file_path);
            img.thumbnail((80, 80), Image.Resampling.LANCZOS)
            thumb_photo_for_list = ImageTk.PhotoImage(img);
            self.thumbnail_photos_for_list.append(thumb_photo_for_list)
            img.close()
            thumb_label = ctk.CTkLabel(item_frame, image=thumb_photo_for_list, text="")
            thumb_label.pack(side="left", padx=5, pady=5)
        except Exception as e:
            print(f"Error creating thumbnail for list: {e}")
            thumb_label = ctk.CTkLabel(item_frame, text="Err", width=80, height=80, fg_color="red");
            thumb_label.pack(side="left", padx=5, pady=5)

        filename = os.path.basename(file_path)
        parent_width = parent_frame.winfo_width() if parent_frame.winfo_exists() and parent_frame.winfo_width() > 0 else 280
        wraplen = parent_width - 110 if parent_width > 120 else 180
        name_label = ctk.CTkLabel(item_frame, text=filename, anchor="w", wraplength=wraplen)
        name_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        for widget in [item_frame, thumb_label, name_label]:
            widget.bind("<Button-1>", lambda event, idx=index: self._on_image_item_selected(idx))
        return item_frame

    def _update_image_list_display(self):
        for widget in self.image_list_frame.winfo_children(): widget.destroy()
        self.thumbnail_photos_for_list.clear();
        self.image_item_frames.clear()

        for i, p in enumerate(self.file_paths):
            item_frame = self._create_image_list_item(self.image_list_frame, i, p)
            self.image_item_frames.append(item_frame)

        if self.file_paths and self.current_index == -1:
            self._on_image_item_selected(0)
        elif self.file_paths and 0 <= self.current_index < len(self.file_paths):
            self._highlight_selected_item(self.current_index)
            self._load_settings_for_active_image()
        elif not self.file_paths:
            self.current_index = -1;
            self.preview_label.configure(text="请导入图片", image=None);
            self.img_tk = None
            self._clear_ui_fields()

    def _highlight_selected_item(self, selected_idx):
        for i, frame in enumerate(self.image_item_frames):
            frame.configure(fg_color=self.selected_item_bg_color if i == selected_idx else self.default_item_bg_color)

    def _on_image_item_selected(self, index):
        if not (0 <= index < len(self.file_paths)): return
        if self.current_index == index and self._ui_update_active:
            pass
        self.current_index = index
        self._highlight_selected_item(index)
        self._load_settings_for_active_image()

    def select_files(self):
        if self.file_paths:
            if CTkMessagebox(title="确认操作", message="导入新的图片将会清空当前列表和已编辑的设置。\n是否继续？",
                             icon="question", option_1="否", option_2="是").get() != "是": return

        paths = filedialog.askopenfilenames(title="选择图片",
                                            filetypes=[("图片", "*.jpg *.jpeg *.png *.tif *.tiff"), ("所有", "*.*")])
        if paths:
            self.file_paths = list(paths);
            self.current_index = -1;
            self.image_specific_settings.clear()
            for path in self.file_paths:
                current_img_settings = DEFAULT_SETTINGS.copy()
                try:
                    img_temp = Image.open(path)
                    mag_meta_float = read_magnification_from_metadata(img_temp)
                    img_temp.close()
                    if mag_meta_float is not None and mag_meta_float > 0:
                        current_img_settings[KEY_MAG] = float(int(mag_meta_float))
                except Exception as e:
                    print(f"Could not read metadata for {os.path.basename(path)}: {e}")
                self.image_specific_settings[path] = current_img_settings

            self._update_image_list_display()

            if not self.file_paths:
                self.preview_label.configure(text="未选择图片", image=None);
                self.img_tk = None
                self._clear_ui_fields()

    def _clear_ui_fields(self):
        self._ui_update_active = False
        self.magnification_var.set(str(int(DEFAULT_SETTINGS[KEY_MAG])))
        self.screen_width_var.set(str(DEFAULT_SETTINGS[KEY_SW]))
        self.sample_name_var.set(DEFAULT_SETTINGS[KEY_SAMPLE])
        self.shoot_time_var.set(DEFAULT_SETTINGS[KEY_TIME])
        self.remark_var.set(DEFAULT_SETTINGS[KEY_REMARK])
        self.scalebar_position_var.set(DEFAULT_SETTINGS[KEY_POS])
        self.text_color_var.set(DEFAULT_SETTINGS[KEY_TEXT_COLOR])
        self.scalebar_color_var.set(DEFAULT_SETTINGS[KEY_SCALEBAR_COLOR])

        if hasattr(self, 'text_color_preview'):
            self._update_color_preview(self.text_color_preview, DEFAULT_SETTINGS[KEY_TEXT_COLOR])
        if hasattr(self, 'scalebar_color_preview'):
            self._update_color_preview(self.scalebar_color_preview, DEFAULT_SETTINGS[KEY_SCALEBAR_COLOR])
        self._ui_update_active = True

    def _load_settings_for_active_image(self):
        if not (0 <= self.current_index < len(self.file_paths)):
            self._clear_ui_fields()
            self._refresh_preview_for_current_image()
            return

        current_path = self.file_paths[self.current_index]
        settings = self.image_specific_settings.get(current_path)
        if not settings:
            settings = DEFAULT_SETTINGS.copy()
            self.image_specific_settings[current_path] = settings

        self._ui_update_active = False
        mag_val = settings.get(KEY_MAG, DEFAULT_SETTINGS[KEY_MAG])
        sw_val = settings.get(KEY_SW, DEFAULT_SETTINGS[KEY_SW])
        self.magnification_var.set(str(int(mag_val)) if mag_val != 1.0 else "")
        self.screen_width_var.set(str(sw_val) if sw_val != 1.0 else "")

        self.sample_name_var.set(settings.get(KEY_SAMPLE, DEFAULT_SETTINGS[KEY_SAMPLE]))
        self.shoot_time_var.set(settings.get(KEY_TIME, DEFAULT_SETTINGS[KEY_TIME]))
        self.remark_var.set(settings.get(KEY_REMARK, DEFAULT_SETTINGS[KEY_REMARK]))
        self.scalebar_position_var.set(settings.get(KEY_POS, DEFAULT_SETTINGS[KEY_POS]))

        text_c = settings.get(KEY_TEXT_COLOR, DEFAULT_SETTINGS[KEY_TEXT_COLOR])
        scalebar_c = settings.get(KEY_SCALEBAR_COLOR, DEFAULT_SETTINGS[KEY_SCALEBAR_COLOR])
        self.text_color_var.set(text_c)
        self.scalebar_color_var.set(scalebar_c)

        if hasattr(self, 'text_color_preview'):
            self._update_color_preview(self.text_color_preview, text_c)
        if hasattr(self, 'scalebar_color_preview'):
            self._update_color_preview(self.scalebar_color_preview, scalebar_c)

        self._ui_update_active = True
        self._refresh_preview_for_current_image(force_reload_image=True)

    def _refresh_preview_for_current_image(self, force_reload_image=False):
        if not (0 <= self.current_index < len(self.file_paths)):
            self.preview_label.configure(text="无图片可预览", image=None);
            self.img_tk = None;
            return

        current_path = self.file_paths[self.current_index]
        settings = self.image_specific_settings.get(current_path)
        if not settings:
            self.preview_label.configure(text="错误: 图片设置丢失", image=None);
            self.img_tk = None;
            return

        try:
            mag_to_draw = settings[KEY_MAG]
            sw_to_draw = settings[KEY_SW]
            sample_to_draw = settings[KEY_SAMPLE]
            time_to_draw = settings[KEY_TIME]
            remark_to_draw = settings[KEY_REMARK]
            pos_to_draw = settings[KEY_POS]
            text_c_to_draw = settings.get(KEY_TEXT_COLOR, DEFAULT_TEXT_COLOR)
            scalebar_c_to_draw = settings.get(KEY_SCALEBAR_COLOR, DEFAULT_SCALEBAR_COLOR)

            img = Image.open(current_path)
            W_orig, H_orig = img.size
            scalebar_len_um = choose_scalebar_length(mag_to_draw, W_orig, sw_to_draw)

            img_with_info = draw_scalebar_and_info(img.copy(), mag_to_draw, sw_to_draw, scalebar_len_um,
                                                   pos_to_draw, sample_to_draw, time_to_draw, remark_to_draw,
                                                   text_color=text_c_to_draw,
                                                   scalebar_fill_color=scalebar_c_to_draw)
            img.close()

            preview_width = self.preview_label.winfo_width() - 10
            preview_height = self.preview_label.winfo_height() - 10
            if preview_width <= 10 or preview_height <= 10:
                preview_width, preview_height = 600, 500

            img_preview = img_with_info.copy();
            img_preview.thumbnail((preview_width, preview_height), Image.Resampling.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img_preview)

            self.preview_label.configure(image=self.img_tk, text="")
            img_with_info.close()
        except FileNotFoundError:
            self.preview_label.configure(text=f"预览失败: 文件未找到\n{os.path.basename(current_path)}", image=None);
            self.img_tk = None
        except Exception as e:
            print(f"Error refreshing preview for {current_path}: {e}")
            self.preview_label.configure(text=f"预览失败: {e}", image=None);
            self.img_tk = None

    def _get_current_ui_settings_validated(self):
        mag_str = self.magnification_var.get()
        sw_str = self.screen_width_var.get()
        mag_val, sw_val = 1.0, 1.0

        try:
            if mag_str:
                mag_val = float(int(float(mag_str)))
                if mag_val <= 0: raise ValueError("Magnification must be positive.")
        except ValueError:
            CTkMessagebox(title="错误", message="主面板中的放大倍数值无效。请输入一个正整数，或留空。", icon="cancel");
            return None

        try:
            if sw_str:
                sw_val = float(sw_str)
                if sw_val <= 0: raise ValueError("Screen width must be positive.")
        except ValueError:
            CTkMessagebox(title="错误", message="主面板中的图片参考宽度值无效。请输入一个正数，或留空。", icon="cancel");
            return None

        return {
            KEY_MAG: mag_val, KEY_SW: sw_val,
            KEY_SAMPLE: self.sample_name_var.get(), KEY_TIME: self.shoot_time_var.get(),
            KEY_REMARK: self.remark_var.get(), KEY_POS: self.scalebar_position_var.get(),
            KEY_TEXT_COLOR: self.text_color_var.get(),
            KEY_SCALEBAR_COLOR: self.scalebar_color_var.get()
        }

    def _open_apply_to_selected_dialog(self):
        if not self.file_paths:
            CTkMessagebox(title="提示", message="请先导入图片。", icon="info");
            return

        current_settings_for_dialog = self._get_current_ui_settings_validated()
        if not current_settings_for_dialog: return

        dialog_thumb_data = []
        temp_thumbs_for_dialog = []
        for path in self.file_paths:
            thumb_photo = None
            try:
                img = Image.open(path)
                img.thumbnail((50, 50), Image.Resampling.LANCZOS)
                thumb_photo = ImageTk.PhotoImage(img)
                temp_thumbs_for_dialog.append(thumb_photo)
                img.close()
            except Exception as e:
                print(f"Error creating thumbnail for dialog: {path} - {e}")
            dialog_thumb_data.append((path, thumb_photo))

        SelectImagesDialog(self, dialog_thumb_data, current_settings_for_dialog,
                           self._apply_settings_to_specific_images)

    def _apply_settings_to_specific_images(self, selected_paths, settings_to_apply):
        if not selected_paths: return

        applied_count = 0
        for path in selected_paths:
            if path in self.image_specific_settings:
                updated_settings = self.image_specific_settings[path].copy()
                updated_settings.update(settings_to_apply)
                self.image_specific_settings[path] = updated_settings
                applied_count += 1

        CTkMessagebox(title="成功", message=f"当前设置已应用到选定的 {applied_count} 张图片。", icon="check")

        if 0 <= self.current_index < len(self.file_paths):
            current_active_path = self.file_paths[self.current_index]
            if current_active_path in selected_paths:
                self._load_settings_for_active_image()

    def select_export_folder(self):
        folder = filedialog.askdirectory(title="选择导出文件夹")
        if folder:
            self.export_folder_var.set(folder);
            base_name = os.path.basename(folder);
            parent_name = os.path.basename(os.path.dirname(folder))
            text_path = f"...{os.sep}{parent_name}{os.sep}{base_name}" if len(folder) > 40 and parent_name else folder
            self.export_folder_label.configure(text=f"导出至: {text_path}")

    def process_images(self):
        if not self.file_paths: CTkMessagebox(title="错误", message="请先导入图片。", icon="cancel"); return
        export_dir = self.export_folder_var.get()
        if not export_dir:
            CTkMessagebox(title="错误", message="请选择导出文件夹。", icon="cancel")
            self.select_export_folder();
            export_dir = self.export_folder_var.get()
            if not export_dir: return

        processed, errors = 0, 0
        for i, path_img in enumerate(self.file_paths):
            try:
                settings = self.image_specific_settings.get(path_img, DEFAULT_SETTINGS.copy())
                img_original = Image.open(path_img);
                W, H = img_original.size

                mag = settings.get(KEY_MAG, DEFAULT_SETTINGS[KEY_MAG]);
                sw = settings.get(KEY_SW, DEFAULT_SETTINGS[KEY_SW])
                sample = settings.get(KEY_SAMPLE, DEFAULT_SETTINGS[KEY_SAMPLE]);
                time = settings.get(KEY_TIME, DEFAULT_SETTINGS[KEY_TIME])
                remark = settings.get(KEY_REMARK, DEFAULT_SETTINGS[KEY_REMARK]);
                pos = settings.get(KEY_POS, DEFAULT_SETTINGS[KEY_POS])
                text_c = settings.get(KEY_TEXT_COLOR, DEFAULT_SETTINGS[KEY_TEXT_COLOR])
                scalebar_c = settings.get(KEY_SCALEBAR_COLOR, DEFAULT_SETTINGS[KEY_SCALEBAR_COLOR])

                scalebar_val_um = choose_scalebar_length(mag, W, sw)
                img_processed = draw_scalebar_and_info(img_original.copy(), mag, sw, scalebar_val_um, pos,
                                                       sample, time, remark,
                                                       text_color=text_c, scalebar_fill_color=scalebar_c)
                img_original.close()
                base, ext = os.path.splitext(os.path.basename(path_img));
                save_ext = ext.lower() if ext.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.tif'] else '.png'
                save_path = os.path.join(export_dir, f"{base}_processed{save_ext}")
                img_processed.save(save_path);
                img_processed.close();
                processed += 1
            except Exception as e:
                print(f"Error processing {os.path.basename(path_img)}: {e}");
                errors += 1

        summary = f"批量处理完成。\n成功: {processed} 张图片。\n失败: {errors} 张图片。"
        icon_type = "check" if errors == 0 and processed > 0 else (
            "warning" if errors > 0 and processed > 0 else "cancel")
        CTkMessagebox(title="处理结果", message=summary, icon=icon_type)

    def _on_closing_app(self):
        if self.file_paths:
            if messagebox.askyesno("退出确认",
                                   "您已加载图片且可能有未保存的设置。\n确定要退出吗？所有当前编辑的设置将会丢失。",
                                   icon='warning', parent=self):
                self.destroy()
        else:
            self.destroy()


if __name__ == "__main__":
    app = MainWindowSEMApp()
    app.mainloop()