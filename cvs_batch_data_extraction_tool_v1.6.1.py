import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

selected_folder = ""
column_vars = {}
all_columns = []
file_vars = {}
model_dict = {}
filtered_models = []


progress_info = {
    "current": 0,
    "total": 0
}

def read_csv_auto(file_path):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "gbk",
        "gb18030"
    ]

    last_error = None

    for enc in encodings:

        try:
            return pd.read_csv(
                file_path,
                encoding=enc
            )

        except Exception as e:
            last_error = e

    raise last_error

def get_target_csv_files(folder_path):

    csv_files = []

    for root_dir, dirs, files in os.walk(folder_path):

        dirs[:] = [
            d
            for d in dirs
            #if d.lower() != "result"
            if not d.lower().startswith("result")
        ]

        for file_name in files:

            if not file_name.lower().endswith(".csv"):
                continue

            csv_files.append(
                os.path.join(
                    root_dir,
                    file_name
                )
            )

    return csv_files


def count_total_csv():

    mode = mode_var.get()

    total = 0

    if mode == "merge":

        total = len(
            get_target_csv_files(
                selected_folder
            )
        )

    elif mode == "separate":

        for item in os.listdir(selected_folder):

            sub_folder = os.path.join(
                selected_folder,
                item
            )

            if not os.path.isdir(sub_folder):
                continue

            #if item.lower() == "result":
            if item.lower().startswith("result"):
                continue

            total += len(
                get_target_csv_files(
                    sub_folder
                )
            )

    else:

        total = len(
            get_target_csv_files(
                selected_folder
            )
        )

    return total

def build_model_dict(folder_path):

    global model_dict

    model_dict = {}

    csv_files = get_target_csv_files(
        folder_path
    )

    for file_path in csv_files:

        model_name = os.path.splitext(
            os.path.basename(file_path)
        )[0]

        if model_name not in model_dict:

            model_dict[model_name] = []

        model_dict[model_name].append(
            file_path
        )

    return sorted(
        model_dict.keys()
    )

def get_columns_from_first_csv(folder):

    csv_files = get_target_csv_files(
        folder
    )

    for file_path in csv_files:

        try:

            df = read_csv_auto(
                file_path
            )

            df.columns = (
                df.columns.astype(str)
                .str.strip()
                .str.replace(
                    '\ufeff',
                    '',
                    regex=False
                )
            )

            return list(df.columns)

        except:
            continue

    return []

def get_columns_from_selected_files():

    columns = set()

    selected_models = [

        model
        for model, var in file_vars.items()
        if var.get() == 1

    ]

    for model in selected_models:

        for file_path in model_dict.get(model, []):

            try:

                df = read_csv_auto(file_path)

                df.columns = (
                    df.columns.astype(str)
                    .str.strip()
                    .str.replace(
                        '\ufeff',
                        '',
                        regex=False
                    )
                )

                columns.update(df.columns)

            except:
                pass

    return sorted(columns)


def update_columns_by_selected_files():

    global all_columns

    # 保存当前已勾选字段
    old_selected = {

        col
        for col, var in column_vars.items()
        if var.get() == 1

    }

    all_columns = get_columns_from_selected_files()

    show_columns(all_columns)

    # 恢复仍然存在的勾选状态
    for col in old_selected:

        if col in column_vars:

            column_vars[col].set(1)


def on_column_mousewheel(event):

    canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )

    return "break"

def on_file_mousewheel(event):

    file_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )

    return "break"

def select_folder():

    global selected_folder
    global column_vars

    folder = filedialog.askdirectory(
        title="请选择文件夹"
    )

    if not folder:
        return

    selected_folder = folder

    folder_label.config(
        text=selected_folder
    )
    models = build_model_dict(
        selected_folder
    )

    show_model_list(
        models
    )

    update_columns_by_selected_files()

def select_all_files():

    for var in file_vars.values():
        var.set(1)
    update_columns_by_selected_files()

def deselect_all_files():

    for var in file_vars.values():
        var.set(0)
    update_columns_by_selected_files()


