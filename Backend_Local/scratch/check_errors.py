import os
import re

def check_files():
    project_root = r"c:\Users\Usuario para program\Documents\Proyecto"
    python_files = []
    for root, dirs, files in os.walk(project_root):
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    for file_path in python_files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
            # Check for 'database.' usage
            if re.search(r"\bdatabase\.", content):
                # Check if 'import database' is present
                if not re.search(r"\bimport database\b", content):
                    print(f"MISSING IMPORT: 'import database' in {file_path}")
            
            # Check for other potential issues (e.g., build_reporte_text but missing printer import)
            if "build_venta_equipo_text" in content and "from printing.printer" not in content:
                 if "def build_venta_equipo_text" not in content: # Not the file defining it
                    print(f"MISSING IMPORT: 'build_venta_equipo_text' from printing.printer in {file_path}")

            # Check for build_reporte_text
            if "build_reporte_text" in content and "from printing.printer" not in content:
                if "def build_reporte_text" not in content:
                    print(f"MISSING IMPORT: 'build_reporte_text' from printing.printer in {file_path}")

            # Check for build_nota_text
            if "build_nota_text" in content and "from printing.printer" not in content:
                if "def build_nota_text" not in content:
                    print(f"MISSING IMPORT: 'build_nota_text' from printing.printer in {file_path}")
            
            # Check for build_venta_text
            if "build_venta_text" in content and "from printing.printer" not in content:
                if "def build_venta_text" not in content:
                    print(f"MISSING IMPORT: 'build_venta_text' from printing.printer in {file_path}")

if __name__ == "__main__":
    check_files()
