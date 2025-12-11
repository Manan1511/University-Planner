import flet as ft
import math
import datetime

# --- Constants ---
GRID_TIME_SLOTS = [
    # Theory Slots
    ("08:00 T", "08:00 - 08:50 (Theory)"),
    ("09:00 T", "09:00 - 09:50 (Theory)"),
    ("10:00 T", "10:00 - 10:50 (Theory)"),
    ("11:00 T", "11:00 - 11:50 (Theory)"),
    ("12:00 T", "12:00 - 12:50 (Theory)"),
    ("14:00 T", "14:00 - 14:50 (Theory)"),
    ("15:00 T", "15:00 - 15:50 (Theory)"),
    ("16:00 T", "16:00 - 16:50 (Theory)"),
    ("17:00 T", "17:00 - 17:50 (Theory)"),
    ("18:00 T", "18:00 - 18:50 (Theory)"),
    ("19:00 T", "19:00 - 19:50 (Theory)"),
    # Lab Slots
    ("08:00 L", "08:00 - 08:50 (Lab)"),
    ("08:51 L", "08:51 - 09:40 (Lab)"),
    ("09:51 L", "09:51 - 10:40 (Lab)"),
    ("10:41 L", "10:41 - 11:30 (Lab)"),
    ("11:40 L", "11:40 - 12:30 (Lab)"),
    ("12:31 L", "12:31 - 13:20 (Lab)"),
    ("14:00 L", "14:00 - 14:50 (Lab)"),
    ("14:51 L", "14:51 - 15:40 (Lab)"),
    ("15:51 L", "15:51 - 16:40 (Lab)"),
    ("16:41 L", "16:41 - 17:30 (Lab)"),
    ("17:40 L", "17:40 - 18:30 (Lab)"),
    ("18:31 L", "18:31 - 19:20 (Lab)"),
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# --- Logic & Data Models ---

class Subject:
    def __init__(self, name, attended=0, conducted=0, code="", professor="", schedule=None, assignments=None):
        self.name = name
        self.attended = attended
        self.conducted = conducted
        self.code = code
        self.professor = professor
        self.schedule = schedule if schedule else []
        self.assignments = assignments if assignments else []

    @property
    def percentage(self):
        if self.conducted == 0: return 0.0
        return (self.attended / self.conducted) * 100

    def get_bunk_message(self):
        current_ratio = self.attended / self.conducted if self.conducted > 0 else 0
        if current_ratio >= 0.75:
            if self.conducted == 0: return "Start a class!"
            can_bunk = math.floor((self.attended * 4 / 3) - self.conducted)
            return f"Safe to bunk: {can_bunk}"
        else:
            needed = math.ceil(3 * self.conducted - 4 * self.attended)
            if needed < 0: needed = 0
            return f"Attend next: {needed}"

    def to_dict(self):
        return {
            "name": self.name, "attended": self.attended, "conducted": self.conducted,
            "code": self.code, "professor": self.professor,
            "schedule": self.schedule, "assignments": self.assignments
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", "Unknown"), attended=data.get("attended", 0), conducted=data.get("conducted", 0),
            code=data.get("code", ""), professor=data.get("professor", ""),
            schedule=data.get("schedule", []), assignments=data.get("assignments", [])
        )

# --- Components ---

class HeroCard(ft.Container):
    def __init__(self):
        self.status_text = ft.Text("Welcome! Add subjects.", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
        super().__init__(
            content=ft.Column([ft.Text("Safe Bunk Prediction", color=ft.Colors.WHITE70, size=14), self.status_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=["#3D5CFF", "#2C3E50"]),
            border_radius=20, padding=20, height=160, alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLUE_GREY_200, offset=ft.Offset(0, 10))
        )

    def update_prediction(self, subjects):
        if not subjects:
            self.status_text.value = "Add subjects in 'Subjects' tab."
            return
        warning_subject = None
        best_bunk_subject = None
        max_bunks = -1
        for sub in subjects:
            if sub.conducted == 0: continue
            if sub.percentage < 75.0:
                if warning_subject is None: warning_subject = sub
            else:
                bunkable = math.floor((sub.attended * 4 / 3) - sub.conducted)
                if bunkable > max_bunks:
                    max_bunks = bunkable
                    best_bunk_subject = sub
        if warning_subject:
            needed = math.ceil(3 * warning_subject.conducted - 4 * warning_subject.attended)
            self.status_text.value = f"Risk! Attend {needed} in {warning_subject.name}."
        elif best_bunk_subject:
             self.status_text.value = f"Relax! Skip {max_bunks} in {best_bunk_subject.name}."
        else:
            self.status_text.value = "All good. Keep it up!"

class SubjectCard(ft.Container):
    def __init__(self, subject: Subject, on_click_callback):
        self.subject = subject
        status_color = ft.Colors.GREEN if self.subject.percentage >= 75.0 else ft.Colors.RED
        super().__init__(
            content=ft.Row([
                ft.Container(width=5, bgcolor=status_color, border_radius=ft.border_radius.only(top_left=12, bottom_left=12)),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(self.subject.code, size=10, weight=ft.FontWeight.W_900, color=ft.Colors.GREY_500), ft.Text(f"{self.subject.percentage:.1f}%", size=10, color=ft.Colors.GREY_500)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(self.subject.name, weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.BLACK87),
                        ft.Text(self.subject.professor if self.subject.professor else "No Prof Info", size=12, color=ft.Colors.GREY_600),
                        ft.Text(self.subject.get_bunk_message(), color=ft.Colors.BLUE_GREY, size=12, italic=True)
                    ], spacing=2),
                    padding=10, expand=True
                )
            ], spacing=0),
            bgcolor=ft.Colors.WHITE, border_radius=12, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)),
            margin=ft.margin.only(bottom=10), on_click=lambda e: on_click_callback(self.subject), ink=True
        )

