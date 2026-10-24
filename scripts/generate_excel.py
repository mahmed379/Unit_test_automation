import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pathlib import Path

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Test Cases"

headers = ["ID", "Module", "Function", "Description", "Input", "Expected Result", "Type ECP/BVA", "Owner"]
ws.append(headers)

# Styling header
header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

thin_border = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9")
)

for col_num, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_num)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = header_align
    cell.border = thin_border

rows = [
    # Mohammad Ahmed (mahmed379)
    ("TC_M01", "table", "insert()", "Insert valid dictionary mapping into empty table", '{"name": "Alice", "role": "Engineer"}', "Document stored with doc_id 1", "ECP", "mahmed379"),
    ("TC_M02", "table", "insert()", "Insert non-mapping type (string/int)", '"not-a-dict"', "ValueError raised", "ECP", "mahmed379"),
    ("TC_M03", "table", "get()", "Get document with boundary ID 0 and negative IDs", "doc_id=0, doc_id=-1", "Returns None", "BVA", "mahmed379"),
    ("TC_M04", "table", "update()", "Unconditional update on all documents in table", 'fields={"archived": True}', "All documents updated, returns list of all doc_ids", "BVA", "mahmed379"),
    ("TC_M05", "queries", "__lt__()", "Comparison test just below threshold 50", "val=49, threshold=50", "Evaluates to True", "BVA", "mahmed379"),
    ("TC_M06", "queries", "__ge__()", "Comparison test exactly on threshold boundary 50", "val=50, threshold=50", "Evaluates to True", "BVA", "mahmed379"),
    ("TC_M07", "queries", "exists()", "Check key existence when value is None or False", '{"flag": None}', "Evaluates to True", "BVA", "mahmed379"),
    ("TC_M08", "storages", "read()", "Read on freshly initialized MemoryStorage", "None (no writes performed)", "Returns None", "ECP", "mahmed379"),
    ("TC_M09", "storages", "write()", "Write empty dictionary into MemoryStorage", "data={}", "Returns {} on subsequent read()", "BVA", "mahmed379"),
    # Wabil Rehman (Wabil-Rehman)
    ("TC_W01", "table", "insert_multiple()", "Batch insert multiple valid document mappings", '[{"item": "A"}, {"item": "B"}]', "Returns [1, 2], table len is 2", "ECP", "Wabil-Rehman"),
    ("TC_W02", "table", "remove()", "Remove document by doc_id list with boundary missing IDs", "doc_ids=[1, 999]", "Removes doc 1, silently skips 999, returns [1]", "BVA", "Wabil-Rehman"),
    ("TC_W03", "table", "upsert()", "Upsert on non-matching query inserts new document", 'doc={"task": "deploy"}, q.task == "deploy"', "Inserts new doc, returns new doc_id", "ECP", "Wabil-Rehman"),
    ("TC_W04", "table", "count()", "Count documents matching query with zero matches", "q.missing == True", "Returns integer 0", "BVA", "Wabil-Rehman"),
    ("TC_W05", "queries", "matches()", "Regex matching full string pattern with anchor", 'regex=r"^[a-z]+$", val="test"', "Evaluates to True", "ECP", "Wabil-Rehman"),
    ("TC_W06", "queries", "any()", "Sequence predicate any() on empty list boundary", "cond=[1, 2], val=[]", "Evaluates to False", "BVA", "Wabil-Rehman"),
    ("TC_W07", "queries", "one_of()", "Set inclusion test with target value present", 'val="admin", allowed=["admin", "root"]', "Evaluates to True", "ECP", "Wabil-Rehman"),
    ("TC_W08", "storages", "read()", "Read from 0-byte empty JSON file", 'path="empty.json", size=0 bytes', "Returns None", "BVA", "Wabil-Rehman"),
    ("TC_W09", "storages", "write()", "Overwrite large JSON file with smaller JSON payload", "New payload shorter than prior file", "File truncated cleanly, no trailing bytes", "BVA", "Wabil-Rehman"),
    ("TC_W10", "storages", "write()", "Attempt write on JSONStorage opened in read-only mode r", 'access_mode="r"', "Raises IOError", "ECP", "Wabil-Rehman")
]

for row_idx, r in enumerate(rows, 2):
    ws.append(r)
    fill_color = "F9FBFD" if row_idx % 2 == 0 else "FFFFFF"
    row_fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    for col_idx in range(1, len(r) + 1):
        c = ws.cell(row=row_idx, column=col_idx)
        c.fill = row_fill
        c.font = Font(name="Calibri", size=10)
        c.border = thin_border
        if col_idx in (1, 2, 7, 8):
            c.alignment = Alignment(horizontal="center", vertical="center")
        else:
            c.alignment = Alignment(horizontal="left", vertical="center")

for col in ws.columns:
    max_len = max(len(str(cell.value or "")) for cell in col)
    col_letter = openpyxl.utils.get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

ws.row_dimensions[1].height = 26

out_path = Path("tests/excel")
out_path.mkdir(parents=True, exist_ok=True)
wb.save(out_path / "test_cases.xlsx")
print("Saved tests/excel/test_cases.xlsx successfully")
