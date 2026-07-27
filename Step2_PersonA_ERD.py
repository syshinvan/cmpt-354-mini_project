"""
Step 2 ERD - Item (+5 isa subclasses), Loan, Fine, AcquisitionCandidate.
Notation: rectangle=entity, double-rectangle=weak entity, oval=attribute, diamond=relationship,
double-diamond=identifying relationship, solid/dashed underline=key/partial key.
Person/Member boxes are dashed placeholders for Person B's domain.
"""
import math
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

# ============ Item + isa subclasses ============
rect('Item', 11, 11.5, 'Item')

tri('isa', 11, 13.15)
connect('Item', 'isa')
sub_x = {'PrintBook': 2, 'OnlineBook': 6.5, 'Magazine': 11, 'Journal': 15.5, 'Recording': 20}
for name, x in sub_x.items():
    rect(name, x, 14.9, name, w=2.3, h=1.0)
    connect(name, 'isa')

oval('a_isbn1', 0.5, 16.2, 'ISBN');           connect('a_isbn1', 'PrintBook')
oval('a_author1', 2.2, 16.6, 'author');       connect('a_author1', 'PrintBook')
oval('a_pub1', 3.7, 16.1, 'publisher');       connect('a_pub1', 'PrintBook')
oval('a_shelf', 0.9, 14.0, 'shelfLoc.');      connect('a_shelf', 'PrintBook')

oval('a_isbn2', 5.4, 16.5, 'ISBN');           connect('a_isbn2', 'OnlineBook')
oval('a_author2', 6.9, 16.7, 'author');       connect('a_author2', 'OnlineBook')
oval('a_fmt2', 8.4, 16.3, 'fileFormat');      connect('a_fmt2', 'OnlineBook')
oval('a_url2', 9.0, 15.2, 'accessURL');       connect('a_url2', 'OnlineBook')

oval('a_issue3', 10.0, 16.6, 'issueNumber');  connect('a_issue3', 'Magazine')
oval('a_pubdate3', 11.6, 16.9, 'pubDate');    connect('a_pubdate3', 'Magazine')
oval('a_pub3', 13.1, 16.4, 'publisher');      connect('a_pub3', 'Magazine')

oval('a_vol4', 14.5, 16.6, 'volume');         connect('a_vol4', 'Journal')
oval('a_issue4', 16.0, 16.9, 'issueNumber');  connect('a_issue4', 'Journal')
oval('a_subj4', 17.6, 16.4, 'subjectArea');   connect('a_subj4', 'Journal')

oval('a_artist5', 19.0, 16.5, 'artist');      connect('a_artist5', 'Recording')
oval('a_fmt5', 20.5, 16.8, 'format');         connect('a_fmt5', 'Recording')
oval('a_dur5', 22.0, 16.2, 'duration');       connect('a_dur5', 'Recording')

# Item's own attributes -- stacked on the right; one on the lower-left (clear of DonatedBy)
oval('i_id', 15.3, 13.0, 'itemID', key=True);          connect('i_id', 'Item')
oval('i_title', 15.6, 12.0, 'title');                   connect('i_title', 'Item')
oval('i_acq', 15.6, 11.0, 'acquisitionMethod', w=2.4);  connect('i_acq', 'Item')
oval('i_date', 15.3, 10.0, 'dateAdded');                connect('i_date', 'Item')
oval('i_status', 9.3, 10.3, 'status');                  connect('i_status', 'Item')

# ============ Loan (weak) ============
rect('Loan', 11, 7.4, 'Loan', weak=True)

diamond('For', 11, 9.6, 'For', dbl=True)
connect('For', 'Item', arrow=True)
connect('For', 'Loan')

# DonatedBy: Item -> Person (left side, clear of attributes)
rect('PersonDonated', 5.0, 11.5, 'Person /\nMember', w=2.4, h=1.2, dashed=True)
diamond('DonatedBy', 8.2, 11.5, 'DonatedBy', w=2.4, h=1.0)
connect('DonatedBy', 'Item')
connect('DonatedBy', 'PersonDonated', arrow=True)

oval('l_loandate', 15.0, 8.7, 'loanDate', partial=True);  connect('l_loandate', 'Loan')
oval('l_return', 15.0, 7.9, 'returnDate');                 connect('l_return', 'Loan')
oval('l_status', 15.0, 7.0, 'status');                     connect('l_status', 'Loan')
oval('l_due', 15.0, 6.1, 'dueDate');                       connect('l_due', 'Loan')

# By: Loan -> Person/Member (identifying, weak, left side clear of attributes)
rect('PersonBy', 5.0, 7.4, 'Person /\nMember', w=2.4, h=1.2, dashed=True)
diamond('By', 8.2, 7.4, 'By', w=2.4, h=1.0, dbl=True)
connect('By', 'Loan')
connect('By', 'PersonBy', arrow=True)

# ============ Fine (weak, depends on Loan) ============
rect('Fine', 11, 3.2, 'Fine', weak=True)
oval('f_amount', 7.3, 4.0, 'amountOwed');  connect('f_amount', 'Fine')
oval('f_issued', 7.3, 2.4, 'dateIssued');  connect('f_issued', 'Fine')
oval('f_paid', 14.7, 4.0, 'datePaid');     connect('f_paid', 'Fine')
oval('f_status', 14.7, 2.4, 'status');     connect('f_status', 'Fine')

diamond('IncursFine', 11, 5.3, 'Incurs\nFine', dbl=True)
connect('IncursFine', 'Loan', arrow=True)
connect('IncursFine', 'Fine')

# ============ AcquisitionCandidate ============
rect('AC', 20, 9.5, 'Acquisition\nCandidate', w=2.8)
oval('ac_id', 20, 11.4, 'candidateID', key=True);       connect('ac_id', 'AC')
oval('ac_title', 23.0, 10.6, 'proposedTitle', w=2.2);   connect('ac_title', 'AC')
oval('ac_fmt', 23.2, 9.3, 'format');                     connect('ac_fmt', 'AC')
oval('ac_cost', 23.0, 8.1, 'estimatedCost', w=2.1);      connect('ac_cost', 'AC')
oval('ac_status', 17.6, 10.7, 'status');                 connect('ac_status', 'AC')
oval('ac_dateprop', 17.6, 8.3, 'dateProposed');          connect('ac_dateprop', 'AC')

rect('PersonSuggested', 20, 5.2, 'Person', w=2.0, h=1.0, dashed=True)
diamond('Suggested', 20, 7.2, 'Suggested', w=2.2, h=1.0)
connect('Suggested', 'AC')
connect('Suggested', 'PersonSuggested', arrow=True)

plt.tight_layout()
out = '/Users/seungyeopshin/Desktop/CMPT_354/MiniProject/Step2_PersonA_ERD.pdf'
plt.savefig(out, bbox_inches='tight')
plt.savefig(out.replace('.pdf', '.png'), dpi=130, bbox_inches='tight')
print('saved:', out)
