"""
Step 2 ERD - Person (+3 isa subclasses), Room, Event, AudienceGroup.
Notation: rectangle=entity, double-rectangle=weak entity, oval=attribute, diamond=relationship,
double-diamond=identifying relationship, solid/dashed underline=key/partial key.
Item/Loan/AcquisitionCandidate boxes are dashed placeholders for Person A's domain
(the three agreed touch-points: DonatedBy, Borrows/By, Suggested).
Helper functions are shared with Step2_PersonA_ERD.py so both halves render identically.
"""
import math
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(22, 17))
ax.set_xlim(0, 24)
ax.set_ylim(1, 18)
ax.axis('off')

SHAPES = {}  # name -> (cx, cy, w, h, kind)  kind in {rect, diamond, ellipse}

def _edge_point(cx, cy, w, h, kind, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return (cx, cy)
    hw, hh = w / 2, h / 2
    if kind == 'ellipse':
        denom = math.sqrt((dx / hw) ** 2 + (dy / hh) ** 2)
    elif kind == 'diamond':
        denom = abs(dx) / hw + abs(dy) / hh
    else:  # rect
        denom = max(abs(dx) / hw, abs(dy) / hh)
    t = 1 / denom
    return (cx + dx * t, cy + dy * t)

def rect(name, cx, cy, label, w=2.3, h=1.0, weak=False, dashed=False, fontsize=12):
    ls = 'dashed' if dashed else 'solid'
    ax.add_patch(Rectangle((cx-w/2, cy-h/2), w, h, fill=False, lw=1.6, ec='black', linestyle=ls))
    if weak:
        ax.add_patch(Rectangle((cx-w/2+0.1, cy-h/2+0.1), w-0.2, h-0.2, fill=False, lw=1.2, ec='black'))
    ax.text(cx, cy, label, ha='center', va='center', fontsize=fontsize, fontweight='bold')
    SHAPES[name] = (cx, cy, w, h, 'rect')

def oval(name, cx, cy, label, key=False, partial=False, w=1.9, h=0.62):
    ax.add_patch(Ellipse((cx, cy), w, h, fill=False, lw=1.1, ec='black'))
    ax.text(cx, cy, label, ha='center', va='center', fontsize=8.5)
    half = 0.045 * len(label) + 0.08
    if key:
        ax.plot([cx-half, cx+half], [cy-0.16, cy-0.16], color='black', lw=1.1)
    if partial:
        ax.plot([cx-half, cx+half], [cy-0.16, cy-0.16], color='black', lw=1.1,
                linestyle=(0, (2, 1.5)))
    SHAPES[name] = (cx, cy, w, h, 'ellipse')

def diamond(name, cx, cy, label, w=2.4, h=1.2, dbl=False, fontsize=9):
    pts = [(cx, cy+h/2), (cx+w/2, cy), (cx, cy-h/2), (cx-w/2, cy)]
    ax.add_patch(mpatches.Polygon(pts, closed=True, fill=False, lw=1.5, ec='black'))
    if dbl:
        pts2 = [(cx, cy+h/2-0.14), (cx+w/2-0.18, cy), (cx, cy-h/2+0.14), (cx-w/2+0.18, cy)]
        ax.add_patch(mpatches.Polygon(pts2, closed=True, fill=False, lw=1.1, ec='black'))
    ax.text(cx, cy, label, ha='center', va='center', fontsize=fontsize, fontweight='bold')
    SHAPES[name] = (cx, cy, w, h, 'diamond')

def tri(name, cx, cy, w=1.4, h=1.0):
    pts = [(cx, cy+h/2), (cx+w/2, cy-h/2), (cx-w/2, cy-h/2)]
    ax.add_patch(mpatches.Polygon(pts, closed=True, fill=False, lw=1.5, ec='black'))
    ax.text(cx, cy-0.05, 'isa', ha='center', va='center', fontsize=8)
    SHAPES[name] = (cx, cy, w, h, 'rect')

def connect(name1, name2, arrow=False, lw=1.1):
    cx1, cy1, w1, h1, k1 = SHAPES[name1]
    cx2, cy2, w2, h2, k2 = SHAPES[name2]
    p1 = _edge_point(cx1, cy1, w1, h1, k1, cx2, cy2)
    p2 = _edge_point(cx2, cy2, w2, h2, k2, cx1, cy1)
    if arrow:
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle='-|>', lw=lw+0.3, color='black'), zorder=1)
    else:
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', lw=lw, zorder=0)

# ============ Person + isa subclasses ============
rect('Person', 9, 11.8, 'Person')

tri('isa', 9, 13.6)
connect('Person', 'isa')
sub_x = {'Member': 4, 'Staff': 9, 'Volunteer': 14}
for name, x in sub_x.items():
    rect(name, x, 15.2, name, w=2.3, h=1.0)
    connect(name, 'isa')

oval('m_date', 2.4, 16.6, 'membershipDate', w=2.3);    connect('m_date', 'Member')
oval('m_status', 5.2, 16.9, 'membershipStatus', w=2.4); connect('m_status', 'Member')