def invert_file_selection():

    for var in file_vars.values():

        if var.get():

            var.set(0)

        else:

            var.set(1)
    update_columns_by_selected_files()
            
def show_model_list(model_list):

    global file_vars

    file_vars = {}

    for widget in files_inner_frame.winfo_children():
        widget.destroy()

    for model in model_list:

        var = tk.IntVar(value=1)

        chk = tk.Checkbutton(
            files_inner_frame,
            text=model,
            variable=var,
            anchor="w",
            command=update_columns_by_selected_files
        )

        chk.pack(
            anchor="w",
            padx=5,
            pady=2
        )

        file_vars[model] = var

def apply_model_filter():

    include_text = (
        include_entry.get()
        .strip()
    )

    exclude_text = (
        exclude_entry.get()
        .strip()
    )

    all_models = list(
        model_dict.keys()
    )

    include_keywords = [

        x.strip().lower()

        for x in include_text.split(",")

        if x.strip()
    ]

    exclude_keywords = [

        x.strip().lower()

        for x in exclude_text.split(",")

        if x.strip()
    ]

    result = []

    for model in all_models:

        model_lower = model.lower()

        if include_keywords:

            if not any(

                key in model_lower

                for key in include_keywords

            ):

                continue
        if exclude_keywords:

            if any(

                key in model_lower

                for key in exclude_keywords

            ):

                continue

        result.append(
            model
        )

    show_model_list(
        result
    )

def show_columns(column_list):

    global column_vars

    for widget in columns_frame.winfo_children():
        widget.destroy()

    column_vars = {}

    for col in column_list:

        var = tk.IntVar(value=0)

        chk = tk.Checkbutton(
            columns_frame,
            text=col,
            variable=var,
            anchor="w"
        )

        chk.pack(
            anchor="w",
            padx=5,
            pady=2
        )

        column_vars[col] = var

def apply_column_filter():

    include_text = (
        column_include_entry.get()
        .strip()
    )

    exclude_text = (
        column_exclude_entry.get()
        .strip()
    )

    include_keywords = [

        x.strip().lower()

        for x in include_text.split(",")

        if x.strip()
    ]

    exclude_keywords = [

        x.strip().lower()

        for x in exclude_text.split(",")

        if x.strip()
    ]

    result = []

    for col in all_columns:

        col_lower = col.lower()

        if include_keywords:

            if not any(

                key in col_lower

                for key in include_keywords

            ):

                continue
        if exclude_keywords:

            if any(

                key in col_lower

                for key in exclude_keywords

            ):

                continue

        result.append(col)

    show_columns(result)

def select_all_columns():

    for var in column_vars.values():
        var.set(1)


def deselect_all_columns():

    for var in column_vars.values():
        var.set(0)


def save_dataframe(df, filepath):

    if output_var.get() == "Excel":

        df.to_excel(
            filepath + ".xlsx",
            index=False
        )

    else:

        df.to_csv(
            filepath + ".csv",
            index=False,
            encoding="utf-8-sig"
        )

def get_new_result_folder(base_folder):

    index = 1

    while True:

        folder_name = f"Result{index}"

        folder_path = os.path.join(
            base_folder,
            folder_name
        )

        if not os.path.exists(folder_path):

            os.makedirs(folder_path)

            return folder_path

        index += 1


