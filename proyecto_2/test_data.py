import data_loader
import os

def test_loaders():
    base_path = r"c:\Users\sergi\OneDrive\Documentos\ARTICULOS\proyecto 1\data"
    
    print("Test BDPI...")
    bdpi = data_loader.load_bdpi(os.path.join(base_path, "bdpi.xlsx"))
    if bdpi is not None:
        print(f"BDPI cargado: {len(bdpi)} registros.")
        print(bdpi.head(2))
        print("CRS:", bdpi.crs)
    else:
        print("Fallo BDPI")

    print("\nTest Minas...")
    minas = data_loader.load_minas(os.path.join(base_path, "minas.xlsx"))
    if minas is not None:
        print(f"Minas cargado: {len(minas)} registros.")
        print(minas.head(2))
        print("CRS:", minas.crs)
    else:
        print("Fallo Minas")

    print("\nTest Departamentos...")
    dep = data_loader.load_departamentos(os.path.join(base_path, "departamentos"))
    if dep is not None:
        print(f"Departamentos cargado: {len(dep)} registros.")
        print(dep.head(2))
        print("CRS:", dep.crs)
    else:
        print("Fallo Departamentos")

if __name__ == "__main__":
    test_loaders()
