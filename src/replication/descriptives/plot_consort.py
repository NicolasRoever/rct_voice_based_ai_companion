import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from replication.descriptives.functions import calculate_screening_summary
from replication.plotting import set_plot_theme


def _draw_box(ax, cx, cy, width, height, text, color, fontsize=11):
    x = cx - width / 2
    y = cy - height / 2
    box = mpatches.FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02",
        linewidth=1.2,
        edgecolor=color,
        facecolor="white",
    )
    ax.add_patch(box)
    ax.text(
        cx,
        cy,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        wrap=True,
        multialignment="center",
    )


def _arrow(ax, x1, y1, x2, y2, color="#333333"):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2),
    )


def plot_consort_diagram_w124(df_wave1, df_merged):
    """CONSORT diagram including only waves 1, 2, and 4 (no 1-week or 1-month follow-ups)."""
    set_plot_theme()

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    primary = colors[0]
    secondary = colors[1]
    ctrl_color = colors[2]

    summary = calculate_screening_summary(df_wave1)
    n_wave1 = summary["screened"]
    failure_counts = summary["exclusions"]
    n_phone = summary["phone_invited"]

    n_randomized = len(df_merged)
    treat = df_merged[df_merged["sonia_treatment"] == 1]
    ctrl = df_merged[df_merged["sonia_treatment"] == 0]
    n_treat = len(treat)
    n_ctrl = len(ctrl)

    n_app_treat = int(treat["signed_up_in_app"].sum())
    n_app_ctrl = int(ctrl["signed_up_in_app"].sum())

    n_w4_treat = int(treat["gad7_score_w4"].notnull().sum())
    n_w4_ctrl = int(ctrl["gad7_score_w4"].notnull().sum())

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(-0.1, 12.3)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    box_w = 3.2
    box_h = 0.60
    center_x = 4.2
    treat_x = 1.9
    ctrl_x = 6.5

    y_wave1 = 6.6
    y_phone = 5.5
    y_rand = 4.4
    y_alloc = 3.3
    y_app = 2.2
    y_w4 = 1.1

    gap = box_h / 2

    _draw_box(
        ax,
        center_x,
        y_wave1,
        box_w,
        box_h,
        f"Screener survey\nn = {n_wave1:,}",
        primary,
    )
    _draw_box(
        ax,
        center_x,
        y_phone,
        box_w,
        box_h,
        f"Phone Screener Passed\nn = {n_phone}",
        primary,
    )
    _draw_box(
        ax,
        center_x,
        y_rand,
        box_w,
        box_h,
        f"Baseline survey\nn = {n_randomized}",
        primary,
    )

    _draw_box(
        ax,
        treat_x,
        y_alloc,
        box_w,
        box_h,
        f"Treatment (AI App)\nn = {n_treat}",
        secondary,
    )
    _draw_box(
        ax,
        ctrl_x,
        y_alloc,
        box_w,
        box_h,
        f"Control (Webapp)\nn = {n_ctrl}",
        ctrl_color,
    )

    _draw_box(
        ax,
        treat_x,
        y_app,
        box_w,
        box_h,
        f"App Download (AI App)\nn = {n_app_treat}",
        secondary,
    )
    _draw_box(
        ax,
        ctrl_x,
        y_app,
        box_w,
        box_h,
        f"App Signup (Control Webapp)\nn = {n_app_ctrl}",
        ctrl_color,
    )

    _draw_box(
        ax,
        treat_x,
        y_w4,
        box_w,
        box_h,
        f"Week 2 follow-up\nn = {n_w4_treat}",
        secondary,
    )
    _draw_box(
        ax,
        ctrl_x,
        y_w4,
        box_w,
        box_h,
        f"Week 2 follow-up\nn = {n_w4_ctrl}",
        ctrl_color,
    )

    _draw_box(
        ax,
        10.25,
        y_w4,
        3.5,
        1.2,
        "Did not complete the\nweek-2 survey\n"
        f"Treatment: n = {n_treat - n_w4_treat}\n"
        f"Control: n = {n_ctrl - n_w4_ctrl}\n"
        "Reasons unknown",
        primary,
        fontsize=9.5,
    )

    _arrow(ax, center_x, y_wave1 - gap, center_x, y_phone + gap)
    _arrow(ax, center_x, y_phone - gap, center_x, y_rand + gap)

    mid_y = (y_rand - gap + y_alloc + gap) / 2
    ax.plot([center_x, center_x], [y_rand - gap, mid_y], color="#333333", lw=1.2)
    ax.plot([treat_x, ctrl_x], [mid_y, mid_y], color="#333333", lw=1.2)
    _arrow(ax, treat_x, mid_y, treat_x, y_alloc + gap)
    _arrow(ax, ctrl_x, mid_y, ctrl_x, y_alloc + gap)

    _arrow(ax, treat_x, y_alloc - gap, treat_x, y_app + gap)
    _arrow(ax, treat_x, y_app - gap, treat_x, y_w4 + gap)

    _arrow(ax, ctrl_x, y_alloc - gap, ctrl_x, y_app + gap)
    _arrow(ax, ctrl_x, y_app - gap, ctrl_x, y_w4 + gap)

    excl_fontsize = 8.5
    excl_w = 4.8
    excl_cx = 12 - excl_w / 2

    excl_lines = ["Excluded (can fail multiple criteria):"]
    for label, count in failure_counts.items():
        pct = 100 * count / n_wave1 if n_wave1 > 0 else 0
        excl_lines.append(f"  {label}: {count:,} ({pct:.1f}%)")
    excl_text = "\n".join(excl_lines)

    line_h = 0.185
    excl_h = line_h * (len(excl_lines) + 0.8)
    excl_cy = (y_wave1 + y_phone) / 2
    x_excl = excl_cx - excl_w / 2
    y_excl = excl_cy - excl_h / 2

    excl_box = mpatches.FancyBboxPatch(
        (x_excl, y_excl),
        excl_w,
        excl_h,
        boxstyle="round,pad=0.02",
        linewidth=1.2,
        edgecolor=primary,
        facecolor="white",
    )
    ax.add_patch(excl_box)
    ax.text(
        x_excl + 0.12,
        excl_cy,
        excl_text,
        ha="left",
        va="center",
        fontsize=excl_fontsize,
        multialignment="left",
        family="monospace",
    )

    branch_y = (y_wave1 + y_phone) / 2
    ax.annotate(
        "",
        xy=(x_excl, excl_cy),
        xytext=(center_x + box_w / 2, branch_y),
        arrowprops=dict(
            arrowstyle="-|>", color=primary, lw=1.2, connectionstyle="arc3,rad=0"
        ),
    )

    plt.tight_layout()
    return fig