def extract_folder(
        folder_path,
        selected_columns,
        failed_files
):

    global progress_info

    all_files = folder_path

    total_csv = len(all_files)
    success_csv = 0

    all_columns = []

    for file_path in all_files:

        try:

            df = read_csv_auto(
                file_path
            )

            df.columns = (
                df.columns.astype(str)
                .str.strip()
                .str.replace(
                    '\ufeff',
                    '',
                    regex=False
                )
            )

            file_base = os.path.splitext(
                os.path.basename(file_path)
            )[0]

            missing_cols = []

            for col in selected_columns:

                if col not in df.columns:
                    missing_cols.append(col)
                    continue

                temp = df[[col]].copy()

                temp.columns = [
                    f"{file_base}_{col}"
                ]

                all_columns.append(
                    temp
                )
                if missing_cols:

                    failed_files.append(    
                    f"{file_path} -> 缺少列: "
                    f"{', '.join(missing_cols)}"
                )

            success_csv += 1

        except Exception as e:

            failed_files.append(
                f"{file_path} -> {str(e)}"
            )

        progress_info["current"] += 1

        progress_bar["value"] = (
            progress_info["current"]
        )

        status_label.config(
            text=(
                f"处理中..."
                f" {progress_info['current']}"
                f"/{progress_info['total']}"
            )
        )

        root.update_idletasks()

    if len(all_columns) == 0:

        return (
            None,
            total_csv,
            success_csv
        )

    result = pd.concat(
        all_columns,
        axis=1
    )

    return (
        result,
        total_csv,
        success_csv
    )


def run_process():

    global progress_info

    if not selected_folder:

        messagebox.showerror(
            "错误",
            "请先选择文件夹"
        )

        return

    selected_columns = [

        col

        for col, var
        in column_vars.items()

        if var.get() == 1
    ]

    if not selected_columns:

        messagebox.showerror(
            "错误",
            "请至少选择一个列"
        )

        return

    result_dir = get_new_result_folder(
    selected_folder
        )

    failed_files = []

    total_csv = 0
    success_csv = 0

    progress_info = {
        "current": 0,
        "total": count_total_csv()
    }

    progress_bar["maximum"] = max(
        progress_info["total"],
        1
    )

    progress_bar["value"] = 0

    status_label.config(
        text="开始处理..."
    )

    root.update()

    mode = mode_var.get()

    if mode in ["merge", "both"]:
        selected_models = [

            model

            for model, var
            in file_vars.items()

            if var.get() == 1
        ]

        selected_files = []

        for model in selected_models:

            selected_files.extend(
                model_dict[model]
            )

        result, total, success = extract_folder(
            selected_files,
            selected_columns,
            failed_files
        )

        total_csv += total
        success_csv += success

        if result is not None:

            save_dataframe(
                result,
                os.path.join(
                    result_dir,
                    "Merged_Result"
                )
            )

    if mode in ["separate", "both"]:

        for item in os.listdir(selected_folder):

            sub_folder = os.path.join(
                selected_folder,
                item
            )

            if not os.path.isdir(sub_folder):
                continue

            #if item.lower() == "result":
            if item.lower().startswith("result"):
                continue

            result, total, success = extract_folder(
                sub_folder,
                selected_columns,
                failed_files
            )

            total_csv += total
            success_csv += success

            if result is not None:

                save_dataframe(
                    result,
                    os.path.join(
                        result_dir,
                        f"{item}_Result"
                    )
                )

    if failed_files:

        with open(
            os.path.join(
                result_dir,
                "failed_files.txt"
            ),
            "w",
            encoding="utf-8"
        ) as f:

            for line in failed_files:
                f.write(line + "\n")

    progress_bar["value"] = progress_bar["maximum"]

    status_label.config(
        text=f"完成，共处理 {progress_info['total']} 个文件"
    )

    messagebox.showinfo(
        "完成",
        f"处理完成\n\n"
        f"CSV数量：{total_csv}\n"
        f"成功：{success_csv}\n"
        f"失败记录：{len(failed_files)}\n\n"
        f"结果目录：\n{result_dir}"
    )


# GUI页面设计
root = tk.Tk()

root.title("CSV文件批量提取工具V1.6")
root.geometry("650x793")
root.minsize(650, 700)
style = ttk.Style()

try:
    style.theme_use("vista")
except:
    try:
        style.theme_use("winnative")
    except:
        pass

style.configure(
    "Title.TLabel",
    font=("Microsoft YaHei UI", 18)
)

style.configure(
    "TLabelframe",
    padding=10
)

main_canvas = tk.Canvas(
    root,
    bg="white",
    highlightthickness=0
)

main_scrollbar = ttk.Scrollbar(
    root,
    orient="vertical",
    command=main_canvas.yview
)

