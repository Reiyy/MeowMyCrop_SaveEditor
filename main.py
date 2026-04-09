import base64
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

XOR_KEY = [90,61,127,27,156,46,79,138,29,107,60,94,127,42,157,75,
           142,31,108,58,93,123,47,158,76,143,30,109,59,95,122,46]
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
        self.root.title("喵了个菜！存档编辑器 v1.0")
        self.root.geometry("500x650")
        self.root.minsize(450, 550)
        
        self.bg_color = "#e9eef6"
        self.card_color = "#FFFFFF"
        self.accent_color = "#4A90E2"
        
        ctk.set_appearance_mode("Light")
        self.root.configure(fg_color=self.bg_color)

        self.file_path = None
        self.data = None
        self.original_data = None
        self.entries = {}

        # 加载配置
        self.load_item_map()

        self.title_label = ctk.CTkLabel(root, text="喵了个菜！存档编辑器", font=ctk.CTkFont(size=20, weight="bold"), text_color="#333333")
        self.title_label.pack(pady=(15, 10))

        btn_frame = ctk.CTkFrame(root, fg_color="transparent")
        btn_frame.pack(pady=5)
        
        common_btn_set = {"width": 100, "height": 32, "corner_radius": 16, "font": ctk.CTkFont(size=12)}
        ctk.CTkButton(btn_frame, text="📂 打开", command=self.load_file, **common_btn_set).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="💾 保存", command=self.save_file, fg_color="#27AE60", hover_color="#2ECC71", **common_btn_set).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="🔄 重置", command=self.reset_data, fg_color="#E74C3C", hover_color="#FF5A4D", **common_btn_set).pack(side=tk.LEFT, padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(root, fg_color=self.bg_color, corner_radius=0)
        self.scroll_frame.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)

        self.log_box = ctk.CTkTextbox(root, height=100, corner_radius=12, border_width=2, border_color="#D1D9E6", fg_color="#F0F2F5", text_color="#555555")
        self.log_box.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.auto_load()

    def load_item_map(self):
        try:
            if os.path.exists("item_map.json"):
                with open("item_map.json", "r", encoding="utf-8") as f:
                    self.map = json.load(f)
            else:
                self.map = {"fruits": {}, "items": {}}
        except Exception as e:
            self.map = {"fruits": {}, "items": {}}

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
        self.render_section("🍎 水果", "fruitInventory", "fruitId", "fruits", "fruit")
        self.render_section("🎒 道具", "itemInventory", "itemId", "items", "item")

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
            
            ctk.CTkLabel(card, text=display_name, text_color="#333333").pack(side=tk.LEFT, padx=15, pady=10)
            
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
            
            ctk.CTkButton(ctrl_frame, text="-", command=lambda e=entry, s=step_value: self.change(e, -s), **btn_cfg).pack(side=tk.LEFT, padx=2)
            entry.pack(side=tk.LEFT, padx=5)
            ctk.CTkButton(ctrl_frame, text="+", command=lambda e=entry, s=step_value: self.change(e, s), **btn_cfg).pack(side=tk.LEFT, padx=2)

            self.entries[f"{prefix}_{iid}"] = entry

    def change(self, entry, delta):
        try:
            val = max(0, int(entry.get()) + delta)
            entry.delete(0, tk.END)
            entry.insert(0, str(val))
        except: pass

    def reset_data(self):
        if self.original_data:
            self.data = json.loads(json.dumps(self.original_data))
            self.build_ui()
            self.log("🔄 已重置修改")

    def save_file(self):
        if not self.file_path or not self.data:
            messagebox.showwarning("提示", "请先选择存档文件！")
            return

        confirm = messagebox.askyesno("确认保存", "确定要保存修改吗？\n\n警告：此操作不可逆，注意备份原始存档！")
        
        if not confirm:
            self.log("ℹ️ 已取消保存操作")
            return

        try:
            # 更新内部数据
            for key, entry in self.entries.items():
                parts = key.split("_")
                prefix = parts[0]
                iid = parts[1]
                data_key = "fruitInventory" if prefix == "fruit" else "itemInventory"
                id_key = "fruitId" if prefix == "fruit" else "itemId"
                for obj in self.data[data_key]:
                    if str(obj[id_key]) == iid:
                        obj["quantity"] = int(entry.get())

            # 写入加密文件
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(encrypt(json.dumps(self.data, ensure_ascii=False)))
            
            self.log("💾 已保存修改！")
        except Exception as e:
            self.log(f"❌ 保存失败: {e}")
            messagebox.showerror("错误", f"发生错误：{e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SaveEditor(root)
    root.mainloop()