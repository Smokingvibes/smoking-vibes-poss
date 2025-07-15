"""
Script de migración para actualizar el sistema POS de Smoking Vibes
Este script debe ejecutarse una sola vez para migrar la base de datos existente
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "pos_420_smoking_vibes.db"
BACKUP_PATH = f"backup_antes_migracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"


def hacer_backup():
    """Crea un backup de la base de datos antes de migrar"""
    if os.path.exists(DB_PATH):
        print(f"Creando backup en: {BACKUP_PATH}")
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print("✓ Backup creado exitosamente")
    else:
        print("⚠ No se encontró base de datos existente")


def migrar_base_datos():
    """Migra la estructura de la base de datos"""
    print("\nIniciando migración de base de datos...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Verificar estructura de tabla ventas
        cursor.execute("PRAGMA table_info(ventas)")
        columnas_ventas = [col[1] for col in cursor.fetchall()]

        # Agregar columna cliente_cedula si no existe
        if 'cliente_cedula' not in columnas_ventas:
            print("- Agregando columna cliente_cedula a tabla ventas...")
            cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_cedula TEXT")
            print("  ✓ Columna cliente_cedula agregada")
        else:
            print("  ✓ Columna cliente_cedula ya existe")

        # Agregar columna hora si no existe
        if 'hora' not in columnas_ventas:
            print("- Agregando columna hora a tabla ventas...")
            cursor.execute("ALTER TABLE ventas ADD COLUMN hora TEXT")

            # Intentar extraer la hora de la fecha existente
            cursor.execute("SELECT id, fecha FROM ventas")
            ventas = cursor.fetchall()
            for venta_id, fecha in ventas:
                if fecha and ' ' in fecha:
                    # Si la fecha tiene formato "dd/mm/yyyy hh:mm:ss"
                    partes = fecha.split(' ')
                    if len(partes) >= 2:
                        hora = partes[1]
                        nueva_fecha = partes[0]
                        cursor.execute(
                            "UPDATE ventas SET fecha=?, hora=? WHERE id=?",
                            (nueva_fecha, hora, venta_id)
                        )
            print("  ✓ Columna hora agregada y datos migrados")
        else:
            print("  ✓ Columna hora ya existe")

        # Verificar y agregar columna estado si no existe
        if 'estado' not in columnas_ventas:
            print("- Agregando columna estado a tabla ventas...")
            cursor.execute("ALTER TABLE ventas ADD COLUMN estado TEXT DEFAULT 'completada'")
            cursor.execute("UPDATE ventas SET estado='completada' WHERE estado IS NULL")
            print("  ✓ Columna estado agregada")
        else:
            print("  ✓ Columna estado ya existe")

        # Verificar tabla clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT UNIQUE NOT NULL,
                celular TEXT,
                fecha_registro TEXT
            )
        """)
        print("✓ Tabla clientes verificada")

        # Verificar columnas en productos
        cursor.execute("PRAGMA table_info(productos)")
        columnas_productos = [col[1] for col in cursor.fetchall()]

        if 'stock_minimo' not in columnas_productos:
            print("- Agregando columna stock_minimo a tabla productos...")
            cursor.execute("ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 5")
            print("  ✓ Columna stock_minimo agregada")
        else:
            print("  ✓ Columna stock_minimo ya existe")

        conn.commit()
        print("\n✅ Migración completada exitosamente")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error durante la migración: {e}")
        raise
    finally:
        conn.close()


def crear_directorios():
    """Crea los directorios necesarios para el sistema"""
    directorios = [
        "Facturas",
        "Facturas_Reimpresiones",
        "Reportes",
        "Reportes_Inventario",
        "backups",
        "logs"
    ]

    print("\nCreando directorios necesarios...")
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
        print(f"  ✓ {directorio}/")

    print("✅ Directorios creados")


def verificar_integridad():
    """Verifica la integridad de la base de datos después de la migración"""
    print("\nVerificando integridad de la base de datos...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [t[0] for t in cursor.fetchall()]

        tablas_requeridas = ['productos', 'clientes', 'ventas']
        for tabla in tablas_requeridas:
            if tabla in tablas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"  ✓ Tabla {tabla}: {count} registros")
            else:
                print(f"  ❌ Tabla {tabla} no encontrada")

        print("✅ Verificación completada")

    except Exception as e:
        print(f"❌ Error en verificación: {e}")
    finally:
        conn.close()


def main():
    print("=" * 60)
    print("     MIGRACIÓN DEL SISTEMA POS - 420 SMOKING VIBES")
    print("=" * 60)

    # Confirmar antes de proceder
    respuesta = input("\n¿Desea continuar con la migración? (s/n): ")
    if respuesta.lower() != 's':
        print("Migración cancelada.")
        return

    try:
        # 1. Hacer backup
        hacer_backup()

        # 2. Migrar base de datos
        migrar_base_datos()

        # 3. Crear directorios
        crear_directorios()

        # 4. Verificar integridad
        verificar_integridad()

        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nAhora puede ejecutar el sistema actualizado con main.py")
        print(f"Se creó un backup en: {BACKUP_PATH}")

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR EN LA MIGRACIÓN")
        print("=" * 60)
        print(f"Error: {e}")
        print(f"\nSe puede restaurar el backup desde: {BACKUP_PATH}")

    input("\nPresione Enter para salir...")


if __name__ == "__main__":
    main()