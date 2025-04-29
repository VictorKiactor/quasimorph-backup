# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import shutil
import datetime
import threading
import time

# 获取 AppData\LocalLow 路径（Windows 存档特殊路径）
USER_APPDATA = os.environ.get('LOCALAPPDATA')
USER_LOCALLOW = os.path.join(os.path.dirname(USER_APPDATA), 'LocalLow')

TARGET_FOLDER = os.path.join(USER_LOCALLOW, "Magnum Scriptum Ltd", "Quasimorph")
BACKUP_FOLDER = os.path.join(USER_LOCALLOW, "Magnum Scriptum Ltd", "backups")
ASSETS_FOLDER = os.path.join(USER_LOCALLOW, "Magnum Scriptum Ltd", "assets")

os.makedirs(BACKUP_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)

COLORS = {
    'bg': '#001a0f',
    'frame': '#003322',
    'text': '#FF6600',
    'button_bg': '#002211',
    'progress_bg': '#001a0f',
    'progress_fill': '#FF6600',
    'highlight': '#004433',
    'selected': '#FF3333'
}

ICONS = {
    'play': '''
    ■■
    ■■■
    ■■■■
    ■■■
    ■■
    ''',
    'back': '''
    ■■■■■
    ■   ■
    ■   ■
    ■ ■ ■
    ■■■ ■
    ''',
    'x': '''
    ■■  ■■
     ■■■■
      ■■
     ■■■■
    ■■  ■■
    ''',
    'list': '''
    ■■■■■
    
    ■■■■■
    
    ■■■■■
    '''
}

class PixelButton:
    def __init__(self, canvas, x, y, width, height, text, command=None, is_icon=True):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text.upper()
        self.command = command
        self.is_icon = is_icon
        self.create_button()
        self.bind_events()

    def create_button(self):
        if hasattr(self, 'shapes'):
            for shape in self.shapes:
                self.canvas.delete(shape)
        if hasattr(self, 'icon_shapes'):
            for shape in self.icon_shapes:
                self.canvas.delete(shape)
        if hasattr(self, 'text_id'):
            self.canvas.delete(self.text_id)
        self.shapes = []
        offsets = [0, 3, 6]
        colors = ['#001a0f', '#003322', '#004433']
        for i, color in enumerate(colors):
            x1 = self.x + offsets[i]
            y1 = self.y + offsets[i]
            x2 = self.x + self.width - offsets[i]
            y2 = self.y + self.height - offsets[i]
            shape = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=color,
                width=2,
                fill='' if i < len(colors)-1 else COLORS['button_bg']
            )
            self.shapes.append(shape)
        if self.is_icon and self.text.lower() in ICONS:
            self.create_pixel_icon(ICONS[self.text.lower()])
        else:
            self.text_id = self.canvas.create_text(
                self.x + self.width//2,
                self.y + self.height//2,
                text=self.text,
                fill=COLORS['text'],
                font=('Minecraft', 14, 'bold'),
                justify='center'
            )
        self.bind_events()
        for shape in self.shapes:
            self.canvas.tag_raise(shape)
        if hasattr(self, 'icon_shapes'):
            for shape in self.icon_shapes:
                self.canvas.tag_raise(shape)
        if hasattr(self, 'text_id'):
            self.canvas.tag_raise(self.text_id)

    def create_pixel_icon(self, icon_data):
        lines = [line.strip() for line in icon_data.strip().split('\n')]
        pixel_size = 8
        start_x = self.x + (self.width - len(max(lines, key=len)) * pixel_size) // 2
        start_y = self.y + (self.height - len(lines) * pixel_size) // 2
        self.icon_shapes = []
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == '■':
                    pixel = self.canvas.create_rectangle(
                        start_x + x * pixel_size,
                        start_y + y * pixel_size,
                        start_x + (x + 1) * pixel_size,
                        start_y + (y + 1) * pixel_size,
                        fill=COLORS['text'],
                        outline=''
                    )
                    self.icon_shapes.append(pixel)

    def bind_events(self):
        for shape in self.shapes:
            self.canvas.tag_bind(shape, '<Button-1>', self.on_click)
            self.canvas.tag_bind(shape, '<Enter>', self.on_enter)
            self.canvas.tag_bind(shape, '<Leave>', self.on_leave)
        if hasattr(self, 'text_id'):
            self.canvas.tag_bind(self.text_id, '<Button-1>', self.on_click)
            self.canvas.tag_bind(self.text_id, '<Enter>', self.on_enter)
            self.canvas.tag_bind(self.text_id, '<Leave>', self.on_leave)
        if hasattr(self, 'icon_shapes'):
            for shape in self.icon_shapes:
                self.canvas.tag_bind(shape, '<Button-1>', self.on_click)
                self.canvas.tag_bind(shape, '<Enter>', self.on_enter)
                self.canvas.tag_bind(shape, '<Leave>', self.on_leave)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.canvas.itemconfig(self.shapes[-1], fill='#003322')
        for i, shape in enumerate(self.shapes):
            if i == 0:
                self.canvas.itemconfig(shape, outline='#FF6600')

    def on_leave(self, event):
        self.canvas.itemconfig(self.shapes[-1], fill=COLORS['button_bg'])
        for i, shape in enumerate(self.shapes):
            if i == 0:
                self.canvas.itemconfig(shape, outline='#001a0f')