# --- Visual Scheduler Component ---
class SlotSelector(ft.Container):
    def __init__(self):
        self.selected_slots = [] # List of {"day": d, "time": t}
        self.grid_controls = []
        
        # Header
        header_row = ft.Row([ft.Container(width=50)] + [ft.Container(content=ft.Text(d[:3], weight=ft.FontWeight.BOLD, size=12), width=40, alignment=ft.alignment.center) for d in DAYS])
        
        rows = [header_row]
        for time_label, time_val in GRID_TIME_SLOTS:
            row_ctls = [ft.Container(content=ft.Text(time_label, size=10), width=50, alignment=ft.alignment.center_right, padding=5)]
            for day in DAYS:
                btn = ft.Container(
                    width=40, height=30, bgcolor=ft.Colors.GREY_100, border_radius=4,
                    on_click=lambda e, d=day, t=time_val: self.toggle_slot(e, d, t),
                    data={"day": day, "time": time_val},
                    animate=ft.Animation(200, "easeOut"),
                )
                row_ctls.append(btn)
                self.grid_controls.append(btn)
            rows.append(ft.Row(row_ctls))

        super().__init__(
            content=ft.Column(rows, scroll=ft.ScrollMode.AUTO, height=300),
            border=ft.border.all(1, ft.Colors.GREY_200), border_radius=8, padding=10
        )

    def toggle_slot(self, e, day, time_val):
        ctl = e.control
        # Toggle logic
        search = next((s for s in self.selected_slots if s["day"] == day and s["time"] == time_val), None)
        if search:
            self.selected_slots.remove(search)
            ctl.bgcolor = ft.Colors.GREY_100
        else:
            self.selected_slots.append({"day": day, "time": time_val})
            ctl.bgcolor = ft.Colors.BLUE_400
        ctl.update()

    def load_schedule(self, schedule):
        self.selected_slots = [s.copy() for s in schedule]
        # Update UI
        for ctl in self.grid_controls:
            d = ctl.data["day"]
            t = ctl.data["time"]
            # check if in selected
            is_sel = any(s["day"] == d and s["time"] == t for s in self.selected_slots)
            ctl.bgcolor = ft.Colors.BLUE_400 if is_sel else ft.Colors.GREY_100
        # No implicit update here, done by parent opening dialog usually