oval('s_role', 7.4, 16.8, 'role');        connect('s_role', 'Staff')
oval('s_hire', 8.9, 17.2, 'hireDate');    connect('s_hire', 'Staff')
oval('s_salary', 10.4, 16.8, 'salary');   connect('s_salary', 'Staff')

oval('v_start', 14.2, 17.0, 'startDate');    connect('v_start', 'Volunteer')
oval('v_hours', 16.0, 16.5, 'hoursLogged', w=2.0); connect('v_hours', 'Volunteer')

# Supervises: Staff -> Staff self-relationship (many-one, optional: director has none).
# One auto edge + one manual elbow so the two lines don't overlap.
diamond('Supervises', 12.4, 16.3, 'Supervises', w=2.3, h=1.0)
connect('Supervises', 'Staff')
_sx, _sy = 12.4, 15.05   # elbow: diamond bottom vertex -> down -> left into Staff's right edge
ax.plot([12.4, 12.4], [15.8, _sy], color='black', lw=1.1, zorder=0)
ax.annotate('', xy=(10.15, _sy), xytext=(12.4, _sy),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color='black'), zorder=1)

# Person's own attributes -- fanned to the upper right, mirroring Item's in Person A's half
oval('p_id', 12.0, 13.8, 'personID', key=True);  connect('p_id', 'Person')
oval('p_name', 13.3, 13.1, 'name');              connect('p_name', 'Person')
oval('p_email', 13.7, 12.2, 'email');            connect('p_email', 'Person')
oval('p_phone', 13.5, 11.3, 'phone');            connect('p_phone', 'Person')
oval('p_addr', 12.7, 10.4, 'address');           connect('p_addr', 'Person')

# ============ Touch-points with Person A's domain (dashed placeholders) ============
rect('ItemPh', 1.7, 13.8, 'Item', w=2.0, h=1.0, dashed=True)
diamond('DonatedBy', 4.5, 13.1, 'DonatedBy', w=2.4, h=1.0)
connect('DonatedBy', 'ItemPh')
connect('DonatedBy', 'Person', arrow=True)

rect('LoanPh', 1.7, 11.3, 'Loan', w=2.0, h=1.0, dashed=True)
diamond('By', 4.5, 11.5, 'By', w=2.2, h=1.0, dbl=True)
connect('By', 'LoanPh')
connect('By', 'Person', arrow=True)

rect('ACPh', 1.7, 8.9, 'Acquisition\nCandidate', w=2.4, h=1.1, dashed=True)
diamond('Suggested', 4.6, 9.7, 'Suggested', w=2.2, h=1.0)
connect('Suggested', 'ACPh')
connect('Suggested', 'Person', arrow=True)

# ============ Attends: Person <-> Event (many-many, with registrationDate) ============
rect('Event', 9, 6.5, 'Event')
diamond('Attends', 9, 9.0, 'Attends', w=2.4, h=1.1)
connect('Attends', 'Person')
connect('Attends', 'Event')
oval('at_regdate', 6.3, 9.0, 'registrationDate', w=2.4); connect('at_regdate', 'Attends')

# Event's own attributes -- fanned to the lower left
oval('e_id', 5.3, 7.7, 'eventID', key=True);  connect('e_id', 'Event')
oval('e_title', 4.8, 6.9, 'title');           connect('e_title', 'Event')
oval('e_desc', 4.7, 6.1, 'description');      connect('e_desc', 'Event')
oval('e_type', 5.0, 5.3, 'eventType');        connect('e_type', 'Event')
oval('e_date', 5.8, 4.5, 'eventDate');        connect('e_date', 'Event')
oval('e_start', 7.2, 3.9, 'startTime');       connect('e_start', 'Event')
oval('e_end', 8.9, 3.6, 'endTime');           connect('e_end', 'Event')

# ============ HeldIn: Event -> Room (many-one, total on Event side) ============
rect('Room', 16.5, 6.5, 'Room')
diamond('HeldIn', 12.8, 6.5, 'HeldIn', w=2.3, h=1.0)
connect('HeldIn', 'Event')
connect('HeldIn', 'Room', arrow=True)

oval('r_id', 15.6, 8.2, 'roomID', key=True);  connect('r_id', 'Room')
oval('r_name', 17.5, 8.2, 'name');            connect('r_name', 'Room')
oval('r_cap', 18.9, 7.3, 'capacity');         connect('r_cap', 'Room')

# ============ RecommendedFor: Event <-> AudienceGroup (many-many) ============
rect('AudienceGroup', 16.5, 10.8, 'Audience\nGroup', w=2.6, h=1.1)
diamond('RecommendedFor', 12.9, 9.4, 'Recommended\nFor', w=2.8, h=1.2, fontsize=8)
connect('RecommendedFor', 'Event')
connect('RecommendedFor', 'AudienceGroup')

oval('g_name', 19.6, 11.6, 'groupName', key=True); connect('g_name', 'AudienceGroup')

plt.tight_layout()
out_dir = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(out_dir, 'Step2_PersonB_ERD.pdf')
plt.savefig(out, bbox_inches='tight')
plt.savefig(out.replace('.pdf', '.png'), dpi=130, bbox_inches='tight')
print('saved:', out)