class PixelScrollbar:
    def __init__(self, canvas, x, y, height, command=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.height = height
        self.command = command
        self.scroll_pos = 0
        self.total_items = 0
        self.visible_items = 0
        self.dragging = False
        self.last_y = 0
        self.step = 0.1
        self.thumb_min_height = 40
        self.track_height = height - 8
        self.create_scrollbar()
        self.bind_events()
        self.hide()
    def create_scrollbar(self):
        self.track = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + 20, self.y + self.height,
            outline=COLORS['frame'],
            width=2,
            fill=COLORS['bg']
        )
        self.thumb = self.canvas.create_rectangle(
            self.x + 4, self.y + 4,
            self.x + 16, self.y + 44,
            outline=COLORS['text'],
            width=2,
            fill=COLORS['button_bg']
        )
        self.decorations = []
        for i in range(3):
            line = self.canvas.create_line(
                self.x + 8, self.y + 16 + i * 8,
                self.x + 12, self.y + 16 + i * 8,
                fill=COLORS['text'],
                width=2
            )
            self.decorations.append(line)
    def bind_events(self):
        self.canvas.tag_bind(self.thumb, '<Button-1>', self.start_drag)
        self.canvas.tag_bind(self.thumb, '<B1-Motion>', self.drag)
        self.canvas.tag_bind(self.thumb, '<ButtonRelease-1>', self.stop_drag)
        self.canvas.tag_bind(self.track, '<Button-1>', self.track_click)
        for line in self.decorations:
            self.canvas.tag_bind(line, '<Button-1>', self.start_drag)
            self.canvas.tag_bind(line, '<B1-Motion>', self.drag)
            self.canvas.tag_bind(line, '<ButtonRelease-1>', self.stop_drag)
    def start_drag(self, event):
        self.dragging = True
        self.last_y = event.y
    def stop_drag(self, event):
        self.dragging = False
    def drag(self, event):
        if not self.dragging:
            return
        coords = self.canvas.coords(self.thumb)
        thumb_height = coords[3] - coords[1]
        delta_y = event.y - self.last_y
        new_y = coords[1] + delta_y
        min_y = self.y + 4
        max_y = self.y + self.track_height - thumb_height + 4
        new_y = max(min_y, min(new_y, max_y))
        self.canvas.moveto(self.thumb, self.x + 4, new_y)
        spacing = (thumb_height - 24) / 2
        for i, line in enumerate(self.decorations):
            self.canvas.coords(line,
                self.x + 8, new_y + spacing + i * 8,
                self.x + 12, new_y + spacing + i * 8
            )
        scroll_range = max_y - min_y
        if scroll_range > 0:
            self.scroll_pos = (new_y - min_y) / scroll_range
            if self.command:
                self.command(self.scroll_pos)
        self.last_y = event.y
    def track_click(self, event):
        coords = self.canvas.coords(self.thumb)
        thumb_height = coords[3] - coords[1]
        click_y = event.y - self.y
        new_y = click_y - thumb_height / 2
        min_y = 4
        max_y = self.track_height - thumb_height + 4
        if new_y < min_y:
            new_y = min_y
        elif new_y > max_y:
            new_y = max_y
        self.canvas.moveto(self.thumb, self.x + 4, self.y + new_y)
        spacing = (thumb_height - 24) / 2
        for i, line in enumerate(self.decorations):
            self.canvas.coords(line,
                self.x + 8, self.y + new_y + spacing + i * 8,
                self.x + 12, self.y + new_y + spacing + i * 8
            )
        scroll_range = max_y - min_y
        if scroll_range > 0:
            self.scroll_pos = new_y / max_y
            if self.command:
                self.command(self.scroll_pos)
    def show(self):
        self.canvas.itemconfig(self.track, state='normal')
        self.canvas.itemconfig(self.thumb, state='normal')
        for dec in self.decorations:
            self.canvas.itemconfig(dec, state='normal')
    def hide(self):
        self.canvas.itemconfig(self.track, state='hidden')
        self.canvas.itemconfig(self.thumb, state='hidden')
        for dec in self.decorations:
            self.canvas.itemconfig(dec, state='hidden')
    def update_thumb_size(self):
        if self.total_items <= self.visible_items:
            thumb_height = self.track_height
        else:
            ratio = self.visible_items / self.total_items
            thumb_height = max(self.thumb_min_height, min(self.track_height * ratio, self.track_height))
        coords = self.canvas.coords(self.thumb)
        current_y = coords[1]
        max_y = self.y + self.track_height - thumb_height + 4
        current_y = max(self.y + 4, min(current_y, max_y))
        self.canvas.coords(self.thumb,
            self.x + 4, current_y,
            self.x + 16, current_y + thumb_height
        )
        spacing = (thumb_height - 24) / 2
        for i, line in enumerate(self.decorations):
            self.canvas.coords(line,
                self.x + 8, current_y + spacing + i * 8,
                self.x + 12, current_y + spacing + i * 8
            )
    def set_scroll_range(self, total_items, visible_items):
        self.total_items = total_items
        self.visible_items = visible_items
        self.update_thumb_size()
    def scroll(self, delta):
        if not self.dragging and self.total_items > self.visible_items:
            coords = self.canvas.coords(self.thumb)
            thumb_height = coords[3] - coords[1]
            new_y = coords[1] + delta * self.step * self.track_height
            min_y = self.y + 4
            max_y = self.y + self.track_height - thumb_height + 4
            new_y = max(min_y, min(new_y, max_y))
            self.canvas.moveto(self.thumb, self.x + 4, new_y)
            spacing = (thumb_height - 24) / 2
            for i, line in enumerate(self.decorations):
                self.canvas.coords(line,
                    self.x + 8, new_y + spacing + i * 8,
                    self.x + 12, new_y + spacing + i * 8
                )
            scroll_range = max_y - min_y
            if scroll_range > 0:
                self.scroll_pos = (new_y - min_y) / scroll_range
                if self.command:
                    self.command(self.scroll_pos)