main_canvas.configure(
    yscrollcommand=main_scrollbar.set
)

main_scrollbar.pack(
    side="right",
    fill="y"
)

main_canvas.pack(
    side="left",
    fill="both",
    expand=True
)

main_frame = ttk.Frame(
    main_canvas
)

main_window = main_canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor="nw"
)

def resize_main_frame(event):

    main_canvas.itemconfig(
        main_window,
        width=event.width
    )

main_canvas.bind(
    "<Configure>",
    resize_main_frame
)

def on_main_mousewheel(event):

    main_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )

def update_main_scrollregion(event=None):

    main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )

main_frame.bind(
    "<Configure>",
    update_main_scrollregion
)

root.bind_all(
    "<MouseWheel>",
    on_main_mousewheel
)

title_label = ttk.Label(
    main_frame,
    text="CSV文件批量提取工具",
    style="Title.TLabel"
)

title_label.pack(
    pady=(0, 5)
)

folder_frame = ttk.LabelFrame(
    main_frame,
    text="文件夹选择"
)

folder_frame.pack(
    fill="x",
    pady=5
)

ttk.Button(
    folder_frame,
    text="选择文件夹",
    command=select_folder
).pack(
    pady=2
)

folder_label = ttk.Label(
    folder_frame,
    text="尚未选择文件夹"
)

folder_label.pack(
    fill="x",
    padx=5,
    pady=5
)

file_frame = ttk.LabelFrame(
    main_frame,
    text="文件选择"
)

file_frame.pack(
    fill="x",
    pady=5
)

filter_frame = ttk.Frame(
    file_frame
)

filter_frame.pack(
    fill="x",
    padx=5,
    pady=5
)

ttk.Label(
    filter_frame,
    text="包含："
).pack(
    side="left"
)

include_entry = ttk.Entry(
    filter_frame,
    width=20
)

include_entry.pack(
    side="left",
    padx=5
)

ttk.Label(
    filter_frame,
    text="排除："
).pack(
    side="left"
)

exclude_entry = ttk.Entry(
    filter_frame,
    width=20
)

exclude_entry.pack(
    side="left",
    padx=5
)

ttk.Button(
    filter_frame,
    text="应用筛选",
    command=apply_model_filter
).pack(
    side="left"
)

file_list_frame = ttk.Frame(
    file_frame
)

file_list_frame.pack(
    fill="both",
    expand=True
)

file_canvas = tk.Canvas(
    file_list_frame,
    height=180,
    bg="white",
    highlightthickness=0
)

file_scrollbar = ttk.Scrollbar(
    file_list_frame,
    orient="vertical",
    command=file_canvas.yview
)

files_inner_frame = tk.Frame(
    file_canvas,
    bg="white"
)

files_inner_frame.bind(
    "<Configure>",
    lambda e:
    file_canvas.configure(
        scrollregion=file_canvas.bbox("all")
    )
)

file_canvas.create_window(
    (0,0),
    window=files_inner_frame,
    anchor="nw"
)

file_canvas.configure(
    yscrollcommand=file_scrollbar.set
)

file_canvas.bind(
    "<MouseWheel>",
    on_file_mousewheel
)

file_scrollbar.pack(
    side="right",
    fill="y"
)

file_canvas.pack(
    side="left",
    fill="both",
    expand=True
)

file_btn_frame = ttk.Frame(
    file_frame
)

file_btn_frame.pack(
    fill="x",
    pady=5
)

ttk.Button(
    file_btn_frame,
    text="全选",
    command=select_all_files
).pack(
    side="left",
    padx=5
)

ttk.Button(
    file_btn_frame,
    text="取消全选",
    command=deselect_all_files
).pack(
    side="left",
    padx=5
)

column_frame = ttk.LabelFrame(
    main_frame,
    text="字段选择"
)

column_frame.pack(
    fill="both",
    expand=True,
    pady=8
)

column_filter_frame = ttk.Frame(
    column_frame
)

