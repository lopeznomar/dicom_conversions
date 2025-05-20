import os
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian, SecondaryCaptureImageStorage
import datetime
from PIL import Image
import numpy as np
import requests

# Información del paciente
paciente = {
    "nombre": "Ramon Santiago",
    "id": "4883071",
    "sexo": "M",
    "edad": "070Y",  # formato DICOM: 3 dígitos + Y/M/D
    "institucion": "CDI Valencia.Carabobo.Venezuela",
    "estudio": "RX Mano Derecha"
}

# Directorios base
input_folder = r"C:\PythonApps\orthanc\imagenes_jpg"
output_base = os.path.join("C:\\PythonApps\\orthanc\\imagenes_dcm", f"{paciente['nombre'].replace(' ', '_')}_{paciente['id']}")

# Crear carpeta si no existe
os.makedirs(output_base, exist_ok=True)

def convertir_y_enviar(jpg_path, nombre_archivo):
    dicom_path = os.path.join(output_base, f"{nombre_archivo}.dcm")

    # Leer imagen y convertir a escala de grises
    image = Image.open(jpg_path).convert("L")
    pixel_array = np.array(image)

    # Metadatos DICOM obligatorios
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    # Dataset principal
    ds = FileDataset(dicom_path, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Fecha y hora del estudio
    dt = datetime.datetime.now()
    ds.StudyDate = dt.strftime('%Y%m%d')
    ds.StudyTime = dt.strftime('%H%M%S')

    # Datos del paciente
    ds.PatientName = paciente["nombre"]
    ds.PatientID = paciente["id"]
    ds.PatientSex = paciente["sexo"]
    ds.PatientAge = paciente["edad"]
    ds.InstitutionName = paciente["institucion"]
    ds.StudyDescription = paciente["estudio"]

    # Identificadores únicos
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

    # Configuración de la imagen
    ds.Modality = "OT"
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.Rows, ds.Columns = pixel_array.shape
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = pixel_array.tobytes()

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Guardar archivo
    ds.save_as(dicom_path)
    print(f"✅ DICOM guardado: {dicom_path}")

    # Enviar a Orthanc
    with open(dicom_path, "rb") as f:
        response = requests.post(
            "http://localhost:8042/instances",
            auth=("orthanc", "orthanc"),
            headers={"Content-Type": "application/dicom"},
            data=f.read()
        )
        if response.status_code == 200:
            print(f"📤 Enviado a Orthanc con éxito: {nombre_archivo}")
        else:
            print(f"❌ Error al enviar a Orthanc: {response.status_code} - {response.text}")

# ▶️ Procesar todas las imágenes del paciente
for archivo in os.listdir(input_folder):
    if archivo.lower().endswith(".jpg"):
        ruta_jpg = os.path.join(input_folder, archivo)
        nombre_sin_extension = os.path.splitext(archivo)[0]
        convertir_y_enviar(ruta_jpg, nombre_sin_extension)