class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quasimorph Backup Tool")
        self.root.geometry("640x420")
        self.root.configure(bg=COLORS['bg'])
        
        self.canvas = tk.Canvas(
            root,
            width=640,
            height=420,
            bg=COLORS['bg'],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        self.current_mode = 'backup'
        self.selected_backup = None
        self.selected_index = None
        self.buttons = []
        self.backup_text_items = []
        self.create_layout()

    def create_layout(self):
        self.create_side_panel()
        self.create_main_display()

    def create_side_panel(self):
        x, y = 12, 10
        width, height = 120, 400
        self.create_pixel_frame(x, y, width, height)
        button_width = 88
        button_height = 70
        button_x = x + (width - button_width) // 2
        button_spacing = 20
        num_buttons = 3
        group_height = num_buttons * button_height + (num_buttons - 1) * button_spacing
        button_y = y + (height - group_height) // 2
        buttons = [
            ("play", self.confirm_backup),
            ("back", self.toggle_restore_mode),
            ("list", self.show_backup_list)
        ]
        for i, (text, command) in enumerate(buttons):
            button = PixelButton(
                self.canvas,
                button_x,
                button_y + i * (button_height + button_spacing),
                button_width,
                button_height,
                text,
                command
            )
            self.buttons.append(button)

    def create_main_display(self):
        x, y = 144, 10
        width, height = 480, 400
        self.create_pixel_frame(x, y, width, height)
        self.content_divider1 = self.canvas.create_rectangle(
            x + 12, y + 60, x + width - 12, y + 62,
            outline='#003322', fill='#003322', width=0)
        self.content_divider2 = self.canvas.create_rectangle(
            x + 12, y + height - 60, x + width - 12, y + height - 58,
            outline='#003322', fill='#003322', width=0)
        self.content_vdivider = self.canvas.create_rectangle(
            x + 60, y + 62, x + 62, y + height - 58,
            outline='#003322', fill='#003322', width=0)
        stair_color = '#002211'
        stair_size = 8
        self.canvas.create_rectangle(x, y, x+stair_size, y+stair_size, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+stair_size, y, x+2*stair_size, y+stair_size//2, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x, y+stair_size, x+stair_size//2, y+2*stair_size, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+width-stair_size, y, x+width, y+stair_size, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+width-2*stair_size, y, x+width-stair_size, y+stair_size//2, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+width-stair_size//2, y+stair_size, x+width, y+2*stair_size, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x, y+height-stair_size, x+stair_size, y+height, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x, y+height-2*stair_size, x+stair_size//2, y+height-stair_size, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+stair_size, y+height-stair_size//2, x+2*stair_size, y+height, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+width-stair_size, y+height-stair_size, x+width, y+height, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+width-stair_size//2, y+height-2*stair_size, x+width, y+height-stair_size, fill=stair_color, outline=stair_color)
        self.canvas.create_rectangle(x+width-2*stair_size, y+height-stair_size//2, x+width-stair_size, y+height, fill=stair_color, outline=stair_color)
        self.title_text = self.canvas.create_text(
            x + width//2,
            y + 80,
            text="QUASIMORPH",
            fill=COLORS['text'],
            font=("Minecraft", 28, "bold")
        )
        self.version_text = self.canvas.create_text(
            x + width//2,
            y + 120,
            text="BACKUP TOOL v1.0",
            fill=COLORS['text'],
            font=("Minecraft", 16, "bold")
        )
        self.hint_text = self.canvas.create_text(
            x + width/2,
            y + 30,
            text="CLICK LEFT BUTTON TO START",
            font=("Minecraft", 12),
            fill=COLORS['text'],
            anchor="center"
        )
        self.backup_list_text = self.canvas.create_text(
            x + 24,
            y + 70,
            text="",
            font=("Minecraft", 10),
            fill=COLORS['text'],
            anchor="nw"
        )
        self.scrollbar = PixelScrollbar(
            self.canvas,
            x + width - 24,
            y + 70,
            height - 140,
            command=self.on_scroll
        )
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        progress_width = 320
        progress_height = 28
        progress_x = x + width - progress_width - 40
        progress_y = y + height//2
        self.progress_frame = self.create_pixel_frame(
            progress_x,
            progress_y,
            progress_width,
            progress_height,
            color=COLORS['progress_bg']
        )
        self.progress_led = self.canvas.create_rectangle(
            progress_x - 16, progress_y + 8, progress_x - 8, progress_y + 16,
            fill=COLORS['text'], outline='#003322', width=2
        )
        self.progress_bar = self.canvas.create_rectangle(
            progress_x + 4,
            progress_y + 4,
            progress_x + 4,
            progress_y + progress_height - 4,
            fill=COLORS['progress_fill'],
            width=0
        )
        self.progress_dividers = []
        num_dividers = 7
        for i in range(1, num_dividers):
            px = progress_x + 4 + i * (progress_width - 8) // num_dividers
            divider = self.canvas.create_rectangle(
                px, progress_y + 4,
                px + 2, progress_y + progress_height - 4,
                fill='#003322', outline='#003322', width=0
            )
            self.progress_dividers.append(divider)
        self.progress_width = progress_width
        self.hide_progress_bar()

    def show_progress_bar(self):
        self.canvas.itemconfig(self.title_text, state='hidden')
        self.canvas.itemconfig(self.version_text, state='hidden')
        self.canvas.itemconfig(self.hint_text, state='normal')
        self.canvas.itemconfig(self.backup_list_text, state='hidden')
        for frame in self.progress_frame:
            self.canvas.itemconfig(frame, state='normal')
        self.canvas.itemconfig(self.progress_led, state='normal')
        self.canvas.itemconfig(self.progress_bar, state='normal')
        for divider in getattr(self, 'progress_dividers', []):
            self.canvas.itemconfig(divider, state='normal')

    def hide_progress_bar(self):
        for frame in self.progress_frame:
            self.canvas.itemconfig(frame, state='hidden')
        self.canvas.itemconfig(self.progress_led, state='hidden')
        self.canvas.itemconfig(self.progress_bar, state='hidden')
        for divider in getattr(self, 'progress_dividers', []):
            self.canvas.itemconfig(divider, state='hidden')

    def create_pixel_frame(self, x, y, width, height, color=None):
        offsets = [0, 3, 6, 9]
        colors = ['#001a0f', '#003322', '#004433', '#002211']
        frames = []
        for i, border_color in enumerate(colors):
            frame = self.canvas.create_rectangle(
                x + offsets[i],
                y + offsets[i],
                x + width - offsets[i],
                y + height - offsets[i],
                outline=border_color,
                width=2,
                fill=color if i == len(colors)-1 and color else ''
            )
            frames.append(frame)
        return frames

    def confirm_backup(self):
        if self.current_mode == 'list':
            self.reset_display()
        elif self.current_mode == 'backup':
            result = messagebox.askyesno("CONFIRM", "Start backup now?")
            if result:
                self.show_progress_bar()
                threading.Thread(target=self.perform_backup).start()
        elif self.current_mode == 'restore':
            self.reset_display()

    def toggle_restore_mode(self):
        if not self.selected_backup:
            if self.current_mode == 'backup':
                self.canvas.itemconfig(self.hint_text, text="ENTER LIST MODE FIRST", state='normal')
            else:
                self.canvas.itemconfig(self.hint_text, text="SELECT A VERSION FIRST", state='normal')
            return
        
        if self.current_mode == 'delete':
            result = messagebox.askyesno("CONFIRM", "Delete selected backup?")
            if result:
                self.show_progress_bar()
                self.canvas.itemconfig(self.hint_text, text="DELETING...", state='normal')
                threading.Thread(target=lambda: self.delete_backup(self.selected_backup)).start()
        elif self.current_mode == 'list':
            result = messagebox.askyesno("CONFIRM", "Restore selected backup?")
            if result:
                self.show_progress_bar()
                self.canvas.itemconfig(self.hint_text, text="RESTORING...", state='normal')
                threading.Thread(target=lambda: self.restore_backup(self.selected_backup)).start()
        else:
            self.reset_display()

    def reset_display(self):
        self.current_mode = 'backup'
        self.selected_backup = None
        self.selected_index = None
        
        for item in self.backup_text_items:
            self.canvas.delete(item)
        self.backup_text_items = []
        self.backup_list = []
        
        self.show_progress_bar()
        if hasattr(self, 'animate_progress'):
            self.animate_progress()
        
        self.canvas.itemconfig(self.title_text, state='normal')
        self.canvas.itemconfig(self.version_text, state='normal')
        self.canvas.itemconfig(self.hint_text, text="CLICK LEFT BUTTON TO START", state='normal')
        
        self.hide_progress_bar()
        
        if hasattr(self, 'scrollbar'):
            self.scrollbar.hide()
        
        for button in self.buttons:
            if button.text == 'X':
                button.text = 'BACK'
                button.is_icon = True
                button.create_button()

    def show_backup_list(self):
        if self.current_mode == 'list':
            self.show_progress_bar()
            threading.Thread(target=self.load_backup_list).start()
        elif self.current_mode == 'restore':
            self.current_mode = 'list'
            self.show_progress_bar()
            threading.Thread(target=self.load_backup_list).start()
        else:
            self.current_mode = 'list'
            self.show_progress_bar()
            threading.Thread(target=self.load_backup_list).start()

    def load_backup_list(self):
        for item in self.backup_text_items:
            self.canvas.delete(item)
        self.backup_text_items = []
        
        self.show_progress_bar()
        if hasattr(self, 'animate_progress'):
            self.animate_progress()
        
        self.backup_list = list_backups()
        if not self.backup_list:
            self.hide_progress_bar()
            self.canvas.itemconfig(self.hint_text, text="NO BACKUPS FOUND", state='normal')
            self.canvas.itemconfig(self.title_text, state='hidden')
            self.canvas.itemconfig(self.version_text, state='hidden')
            return

        self.backup_list.sort(reverse=True)
        
        if hasattr(self, 'scrollbar'):
            total_items = len(self.backup_list)
            visible_items = 6
            self.scrollbar.set_scroll_range(total_items, visible_items)
            self.scrollbar.scroll_pos = 0
            if total_items > visible_items:
                self.scrollbar.show()
                self.scrollbar.update_thumb_size()
            else:
                self.scrollbar.hide()
        
        visible_backups = self.backup_list[:6]
        y_offset = 100
        main_y_min = 10 + 12 + 62
        main_y_max = 10 + 400 - 12 - 58
        for i, backup in enumerate(visible_backups):
            try:
                dt = datetime.datetime.strptime(backup, "%Y%m%d_%H%M%S")
                label = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                label = backup
            item_y = y_offset + i * 40
            if main_y_min <= item_y <= main_y_max:
                text_item = self.canvas.create_text(
                    230,
                    item_y,
                    text=label,
                    font=("Minecraft", 14),
                    fill=COLORS['text'],
                    anchor="nw"
                )
                self.backup_text_items.append(text_item)
                self.canvas.tag_bind(text_item, '<Button-1>', lambda e, idx=i: self.on_backup_select(e, idx))
                self.canvas.tag_bind(text_item, '<Double-Button-1>', lambda e, idx=i: self.on_backup_double_click(e, idx))
        
        self.hide_progress_bar()
        self.canvas.itemconfig(self.hint_text, text="SELECT A VERSION", state='normal')
        self.canvas.itemconfig(self.title_text, state='hidden')
        self.canvas.itemconfig(self.version_text, state='hidden')
        
        self.selected_backup = None
        self.selected_index = None

    def on_backup_select(self, event, index):
        if not hasattr(self, 'backup_list') or not self.backup_list:
            return
        
        visible_items = 6
        start_index = int(self.scrollbar.scroll_pos * (len(self.backup_list) - visible_items))
        if start_index < 0:
            start_index = 0
        
        actual_index = start_index + index
        
        if 0 <= actual_index < len(self.backup_list):
            if self.selected_index is not None:
                prev_visible_index = self.selected_index - start_index
                if 0 <= prev_visible_index < len(self.backup_text_items):
                    self.canvas.itemconfig(self.backup_text_items[prev_visible_index], fill=COLORS['text'])
            
            self.selected_backup = self.backup_list[actual_index]
            self.selected_index = actual_index
            
            self.canvas.itemconfig(self.hint_text, text=f"SELECTED VERSION {actual_index + 1}", state='normal')
            
            if 0 <= index < len(self.backup_text_items):
                self.canvas.itemconfig(self.backup_text_items[index], fill=COLORS['selected'])
        else:
            if self.selected_index is not None:
                prev_visible_index = self.selected_index - start_index
                if 0 <= prev_visible_index < len(self.backup_text_items):
                    self.canvas.itemconfig(self.backup_text_items[prev_visible_index], fill=COLORS['text'])
            
            self.selected_backup = None
            self.selected_index = None
            self.canvas.itemconfig(self.hint_text, text="SELECT A VERSION", state='normal')

    def on_backup_double_click(self, event, index):
        self.on_backup_select(event, index)
        if self.selected_backup:
            self.current_mode = 'delete'
            self.canvas.itemconfig(self.hint_text, text="CLICK RESTORE TO DELETE", state='normal')
            for button in self.buttons:
                if button.text == 'BACK':
                    button.text = 'X'
                    button.is_icon = True
                    button.create_button()

    def delete_backup(self, backup_name):
        try:
            backup_path = os.path.join(BACKUP_FOLDER, backup_name)
            if os.path.exists(backup_path):
                if hasattr(self, 'animate_progress'):
                    self.animate_progress()
                shutil.rmtree(backup_path)
                self.canvas.itemconfig(self.hint_text, text="DELETED SUCCESSFULLY", state='normal')
                for button in self.buttons:
                    if button.text == 'X':
                        button.text = 'BACK'
                        button.is_icon = True
                        button.create_button()
                
                self.root.after(1500, self.auto_switch_to_list)
        except Exception as e:
            self.canvas.itemconfig(self.hint_text, text="DELETE FAILED", state='normal')
            messagebox.showerror("ERROR", f"Delete failed: {str(e)}")
        finally:
            self.hide_progress_bar()

    def auto_switch_to_list(self):
        self.current_mode = 'list'
        self.show_progress_bar()
        threading.Thread(target=self.load_backup_list).start()

    def perform_backup(self):
        self.canvas.itemconfig(self.hint_text, text="CREATING BACKUP", state='normal')
        self.canvas.itemconfig(self.title_text, state='hidden')
        self.canvas.itemconfig(self.version_text, state='hidden')
        self.animate_progress()
        name = create_backup()
        if name:
            self.canvas.itemconfig(self.hint_text, text="BACKUP COMPLETE", state='normal')
        else:
            self.canvas.itemconfig(self.hint_text, text="BACKUP FAILED", state='normal')
        self.hide_progress_bar()

    def restore_backup(self, backup_name):
        try:
            backup_path = os.path.join(BACKUP_FOLDER, backup_name)
            if os.path.exists(TARGET_FOLDER):
                if hasattr(self, 'animate_progress'):
                    self.animate_progress()
                shutil.rmtree(TARGET_FOLDER)
            shutil.copytree(backup_path, TARGET_FOLDER)
            self.canvas.itemconfig(self.hint_text, text="RESTORED SUCCESSFULLY", state='normal')
            
            self.root.after(1500, self.auto_switch_to_list)
        except Exception as e:
            self.canvas.itemconfig(self.hint_text, text="RESTORE FAILED", state='normal')
            messagebox.showerror("ERROR", f"Restore failed: {str(e)}")
        finally:
            self.hide_progress_bar()

    def animate_progress(self):
        num_dividers = 7
        bar_x1, bar_y1, bar_x2, bar_y2 = self.canvas.coords(self.progress_bar)
        bar_left = bar_x1
        bar_top = bar_y1
        bar_bottom = bar_y2
        bar_right = bar_x1 + self.progress_width - 8
        segment_width = (self.progress_width - 8) // num_dividers
        for i in range(num_dividers):
            seg_right = bar_left + (i + 1) * segment_width
            if seg_right > bar_right:
                seg_right = bar_right
            self.canvas.coords(
                self.progress_bar,
                bar_left,
                bar_top,
                seg_right,
                bar_bottom
            )
            self.root.update()
            self.root.after(120)
        self.canvas.coords(
            self.progress_bar,
            bar_left,
            bar_top,
            bar_right,
            bar_bottom
        )
        self.root.update()

    def on_scroll(self, scroll_pos):
        if not hasattr(self, 'backup_list') or not self.backup_list:
            return
        
        visible_items = 6
        total_items = len(self.backup_list)
        
        if total_items <= visible_items:
            return
        
        start_index = int(scroll_pos * (total_items - visible_items))
        if start_index < 0:
            start_index = 0
        
        visible_backups = self.backup_list[start_index:start_index + visible_items]
        
        for item in self.backup_text_items:
            self.canvas.delete(item)
        self.backup_text_items = []
        
        y_offset = 100
        main_y_min = 10 + 12 + 62
        main_y_max = 10 + 400 - 12 - 58
        for i, backup in enumerate(visible_backups):
            try:
                dt = datetime.datetime.strptime(backup, "%Y%m%d_%H%M%S")
                label = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                label = backup
            item_y = y_offset + i * 40
            if main_y_min <= item_y <= main_y_max:
                text_item = self.canvas.create_text(
                    230,
                    item_y,
                    text=label,
                    font=("Minecraft", 14),
                    fill=COLORS['text'],
                    anchor="nw"
                )
                self.backup_text_items.append(text_item)
                self.canvas.tag_bind(text_item, '<Button-1>', lambda e, idx=i: self.on_backup_select(e, idx))
                self.canvas.tag_bind(text_item, '<Double-Button-1>', lambda e, idx=i: self.on_backup_double_click(e, idx))
        
        self.selected_backup = None
        self.selected_index = None
        self.canvas.itemconfig(self.hint_text, text="SELECT A VERSION", state='normal')

    def on_mousewheel(self, event):
        if hasattr(self, 'backup_list') and self.backup_list and len(self.backup_list) > 6:
            delta = -1 if event.delta < 0 else 1
            self.scrollbar.scroll(-delta)

def create_backup():
    if not os.path.exists(TARGET_FOLDER):
        messagebox.showerror("错误", f"目标文件夹 '{TARGET_FOLDER}' 不存在。")
        return None
    backup_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)
    try:
        shutil.copytree(TARGET_FOLDER, backup_path)
        return backup_name
    except Exception as e:
        messagebox.showerror("错误", f"备份失败：{str(e)}")
        return None

def list_backups():
    backups = os.listdir(BACKUP_FOLDER)
    backups.sort(reverse=True)
    return backups

if __name__ == "__main__":
    root = tk.Tk()
    app = BackupGUI(root)
    root.mainloop()
