import sqlite3

DB_PATH = "pos_420_smoking_vibes.db"

def borrar_todas_las_facturas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas")
    conn.commit()
    conn.close()
    print("✅ Todas las facturas/ventas han sido eliminadas.")

if __name__ == "__main__":
    borrar_todas_las_facturas()