column_filter_frame.pack(
    fill="x",
    padx=5,
    pady=5
)

ttk.Label(
    column_filter_frame,
    text="包含："
).pack(
    side="left"
)

column_include_entry = ttk.Entry(
    column_filter_frame,
    width=20
)

column_include_entry.pack(
    side="left",
    padx=5
)

ttk.Label(
    column_filter_frame,
    text="排除："
).pack(
    side="left"
)

column_exclude_entry = ttk.Entry(
    column_filter_frame,
    width=20
)

column_exclude_entry.pack(
    side="left",
    padx=5
)

ttk.Button(
    column_filter_frame,
    text="应用筛选",
    command=apply_column_filter
).pack(
    side="left",
    padx=5
)

canvas = tk.Canvas(
    column_frame,
    bg="white",
    highlightthickness=0,
    height=180
)

scrollbar = ttk.Scrollbar(
    column_frame,
    orient="vertical",
    command=canvas.yview
)

columns_frame = tk.Frame(
    canvas,
    bg="white"
)

columns_frame.bind(
    "<Configure>",
    lambda e:
    canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window(
    (0, 0),
    window=columns_frame,
    anchor="nw"
)

canvas.configure(
    yscrollcommand=scrollbar.set
)

scrollbar.pack(
    side="right",
    fill="y"
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)

canvas.bind(
    "<MouseWheel>",
    on_column_mousewheel
)

column_btn_frame = ttk.Frame(
    main_frame
)

column_btn_frame.pack(
    fill="x",
    pady=5
)

ttk.Button(
    column_btn_frame,
    text="全选",
    command=select_all_columns
).pack(
    side="left",
    padx=5
)

ttk.Button(
    column_btn_frame,
    text="取消全选",
    command=deselect_all_columns
).pack(
    side="left",
    padx=5
)


setting_frame = ttk.Frame(
    main_frame
)

setting_frame.pack(
    fill="x",
    pady=10
)


mode_frame = ttk.LabelFrame(
    setting_frame,
    text="处理模式"
)

mode_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 5)
)

mode_var = tk.StringVar(
    value="both"
)

ttk.Radiobutton(
    mode_frame,
    text="全部汇总",
    variable=mode_var,
    value="merge"
).pack(
    anchor="w",
    pady=3,
    padx=10
)

ttk.Radiobutton(
    mode_frame,
    text="分文件夹输出",
    variable=mode_var,
    value="separate"
).pack(
    anchor="w",
    pady=3,
    padx=10
)

ttk.Radiobutton(
    mode_frame,
    text="两种都输出",
    variable=mode_var,
    value="both"
).pack(
    anchor="w",
    pady=3,
    padx=10
)

output_frame = ttk.LabelFrame(
    setting_frame,
    text="输出格式"
)

output_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(5, 0)
)

output_var = tk.StringVar(
    value="Excel"
)

ttk.Radiobutton(
    output_frame,
    text="Excel (.xlsx)",
    variable=output_var,
    value="Excel"
).pack(
    anchor="w",
    pady=3,
    padx=10
)

ttk.Radiobutton(
    output_frame,
    text="CSV (.csv)",
    variable=output_var,
    value="CSV"
).pack(
    anchor="w",
    pady=3,
    padx=10
)

start_btn = tk.Button(
    main_frame,
    text="开始处理",
    command=run_process,
    bg="#2E7D32",
    fg="white",
    font=("Microsoft YaHei UI", 13),
    width=16,
    height=1,
    relief="flat",
    cursor="hand2"
)

start_btn.pack(
    pady=5
)

progress_frame = ttk.LabelFrame(
    main_frame,
    text="处理进度"
)

progress_frame.pack(
    fill="x",
    pady=5
)

progress_bar = ttk.Progressbar(
    progress_frame,
    mode="determinate"
)

progress_bar.pack(
    fill="x",
    padx=5,
    pady=5
)

status_label = ttk.Label(
    progress_frame,
    text="等待开始"
)

status_label.pack(
    pady=(0, 3)
)

root.mainloop()