# --- Main App ---

def main(page: ft.Page):
    page.title = "Attendance Manager V3"
    page.bgcolor = "#F5F7FA"
    page.padding = 0
    page.window_width = 390
    page.window_height = 844

    subjects = []
    stored_data = page.client_storage.get("subjects")
    if stored_data:
        subjects = [Subject.from_dict(d) for d in stored_data]

    def save_data():
        page.client_storage.set("subjects", [s.to_dict() for s in subjects])
        refresh_all_views()

    # --- DIALOGS ---
    
    # Scheduling Logic
    slot_selector = SlotSelector()

    def save_schedule_from_grid(e):
        if edit_subject_ref:
            # Overwrite or append? Let's Overwrite for simplicity in this "Edit" mode
            # or we merge. User requests "choose what slots they have". Implies setting state.
            edit_subject_ref.schedule = slot_selector.selected_slots.copy()
            save_data()
            page.close(sched_dialog)

    sched_dialog = ft.AlertDialog(
        title=ft.Text("Select Class Times"),
        content=slot_selector,
        actions=[ft.TextButton("Save Schedule", on_click=save_schedule_from_grid)]
    )

    # Edit Subject
    edit_subject_ref = None
    
    def on_attendance_change(delta_att, delta_cond):
        if edit_subject_ref:
            edit_subject_ref.attended += delta_att
            edit_subject_ref.conducted += delta_cond
            save_data()
            page.close(edit_dialog)

    def delete_sub(e):
        if edit_subject_ref:
            subjects.remove(edit_subject_ref)
            save_data()
            page.close(edit_dialog)

    # Edit Details Sub-Dialog
    details_name = ft.TextField(label="Name")
    details_code = ft.TextField(label="Code")
    details_prof = ft.TextField(label="Professor")
    
    def save_details_changes(e):
        if edit_subject_ref:
            edit_subject_ref.name = details_name.value
            edit_subject_ref.code = details_code.value
            edit_subject_ref.professor = details_prof.value
            save_data()
            page.close(details_dialog)
            page.close(edit_dialog)

    details_dialog = ft.AlertDialog(
        title=ft.Text("Edit Details"),
        content=ft.Column([details_name, details_code, details_prof], height=200),
        actions=[ft.TextButton("Save", on_click=save_details_changes)]
    )

    def open_details_dialog(e):
        details_name.value = edit_subject_ref.name
        details_code.value = edit_subject_ref.code
        details_prof.value = edit_subject_ref.professor
        page.open(details_dialog)

    def open_sched_dialog(e):
        # Load current
        slot_selector.load_schedule(edit_subject_ref.schedule)
        page.open(sched_dialog)
        # We need to trigger an update on the selector content potentially if not attached
        # Flet dialogs can be tricky with updates before open.
        # But load_schedule updates properties. When page.open happens, it should render correct color.

    edit_dialog = ft.AlertDialog(
        title=ft.Text("Manage Subject"),
        content=ft.Text("Update attendance or details."),
        actions=[
            ft.TextButton("Present (+1)", on_click=lambda e: on_attendance_change(1, 1), style=ft.ButtonStyle(color=ft.Colors.GREEN)),
            ft.TextButton("Absent", on_click=lambda e: on_attendance_change(0, 1), style=ft.ButtonStyle(color=ft.Colors.RED)),
            ft.TextButton("Edit Details", on_click=open_details_dialog),
            ft.TextButton("Edit Schedule", on_click=open_sched_dialog),
            ft.TextButton("Delete", on_click=delete_sub, style=ft.ButtonStyle(color=ft.Colors.GREY)),
        ]
    )

    def open_edit(subject):
        nonlocal edit_subject_ref
        edit_subject_ref = subject
        edit_dialog.title.value = subject.name
        page.open(edit_dialog)

    # 2. Add Subject (EXPANDED)
    add_name = ft.TextField(label="Subject Name")
    add_code = ft.TextField(label="Code (Optional)")
    add_prof = ft.TextField(label="Professor (Optional)")
    
    def save_new_sub(e):
        if add_name.value:
            new_sub = Subject(add_name.value, code=add_code.value, professor=add_prof.value)
            subjects.append(new_sub)
            add_name.value = ""
            add_code.value = ""
            add_prof.value = ""
            save_data()
            page.close(add_dialog)

    add_dialog = ft.AlertDialog(
        title=ft.Text("Add Subject"),
        content=ft.Column([add_name, add_code, add_prof], height=200),
        actions=[ft.TextButton("Add", on_click=save_new_sub), ft.TextButton("Cancel", on_click=lambda e: page.close(add_dialog))]
    )

    # 3. Add Assignment
    assign_title = ft.TextField(label="Title")
    assign_sub_dd = ft.Dropdown(label="Subject", expand=True)
    assign_date_field = ft.TextField(label="Deadline", read_only=True, expand=True)

    def on_date_change(e):
        if date_picker.value:
            assign_date_field.value = date_picker.value.strftime("%Y-%m-%d")
            assign_date_field.update()

    date_picker = ft.DatePicker(on_change=on_date_change)

    def save_assignment(e):
        if assign_title.value and assign_sub_dd.value and assign_date_field.value:
            for s in subjects:
                if s.name == assign_sub_dd.value:
                    s.assignments.append({"title": assign_title.value, "deadline": assign_date_field.value, "completed": False})
                    break
            save_data()
            page.close(assign_dialog)
    
    assign_dialog = ft.AlertDialog(
        title=ft.Text("Add Assignment"),
        content=ft.Column([
            assign_title,
            ft.Row([assign_sub_dd]),
            ft.Row([assign_date_field, ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e: page.open(date_picker))])
        ], height=240, spacing=20),
        actions=[ft.TextButton("Save", on_click=save_assignment)]
    )

    def open_assign_dialog(e):
        assign_sub_dd.options = [ft.dropdown.Option(s.name) for s in subjects]
        assign_date_field.value = ""
        assign_title.value = ""
        page.open(assign_dialog)


    # --- VIEWS ---

    # VIEW 1: HOME
    hero_card = HeroCard()
    today_disp = ft.Column()
    upcoming_disp = ft.Column()

    def build_home_view():
        today_name = datetime.datetime.now().strftime("%A")
        today_classes_ctls = []
        has_classes = False
        for sub in subjects:
            for slot in sub.schedule:
                if slot["day"] == today_name:
                    has_classes = True
                    # Simplified time display from "08:00 - 08:50 (Theory)" to "08:00"
                    time_short = slot["time"].split(' ')[0]
                    today_classes_ctls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(time_short, weight=ft.FontWeight.BOLD),
                                ft.Text(sub.code, size=12, color=ft.Colors.GREY),
                                ft.Text(sub.name, size=12, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ]),
                            bgcolor=ft.Colors.WHITE, padding=10, border_radius=10, width=100, height=80,
                            shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK12)
                        )
                    )
        
        today_disp.controls = [ft.Text("No classes today! 🎉", color=ft.Colors.GREY)] if not has_classes else [ft.Row(today_classes_ctls, scroll=ft.ScrollMode.HIDDEN)]

        all_assigns = []
        for s in subjects:
            for a in s.assignments:
                if not a.get("completed"):
                    all_assigns.append((s, a))
        
        # REMOVED the local + button here as requested
        upcoming_header = ft.Text("Upcoming Work", size=18, weight=ft.FontWeight.BOLD)
        
        if not all_assigns:
            upcoming_disp.controls = [ft.Text("No pending work.", color=ft.Colors.GREY)]
        else:
            upcoming_disp.controls = []
            for sub, a in all_assigns:
                upcoming_disp.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ASSIGNMENT, color=ft.Colors.ORANGE),
                            ft.Column([ft.Text(a["title"], weight=ft.FontWeight.BOLD), ft.Text(f"{sub.name} • {a['deadline']}", size=12, color=ft.Colors.GREY)]),
                            ft.IconButton(icon=ft.Icons.CHECK_CIRCLE_OUTLINE, on_click=lambda e, s=sub, assign=a: complete_assignment(s, assign))
                        ]),
                        bgcolor=ft.Colors.WHITE, padding=10, border_radius=10, margin=ft.margin.only(bottom=5)
                    )
                )
        
        hero_card.update_prediction(subjects)
        return ft.Container(
            content=ft.Column(
                controls=[
                    hero_card,
                    ft.Text("Today's Classes", size=18, weight=ft.FontWeight.BOLD),
                    today_disp,
                    upcoming_header,
                    upcoming_disp
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20
        )

    def complete_assignment(sub, assign):
        assign["completed"] = True
        refresh_all_views()
        page.update()

    # VIEW 2: TIMETABLE
    tt_tabs = ft.Tabs(selected_index=0, tabs=[ft.Tab(text=d[:3]) for d in DAYS], on_change=lambda e: update_tt_grid())
    tt_list = ft.Column()

    def update_tt_grid():
        day_idx = tt_tabs.selected_index
        day_name = DAYS[day_idx]
        tt_list.controls.clear()
        day_slots = []
        for sub in subjects:
            for slot in sub.schedule:
                if slot["day"] == day_name:
                    day_slots.append((slot["time"], sub))
        day_slots.sort(key=lambda x: x[0])

        if not day_slots:
            tt_list.controls.append(ft.Container(content=ft.Text("Free Day!", size=20, color=ft.Colors.GREY_400), alignment=ft.alignment.center, padding=50))
        else:
            for time, sub in day_slots:
                tt_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(time.split(' ')[0], weight=ft.FontWeight.BOLD, width=50),
                            ft.VerticalDivider(width=10, color=ft.Colors.GREY_300),
                            ft.Column([ft.Text(sub.name, weight=ft.FontWeight.BOLD), ft.Text(f"{sub.code} • {sub.professor}", size=12, color=ft.Colors.GREY)])
                        ]),
                        bgcolor=ft.Colors.WHITE, padding=15, border_radius=10, margin=ft.margin.only(bottom=10),
                        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK12)
                    )
                )
        if hasattr(tt_list, "page") and tt_list.page: tt_list.update()

    def build_timetable_view():
        return ft.Container(
            content=ft.Column([
                ft.Text("Weekly Schedule", size=24, weight=ft.FontWeight.BOLD),
                tt_tabs,
                ft.Container(content=tt_list, expand=True, padding=ft.padding.only(top=20))
            ]),
            padding=20, expand=True
        )

    # VIEW 3: SUBJECTS
    sub_list_col = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    
    def build_subjects_view():
        sub_list_col.controls = [SubjectCard(s, open_edit) for s in subjects]
        return ft.Container(
            content=ft.Column([
                ft.Text("All Subjects", size=24, weight=ft.FontWeight.BOLD),
                sub_list_col
            ]),
            padding=20, expand=True
        )

    # --- NAVIGATION ---
    
    body = ft.Container(expand=True)
    
    fab_add_subject = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=lambda e: page.open(add_dialog), bgcolor="#3D5CFF")
    fab_add_assign = ft.FloatingActionButton(icon=ft.Icons.ADD_TASK, on_click=open_assign_dialog, bgcolor=ft.Colors.ORANGE)

    def refresh_all_views():
        if nav.selected_index == 0:
            body.content = build_home_view()
            page.floating_action_button = fab_add_assign
        elif nav.selected_index == 1:
            body.content = build_timetable_view()
            update_tt_grid()
            page.floating_action_button = None
        elif nav.selected_index == 2:
            body.content = build_subjects_view()
            page.floating_action_button = fab_add_subject
        page.update()

    def on_nav_change(e):
        refresh_all_views()

    nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.Icons.CALENDAR_MONTH, label="Timetable"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, selected_icon=ft.Icons.BOOK, label="Subjects"),
        ],
        on_change=on_nav_change
    )

    page.add(body)
    page.navigation_bar = nav
    
    refresh_all_views()

if __name__ == "__main__":
    ft.app(target=main)
