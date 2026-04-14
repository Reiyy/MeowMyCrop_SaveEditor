import base64
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import time

XOR_KEY = [90,61,127,27,156,46,79,138,29,107,60,94,127,42,157,75,142,31,108,58,93,123,47,158,76,143,30,109,59,95,122,46]
PREFIX = "ENCRYPTED_V1:"

def decrypt(text):
    b64 = text[len(PREFIX):]
    data = base64.b64decode(b64)
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ XOR_KEY[i % len(XOR_KEY)]
    return result.decode("utf-8", errors="ignore")

def encrypt(text):
    data = text.encode("utf-8")
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ XOR_KEY[i % len(XOR_KEY)]
    return PREFIX + base64.b64encode(result).decode()

class SaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("喵了个菜！存档编辑器 v1.2")
        self.root.geometry("500x670")
        self.root.minsize(100, 170)
        
        try:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
            except NameError:
                script_dir = os.getcwd()
                
            icon_path = os.path.join(script_dir, "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"加载主图标失败: {e}")
        # ==========================================
        
        self.bg_color = "#e9eef6"
        self.card_color = "#FFFFFF"
        self.accent_color = "#4A90E2"
        
        ctk.set_appearance_mode("Light")
        self.root.configure(fg_color=self.bg_color)
        self.file_path = None
        self.data = None
        self.original_data = None
        self.entries = {}
        self.prev_quantities = {}
        self.icons = {}
        
        self.load_item_map()
        self.title_label = ctk.CTkLabel(root, text="喵了个菜！存档编辑器", font=ctk.CTkFont(size=20, weight="bold"), text_color="#333333")
        self.title_label.pack(pady=(15, 10))
        btn_frame = ctk.CTkFrame(root, fg_color="transparent")
        btn_frame.pack(pady=5)
        
        common_btn_set = {"width": 90, "height": 32, "corner_radius": 16, "font": ctk.CTkFont(size=12)}
        ctk.CTkButton(btn_frame, text="📂 打开", command=self.load_file, **common_btn_set).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="💾 保存", command=self.save_file, fg_color="#27AE60", hover_color="#2ECC71", **common_btn_set).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="🔄 重置", command=self.reset_data, fg_color="#E74C3C", hover_color="#FF5A4D", **common_btn_set).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="➕ 新增物品", command=self.open_add_dialog, fg_color="#F39C12", hover_color="#F1C40F", **common_btn_set).pack(side=tk.LEFT, padx=5)
        
        self.scroll_frame = ctk.CTkScrollableFrame(root, fg_color=self.bg_color, corner_radius=0)
        self.scroll_frame.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.log_box = ctk.CTkTextbox(root, height=120, corner_radius=12, border_width=2, border_color="#D1D9E6", fg_color="#F0F2F5", text_color="#555555")
        self.log_box.pack(fill=tk.X, padx=20, pady=(0, 20))
        self.log(f"版本:v1.2 260414 By 夜棂依Yareiy")
        self.log(f"发布地址：https://github.com/Reiyy/MeowMyCrop_SaveEditor")
        
        self.load_icons()
        self.auto_load()

    def load_item_map(self):
        try:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
            except NameError:
                script_dir = os.getcwd()
            
            json_path = os.path.join(script_dir, "item_map.json")
            
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    self.map = json.load(f)
            else:
                self.log(f"⚠️ 配置文件不存在: {json_path}")
                self.map = {"fruits": {}, "items": {}}
                
        except Exception as e:
            self.log(f"❌ 加载 JSON 失败: {e}")
            self.map = {"fruits": {}, "items": {}}

    def load_icons(self):
        self.icons = {}
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_dir = os.getcwd()
        
        for category in ["fruits", "items"]:
            for iid, config in self.map.get(category, {}).items():
                if isinstance(config, dict) and "img" in config:
                    img_rel = config.get("img")
                    if img_rel:
                        if os.path.isabs(img_rel):
                            img_path = img_rel
                        else:
                            img_path = os.path.join(script_dir, img_rel)
                        
                        if os.path.exists(img_path):
                            try:
                                pil_image = Image.open(img_path)
                                ctk_image = ctk.CTkImage(
                                    light_image=pil_image,
                                    size=(32, 32)
                                )
                                self.icons[f"{category}_{iid}"] = ctk_image
                            except Exception as e:
                                self.log(f"⚠️ 加载图标失败 {img_path}: {e}")
                        else:
                            self.log(f"⚠️ 图标文件不存在: {img_path} (物品ID: {iid})")
        
        loaded_count = len(self.icons)

    def log(self, msg):
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    def auto_load(self):
        base = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Nocturnal Games\MeowMyCrop\Saves")
        if not os.path.exists(base):
            self.log("❌ 找不到存档目录，请手动选择存档文件！")
            return
        
        target_path = os.path.join(base, "gamedata.gdat")
        if os.path.exists(target_path):
            self.log(f"✅ 已找到存档: {target_path}")
            self.open_file(target_path)
        else:
            self.log("❌ 未在默认目录找到 gamedata.gdat，请手动选择！")

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("存档文件", "gamedata.gdat"), ("所有文件", "*.*")])
        if path: self.open_file(path)

    def open_file(self, path):
        try:
            self.file_path = path
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if not content.startswith(PREFIX):
                self.log("❌ 存档格式不正确")
                return
            decrypted = decrypt(content)
            self.data = json.loads(decrypted)
            self.original_data = json.loads(decrypted)
            self.log(f"✅ 已加载: {os.path.basename(path)}")
            self.build_ui()
        except Exception as e:
            self.log(f"❌ 读取失败: {e}")

    def build_ui(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.entries.clear()
        self.prev_quantities.clear()
        self.render_plants()
        self.render_section("🍎 水果", "fruitInventory", "fruitId", "fruits", "fruit")
        self.render_section("🎒 道具", "itemInventory", "itemId", "items", "item")
        self.render_state()

    def render_section(self, title, data_key, id_key, map_key, prefix):
        ctk.CTkLabel(self.scroll_frame, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), anchor="w", padx=10)
        
        raw_items = self.data.get(data_key, [])
        try:
            sorted_items = sorted(raw_items, key=lambda x: int(x[id_key]))
        except (ValueError, KeyError):
            sorted_items = sorted(raw_items, key=lambda x: str(x[id_key]))
        
        for item in sorted_items:
            iid = str(item[id_key])
            if data_key == "fruitInventory" and iid not in ["1", "2", "3", "4"]:
                continue
            
            item_config = self.map.get(map_key, {}).get(iid, iid)
            display_name = f"ID: {iid}"
            step_value = 1
            
            if isinstance(item_config, dict):
                display_name = item_config.get("name", display_name)
                step_value = item_config.get("step", 1)
            else:
                display_name = item_config

            card = ctk.CTkFrame(self.scroll_frame, fg_color=self.card_color, corner_radius=12, border_width=1, border_color="#D1D9E6")
            card.pack(fill=tk.X, pady=4, padx=5)
            
            icon_key = f"{map_key}_{iid}"
            icon_img = self.icons.get(icon_key)
            icon_label = ctk.CTkLabel(
                card,
                image=icon_img,
                text="",
                width=36,
                height=36
            )
            icon_label.pack(side=tk.LEFT, padx=(15, 8), pady=10)

            ctk.CTkLabel(card, text=display_name, text_color="#333333").pack(side=tk.LEFT, padx=(0, 15), pady=10)
            
            ctrl_frame = ctk.CTkFrame(card, fg_color="transparent")
            ctrl_frame.pack(side=tk.RIGHT, padx=10)
            btn_cfg = {
                "width": 28,
                "height": 28,
                "corner_radius": 14,
                "fg_color": self.accent_color,
                "text_color": "#FFFFFF",
                "hover_color": "#357ABD"
            }
            
            entry = ctk.CTkEntry(ctrl_frame, width=60, height=28, justify="center", corner_radius=8, border_width=1, fg_color="#F8F9FA")
            entry.insert(0, str(item["quantity"]))

            key = f"{prefix}_{iid}"
            entry.bind("<FocusIn>", lambda event, e=entry, k=key: self.save_previous(e, k))
            entry.bind("<FocusOut>", lambda event, e=entry, p=prefix, i=iid: self.on_entry_focus_out(e, p, i))

            ctk.CTkButton(ctrl_frame, text="-", 
                          command=lambda e=entry, s=step_value, p=prefix, i=iid: self.change(e, -s, p, i),
                          **btn_cfg).pack(side=tk.LEFT, padx=2)
            entry.pack(side=tk.LEFT, padx=5)
            ctk.CTkButton(ctrl_frame, text="+", 
                          command=lambda e=entry, s=step_value, p=prefix, i=iid: self.change(e, s, p, i),
                          **btn_cfg).pack(side=tk.LEFT, padx=2)

            self.entries[key] = entry

    def save_previous(self, entry, key):
        try:
            self.prev_quantities[key] = int(entry.get())
        except:
            self.prev_quantities[key] = 1

    def change(self, entry, delta, prefix=None, iid=None):
        try:
            current = int(entry.get())
            new_val = max(0, current + delta)
            entry.delete(0, tk.END)
            entry.insert(0, str(new_val))

            if new_val == 0 and prefix is not None and iid is not None:
                if messagebox.askyesno(
                    "确认删除物品",
                    f"确定要删除物品 ID: {iid} 吗？\n\n此操作不可撤销。"
                ):
                    self.remove_item(prefix, iid)
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(current))
        except Exception:
            pass

    def on_entry_focus_out(self, entry, prefix, iid):
        try:
            val = int(entry.get().strip())
            if val <= 0:
                key = f"{prefix}_{iid}"
                old_val = self.prev_quantities.get(key, 1)
                if messagebox.askyesno(
                    "确认删除物品",
                    f"确定要删除物品 ID: {iid} 吗？\n\n此操作不可撤销。"
                ):
                    self.remove_item(prefix, iid)
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(old_val))
        except ValueError:
            pass

    def remove_item(self, prefix, iid):
        data_key = "fruitInventory" if prefix == "fruit" else "itemInventory"
        id_key = "fruitId" if prefix == "fruit" else "itemId"
        
        if data_key in self.data:
            original_len = len(self.data[data_key])
            self.data[data_key] = [
                obj for obj in self.data[data_key]
                if str(obj.get(id_key, "")) != str(iid)
            ]
            if len(self.data[data_key]) < original_len:
                self.build_ui()
                self.log(f"🗑️已删除物品: ID {iid}")
                return
        self.log(f"⚠️ 未找到要删除的物品 ID {iid}")

    def reset_data(self):
        if self.original_data:
            self.data = json.loads(json.dumps(self.original_data))
            self.build_ui()
            self.log("🔄 已重置修改")

    def sync_data_from_ui(self):
        if not self.data: return
        for key, entry in self.entries.items():
            parts = key.split("_")
            prefix = parts[0]
            iid = parts[1]
            data_key = "fruitInventory" if prefix == "fruit" else "itemInventory"
            id_key = "fruitId" if prefix == "fruit" else "itemId"
            
            if data_key in self.data:
                for obj in self.data[data_key]:
                    if str(obj[id_key]) == iid:
                        try:
                            obj["quantity"] = int(entry.get())
                        except ValueError:
                            pass

    def open_add_dialog(self):
        if not self.data:
            messagebox.showwarning("提示", "请先加载一个存档！")
            return
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("添加新物品")
        dialog.geometry("380x280")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.configure(fg_color=self.bg_color)

        ctk.CTkLabel(dialog, text="请选择要添加的物品", 
                     font=ctk.CTkFont(size=14, weight="bold"), 
                     text_color="#333333").pack(pady=(20, 15))

        type_var = tk.StringVar(value="水果")
        item_var = tk.StringVar(value="")
        available_items_map = {}

        def update_item_list(choice=None):
            is_fruit = (type_var.get() == "水果")
            data_key = "fruitInventory" if is_fruit else "itemInventory"
            id_key = "fruitId" if is_fruit else "itemId"
            map_key = "fruits" if is_fruit else "items"
            existing_ids = set()
            if data_key in self.data:
                for obj in self.data[data_key]:
                    existing_ids.add(str(obj[id_key]))
            available_items_map.clear()
            options = []
            for iid, config in self.map.get(map_key, {}).items():
                if str(iid) not in existing_ids:
                    display_name = config.get("name", f"未知") if isinstance(config, dict) else config
                    option_text = f"{display_name} (ID: {iid})"
                    available_items_map[option_text] = str(iid)
                    options.append(option_text)
            if not options:
                options = ["无可用物品 (已全部拥有或配置缺失)"]
                item_var.set(options[0])
                item_dropdown.configure(values=options, state="disabled")
                confirm_btn.configure(state="disabled")
            else:
                item_var.set(options[0])
                item_dropdown.configure(values=options, state="normal")
                confirm_btn.configure(state="normal")

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=tk.X, padx=30, pady=10)

        ctk.CTkLabel(frame, text="类型：", text_color="#333333", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=5, pady=10, sticky="e")
        type_dropdown = ctk.CTkOptionMenu(
            frame,
            variable=type_var,
            values=["水果", "道具"],
            command=update_item_list,
            fg_color="#F8F9FA",
            text_color="#333333",
            button_color=self.accent_color,
            button_hover_color="#357ABD",
            dropdown_fg_color=self.card_color,
            dropdown_text_color="#333333",
            dropdown_hover_color=self.bg_color,
            corner_radius=8
        )
        type_dropdown.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(frame, text="物品：", text_color="#333333", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=5, pady=10, sticky="e")
        item_dropdown = ctk.CTkOptionMenu(
            frame,
            variable=item_var,
            values=[""],
            fg_color="#F8F9FA",
            text_color="#333333",
            button_color=self.accent_color,
            button_hover_color="#357ABD",
            dropdown_fg_color=self.card_color,
            dropdown_text_color="#333333",
            dropdown_hover_color=self.bg_color,
            corner_radius=8
        )
        item_dropdown.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        frame.columnconfigure(1, weight=1)

        def confirm_add():
            sel_text = item_var.get()
            if sel_text not in available_items_map:
                return
            iid = available_items_map[sel_text]
            is_fruit = (type_var.get() == "水果")
            data_key = "fruitInventory" if is_fruit else "itemInventory"
            id_key = "fruitId" if is_fruit else "itemId"
            map_key = "fruits" if is_fruit else "items"
            config = self.map.get(map_key, {}).get(iid, {})
            step_value = config.get("step", 1) if isinstance(config, dict) else 1
            insert_id = iid
            try: insert_id = int(iid)
            except ValueError: pass
            if data_key not in self.data:
                self.data[data_key] = []
            self.data[data_key].append({id_key: insert_id, "quantity": step_value})
            self.sync_data_from_ui()
            self.build_ui()
            item_name = sel_text.split(" (")[0]
            self.log(f"➕ 已添加新物品: {item_name} (数量: {step_value})")
            dialog.destroy()

        confirm_btn = ctk.CTkButton(
            dialog,
            text="添加物品",
            command=confirm_add,
            fg_color=self.accent_color,
            hover_color="#357ABD",
            width=160,
            height=32,
            corner_radius=16,
            font=ctk.CTkFont(size=12)
        )
        confirm_btn.pack(pady=(15, 20))

        update_item_list()

    def render_state(self):
            if not self.data:
                return
            ctk.CTkLabel(
                self.scroll_frame,
                text="📊 增益状态",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=(15, 5), anchor="w", padx=10)
            card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=self.card_color,
                corner_radius=12,
                border_width=1,
                border_color="#D1D9E6"
            )
            card.pack(fill=tk.X, pady=6, padx=5)
            grid = ctk.CTkFrame(card, fg_color="transparent")
            grid.pack(fill=tk.X, padx=15, pady=10)

            ctk.CTkLabel(grid, text="增益剩余时间（秒）", width=80, anchor="w").grid(row=1, column=0, pady=6, sticky="w")
            buff_time_var = tk.StringVar(value=str(self.data.get("buffRemainingTime", 0.0)))
            buff_time = ctk.CTkEntry(grid, width=120, justify="center", textvariable=buff_time_var)
            buff_time.grid(row=1, column=1, padx=10)

            def _update_buff_time(*args):
                try:
                    self.data["buffRemainingTime"] = float(buff_time_var.get())
                except ValueError:
                    pass

            buff_time_var.trace_add("write", _update_buff_time)

    def render_plants(self):
        plants = self.data.get("plants", [])
        if not plants:
            return

        plant = plants[0]
        pid = str(plant.get("plantConfigId", ""))

        config = self.map.get("fruits", {}).get(pid, {})
        name = config.get("name", f"未知作物({pid})")
        max_growth = float(config.get("growthValue", 1))
        current_growth = float(plant.get("growthValue", 0))

        progress = min(current_growth / max_growth, 1.0)

        if progress >= 1:
            bar_color = "#27AE60"
        else:
            bar_color = "#F39C12"

        ctk.CTkLabel(
            self.scroll_frame,
            text="🌱 作物",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5), anchor="w", padx=10)

        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.card_color,
            corner_radius=14,
            border_width=1,
            border_color="#D1D9E6",
            height=90
        )
        card.pack(fill=tk.X, pady=6, padx=5)
        card.pack_propagate(False)

        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill=tk.X, padx=10, pady=(8, 4))

        icon_key = f"fruits_{pid}"
        icon = self.icons.get(icon_key)
        ctk.CTkLabel(top_frame, image=icon, text="").pack(side=tk.LEFT, padx=(5, 8))

        stage_map = ["幼苗", "初期", "后期", "成熟"]
        stage = stage_map[plant.get("currentStage", 0)]

        ctk.CTkLabel(
            top_frame,
            text=f"{name}（{stage}）",
            text_color="#333333",
            font=ctk.CTkFont(size=13)
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            top_frame,
            text="催熟",
            width=90,
            height=28,
            command=self.make_all_plants_mature
        ).pack(side=tk.RIGHT, padx=5)

        progress_bar = ctk.CTkProgressBar(
            card,
            height=10,
            corner_radius=5,
            fg_color="#E0E0E0",
            progress_color=bar_color
        )
        progress_bar.pack(fill=tk.X, padx=15, pady=(2, 2))
        progress_bar.set(progress)

        ctk.CTkLabel(
            card,
            text=f"{int(current_growth)} / {int(max_growth)}",
            text_color="#666666",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="e", padx=15, pady=(0, 6))

    def make_all_plants_mature(self):
        plants = self.data.get("plants", [])
        if not plants:
            return

        pid = str(plants[0].get("plantConfigId", ""))
        config = self.map.get("fruits", {}).get(pid)

        if not config:
            self.log("❌ 未找到作物配置，无法成熟")
            return

        for plant in plants:
            plant["currentStage"] = 3
            plant["growthValue"] = config.get("growthValue", 0)
            plant["currentFruitCount"] = config.get("currentFruitCount", 1)

        self.build_ui()
        self.log("🌱 作物已催熟！")

    def save_file(self):
        if not self.file_path or not self.data:
            messagebox.showwarning("提示", "请先选择存档文件！")
            return
        confirm = messagebox.askyesno("确认保存", "确定要保存修改吗？\n\n警告：此操作不可逆，注意备份原始存档！")
        
        if not confirm:
            self.log("ℹ️ 已取消保存操作")
            return
        try:
            self.sync_data_from_ui()
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(encrypt(json.dumps(self.data, ensure_ascii=False, indent=4)))
            self.log("💾 已保存修改！")
        except Exception as e:
            self.log(f"❌ 保存失败: {e}")
            messagebox.showerror("错误", f"发生错误：{e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SaveEditor(root)
    root.mainloop()